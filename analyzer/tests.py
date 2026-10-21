
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import AnalysisReport


class JobShieldAITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="anotheruser",
            password="AnotherPassword123!",
        )

        self.sample_ad = """
        Urgent Hiring — Software Developer

        Guaranteed selection for all candidates.
        Pay a registration fee upfront to secure your job.
        No interview required.
        """

    def test_risk_score_is_calculated_correctly(self):
        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("home"),
            {"job_description": self.sample_ad},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result"]["score"], 80)
        self.assertEqual(
            response.context["result"]["risk_level"],
            "Very High",
        )

    def test_logged_in_analysis_is_saved_to_user(self):
        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        self.client.post(
            reverse("home"),
            {"job_description": self.sample_ad},
        )

        report = AnalysisReport.objects.latest("id")

        self.assertEqual(report.user, self.user)
        self.assertEqual(report.score, 80)

    def test_empty_advertisement_is_rejected(self):
        response = self.client.post(
            reverse("home"),
            {"job_description": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["result"]["checked"])
        self.assertContains(
            response,
            "Please enter a job advertisement.",
        )
        self.assertEqual(AnalysisReport.objects.count(), 0)

    def test_oversized_advertisement_is_rejected(self):
        oversized_ad = "A" * 20001

        response = self.client.post(
            reverse("home"),
            {"job_description": oversized_ad},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["result"]["checked"])
        self.assertContains(
            response,
            "20,000 characters",
        )
        self.assertEqual(AnalysisReport.objects.count(), 0)

    def test_pdf_download_returns_pdf_file(self):
        report = AnalysisReport.objects.create(
            user=self.user,
            job_description=self.sample_ad,
            score=80,
            risk_level="Very High",
            warnings=[
                "Upfront payment mentioned.",
                "Guaranteed selection promised.",
            ],
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse(
                "download_report_pdf",
                args=[report.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/pdf",
        )
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_user_cannot_download_another_users_report(self):
        report = AnalysisReport.objects.create(
            user=self.other_user,
            job_description="Private job advertisement",
            score=35,
            risk_level="Moderate",
            warnings=["Upfront payment mentioned."],
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse(
                "download_report_pdf",
                args=[report.id],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_history_shows_only_the_logged_in_users_reports(self):
        own_report = AnalysisReport.objects.create(
            user=self.user,
            job_description="My saved job advertisement",
            score=20,
            risk_level="Moderate",
            warnings=["No interview mentioned."],
        )

        AnalysisReport.objects.create(
            user=self.other_user,
            job_description="Another user's private advertisement",
            score=80,
            risk_level="Very High",
            warnings=["Upfront payment mentioned."],
        )

        self.client.login(
            username="testuser",
            password="TestPassword123!",
        )

        response = self.client.get(reverse("history"))

        self.assertEqual(response.status_code, 200)

        report_ids = [
            report.id
            for report in response.context["reports"]
        ]

        self.assertIn(own_report.id, report_ids)
        self.assertEqual(report_ids, [own_report.id])
