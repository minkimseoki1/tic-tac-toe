# AI & Design Daily Newsletter

Scrapes reliable AI and design news every morning, generates a bilingual (English + Korean) newsletter using Claude, and emails it to you at 8:00 AM KST.

## Setup

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Configure credentials
Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=sk-ant-...         ← from console.anthropic.com
EMAIL_ADDRESS=minkimseoki1@gmail.com ← your Gmail
EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx ← Gmail App Password (see below)
EMAIL_TO=minkimseoki1@gmail.com      ← who receives the newsletter
```

**Getting a Gmail App Password:**
1. Enable 2-Step Verification on your Google account: myaccount.google.com/security
2. Go to: myaccount.google.com/apppasswords
3. App name: "AI Newsletter" → click Create
4. Copy the 16-character password into `EMAIL_APP_PASSWORD`

### 3. Test manually
```
python main.py
```

### 4. Schedule (Windows Task Scheduler)
Run PowerShell as Administrator, then:
```
.\setup_tasks.ps1
```
This registers a daily task at **8:00 AM KST** that scrapes, generates, and emails the newsletter.

## Sources

**AI News:** MIT Technology Review · The Verge AI · TechCrunch AI · Wired AI · VentureBeat AI

**Design & AI Design:** Eye on Design (AIGA) · Fast Company Design · Design Week · Nielsen Norman Group · UX Collective
