
# JobShield AI 🛡️

A Django-based web application that analyzes job advertisements and highlights potential recruitment scam warning signs.

## Overview

JobShield AI helps job seekers identify suspicious patterns in job advertisements using a rule-based keyword analysis system. It provides a risk score, explains detected warning indicators, and recommends practical verification steps.

**Important:** JobShield AI is a preliminary screening tool. It does not prove whether a job is fraudulent or legitimate.

## Features

- **Job Advertisement Analysis:** Analyze pasted job descriptions.
- **Risk Scoring:** Calculate a score from 0 to 100 based on detected warning indicators.
- **Warning Explanations:** Show detected indicators and their severity.
- **Recommended Actions:** Provide practical steps for each detected warning.
- **User Accounts:** Register and log in to the application.
- **Analysis History:** View saved reports associated with your account.
- **PDF Reports:** Download analysis reports as PDF files.
- **Input Validation:** Reject empty advertisements and inputs exceeding 20,000 characters.
- **Privacy Controls:** Restrict saved report history and downloads to the owning account.

## Warning Indicators

The current rule-based analyzer checks for patterns such as:

- Upfront or registration fees
- Guaranteed job selection
- Recruitment without an interview
- Requests for OTPs
- Requests for banking passwords or UPI PINs

The score is based on predefined rules and is not a probability of fraud.

## Technology Stack

- **Backend:** Python, Django
- **Database:** SQLite
- **Frontend:** HTML, CSS, Django Templates
- **PDF Generation:** ReportLab
- **Testing:** Django automated tests
- **Version Control:** Git and GitHub

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Amaan-Asif/JobShield-AI.git
cd JobShield-AI
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the packages used by the project:

```powershell
pip install django djangorestframework reportlab python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root containing:

```text
DJANGO_SECRET_KEY=replace-with-a-new-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Generate a fresh secret key for your environment. Do not publish your actual `.env` file or secret key.

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Start the development server

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Run Tests

Run the automated test suite with:

```powershell
python manage.py test analyzer
```

The current test suite covers risk scoring, report ownership, history privacy, PDF downloads, and input validation.

## Security Notes

- Keep `.env`, your secret key, and your local database out of public repositories.
- Do not share OTPs, passwords, or UPI PINs with recruiters.
- Verify employers and vacancies through independently obtained official contact details.
- Before production deployment, configure secure production settings, HTTPS, and an appropriate production database.

## Limitations

- Analysis uses predefined keywords and rules rather than a trained AI model.
- New or cleverly worded scam patterns may not be detected.
- Legitimate advertisements may contain flagged phrases.
- A low score does not guarantee that an opportunity is safe.

## Future Improvements

- Add more configurable warning rules.
- Improve the analysis interface and reporting.
- Add deployment and production configuration.
- Expand automated tests.
- Evaluate additional detection approaches.

## Disclaimer

JobShield AI is an educational project intended to help users review job advertisements. Its output is informational and should not be treated as definitive proof of fraud or legitimacy.

---

**Built with Python and Django.**
