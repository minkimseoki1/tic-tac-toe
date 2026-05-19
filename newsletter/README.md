# AI & Design Daily Newsletter

Scrapes reliable AI and design news every morning, generates a bilingual (English + Korean) newsletter using Claude, and sends it to your Slack DM at 8:00 AM KST.

## Setup

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Configure credentials
Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=sk-ant-...   ← from console.anthropic.com
SLACK_BOT_TOKEN=xoxb-...       ← from api.slack.com/apps
SLACK_USER_ID=U0XXXXXXXXX      ← your Slack member ID
```

**Getting your Slack bot token:**
1. Go to api.slack.com/apps → Create New App → From scratch
2. Name it "AI Newsletter Bot", select your workspace
3. OAuth & Permissions → Bot Token Scopes → add: `chat:write`, `im:write`
4. Install to Workspace → copy the Bot User OAuth Token

**Getting your Slack member ID:**
- In Slack: click your profile picture → Profile → ··· (three dots) → Copy member ID

**Invite the bot to DM yourself:**
- In Slack, search for your bot name and send it a message (opens the DM channel)

### 3. Test manually
```
python main.py
```

### 4. Schedule (Windows Task Scheduler)
Run PowerShell as Administrator, then:
```
.\setup_tasks.ps1
```
This registers a daily task at **8:00 AM KST** that scrapes, generates, and sends the newsletter.

## Sources

**AI News:** MIT Technology Review · The Verge AI · TechCrunch AI · Wired AI · VentureBeat AI

**Design & AI Design:** Eye on Design (AIGA) · Fast Company Design · Design Week · Nielsen Norman Group · UX Collective
