
from io import BytesIO
from html import escape

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .models import AnalysisReport


MAX_AD_LENGTH = 20000


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


def home(request):
    result = None

    warning_rules = [
        {
            "keywords": [
                "registration fee",
                "application fee",
                "pay upfront",
                "upfront payment",
            ],
            "warning": (
                "The advertisement mentions an upfront or application payment."
            ),
            "points": 35,
            "severity": "High",
            "action": (
                "Do not pay recruitment fees before independently verifying "
                "the employer and opportunity."
            ),
        },
        {
            "keywords": [
                "guaranteed selection",
                "100% job guarantee",
                "guaranteed job",
            ],
            "warning": (
                "The advertisement promises guaranteed selection or employment."
            ),
            "points": 25,
            "severity": "High",
            "action": (
                "Verify the offer through the company's official careers page "
                "or an independently verified contact."
            ),
        },
        {
            "keywords": [
                "no interview required",
                "without interview",
            ],
            "warning": (
                "The advertisement suggests hiring without an interview."
            ),
            "points": 20,
            "severity": "Moderate",
            "action": (
                "Confirm the recruitment process directly with the company "
                "using independently verified contact details."
            ),
        },
        {
            "keywords": [
                "send otp",
                "share your otp",
                "one-time password",
            ],
            "warning": (
                "The advertisement asks for an OTP. Never share an OTP "
                "with a recruiter."
            ),
            "points": 50,
            "severity": "High",
            "action": (
                "Never share an OTP with a recruiter. Stop the interaction "
                "and verify the request independently."
            ),
        },
        {
            "keywords": [
                "bank password",
                "upi pin",
                "share your pin",
            ],
            "warning": (
                "The advertisement mentions sensitive banking credentials. "
                "Never share passwords or UPI PINs."
            ),
            "points": 50,
            "severity": "High",
            "action": (
                "Never share banking passwords or UPI PINs. Stop the interaction "
                "and contact your bank if you have already shared them."
            ),
        },
    ]

    if request.method == "POST":
        job_description = request.POST.get(
            "job_description", ""
        ).strip()

        if not job_description:
            result = {
                "status": "Please enter a job advertisement.",
                "warnings": [],
                "warning_details": [],
                "checked": False,
            }

        elif len(job_description) > MAX_AD_LENGTH:
            result = {
                "status": (
                    "Your advertisement is too long. Please limit it to "
                    "20,000 characters and try again."
                ),
                "warnings": [],
                "warning_details": [],
                "checked": False,
            }

        else:
            warnings = []
            warning_details = []
            score = 0
            text = job_description.lower()

            for rule in warning_rules:
                if any(
                    keyword in text
                    for keyword in rule["keywords"]
                ):
                    warnings.append(rule["warning"])
                    warning_details.append({
                        "warning": rule["warning"],
                        "severity": rule["severity"],
                        "action": rule["action"],
                    })
                    score += rule["points"]

            score = min(score, 100)

            if score >= 70:
                risk_level = "Very High"
                recommendation = (
                    "Pause the application process. Multiple serious warning "
                    "signs were detected. Verify the employer independently "
                    "before taking any further action."
                )
            elif score >= 40:
                risk_level = "High"
                recommendation = (
                    "Proceed with caution. Verify the company, recruiter, "
                    "and job advertisement before sharing information."
                )
            elif score >= 20:
                risk_level = "Moderate"
                recommendation = (
                    "Some warning signs were detected. Check the employer "
                    "and recruitment process before proceeding."
                )
            else:
                risk_level = "Low"
                recommendation = (
                    "No listed warning signs were detected. This does not "
                    "guarantee the opportunity is legitimate, so verify it "
                    "independently."
                )

            report = AnalysisReport.objects.create(
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                job_description=job_description,
                score=score,
                risk_level=risk_level,
                warnings=warnings,
            )

            result = {
                "status": (
                    "Potential warning signs found"
                    if warnings
                    else "No listed warning signs detected"
                ),
                "warnings": warnings,
                "warning_details": warning_details,
                "checked": True,
                "score": score,
                "risk_level": risk_level,
                "recommendation": recommendation,
            }

    return render(
        request,
        "analyzer/home.html",
        {"result": result},
    )


@login_required
def history(request):
    reports = AnalysisReport.objects.filter(
        user=request.user
    ).order_by("-created_at")[:50]

    return render(
        request,
        "analyzer/history.html",
        {"reports": reports},
    )


@login_required
def delete_report(request, report_id):
    if request.method != "POST":
        return redirect("history")

    report = AnalysisReport.objects.filter(
        id=report_id,
        user=request.user,
    ).first()

    if report is not None:
        report.delete()

    return redirect("history")


@login_required
def download_report_pdf(request, report_id):
    report = get_object_or_404(
        AnalysisReport,
        id=report_id,
        user=request.user,
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="JobShield AI Analysis Report",
        author="JobShield AI",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#14213D"),
        alignment=1,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#087F6B"),
        spaceBefore=14,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="ReportBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=7,
        wordWrap="CJK",
    ))

    story = [
        Paragraph("JobShield AI", styles["ReportTitle"]),
        Paragraph(
            "Job Advertisement Risk Analysis Report",
            styles["Normal"],
        ),
        Spacer(1, 16),
        Paragraph("Analysis Summary", styles["SectionHeading"]),
    ]

    summary_data = [
        ["Risk Score", f"{report.score} / 100"],
        ["Risk Level", report.risk_level],
        [
            "Report Date",
            report.created_at.strftime("%d %B %Y, %I:%M %p"),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[45 * mm, 110 * mm],
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F7")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#172033")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DDE8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(summary_table)

    story.append(Paragraph(
        "Original Job Advertisement",
        styles["SectionHeading"],
    ))

    safe_description = escape(report.job_description)
    safe_description = safe_description.replace("\n", "<br/>")

    story.append(Paragraph(
        safe_description,
        styles["ReportBody"],
    ))

    story.append(Paragraph(
        "Detected Warning Indicators",
        styles["SectionHeading"],
    ))

    if report.warnings:
        for index, warning in enumerate(report.warnings, start=1):
            story.append(Paragraph(
                f"{index}. {escape(str(warning))}",
                styles["ReportBody"],
            ))
    else:
        story.append(Paragraph(
            "No warning indicators from the current keyword checklist "
            "were detected.",
            styles["ReportBody"],
        ))

    story.append(Paragraph(
        "Employer Verification Checklist",
        styles["SectionHeading"],
    ))

    checklist = [
        "Verify the company website and contact details independently.",
        "Check whether the vacancy appears on the official careers page.",
        "Verify the recruiter's identity through a trusted contact channel.",
        "Never pay money to secure a job.",
        "Never share OTPs, passwords, or UPI PINs.",
    ]

    for item in checklist:
        story.append(Paragraph(
            f"- {escape(item)}",
            styles["ReportBody"],
        ))

    story.append(Paragraph(
        "Important Disclaimer",
        styles["SectionHeading"],
    ))

    story.append(Paragraph(
        "This report is based on a preliminary keyword-based checklist. "
        "The score is not a probability of fraud and does not prove that "
        "a job is fraudulent or legitimate. Always verify the employer "
        "and opportunity independently.",
        styles["ReportBody"],
    ))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Generated by JobShield AI",
        styles["Italic"],
    ))

    document.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(
        pdf,
        content_type="application/pdf",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="JobShield-Report-{report.id}.pdf"'
    )

    return response
