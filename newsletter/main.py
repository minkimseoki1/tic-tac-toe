import os
import sys
import json
import smtplib
import feedparser
import anthropic
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

KST = timezone(timedelta(hours=9))

RSS_FEEDS = {
    "AI News": [
        ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
        ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("Wired AI", "https://www.wired.com/feed/category/artificial-intelligence/latest/rss"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ],
    "Design & AI Design": [
        ("Eye on Design (AIGA)", "https://eyeondesign.aiga.org/feed/"),
        ("Fast Company Design", "https://www.fastcompany.com/section/design/rss"),
        ("Design Week", "https://www.designweek.co.uk/feed/"),
        ("Nielsen Norman Group", "https://www.nngroup.com/feed/rss/"),
        ("UX Collective", "https://uxdesign.cc/feed"),
    ],
}

ARTICLES_PER_FEED = 3


def fetch_articles():
    today = datetime.now(KST).date()
    articles = {"AI News": [], "Design & AI Design": []}

    for category, feeds in RSS_FEEDS.items():
        for source_name, url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:ARTICLES_PER_FEED]:
                    published = entry.get("published_parsed") or entry.get("updated_parsed")
                    articles[category].append({
                        "source": source_name,
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", ""))[:500],
                        "published": str(published) if published else "Unknown",
                    })
            except Exception as e:
                print(f"[WARN] Failed to fetch {source_name}: {e}", file=sys.stderr)

    return articles


def generate_newsletter(articles: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    articles_text = json.dumps(articles, ensure_ascii=False, indent=2)
    today_str = datetime.now(KST).strftime("%Y년 %m월 %d일 / %B %d, %Y")

    prompt = f"""You are a curator writing a bilingual (English + Korean) morning newsletter about AI and design.

Today is {today_str} (KST).

Here are the latest articles scraped from reliable sources:
{articles_text}

Write a polished, engaging newsletter with this exact structure:

---
🌅 AI & Design Morning Brief — {today_str}

## 🤖 AI News Highlights / AI 뉴스 하이라이트

[Pick the 3–5 most important AI stories. For each:
- **Title** (Source) — *link*
- 2–3 sentence English summary
- 한국어 요약 (1–2 sentences in Korean)]

## 🎨 Design & AI Design / 디자인 & AI 디자인

[Pick the 3 most interesting design/AI-design stories. Same format as above.]

## 💡 Today's Insight / 오늘의 인사이트

[A 2–3 sentence reflection in English on the overall theme or trend across today's stories, followed by a Korean translation.]

---
*Curated daily at 8:00 AM KST · Sources: MIT Tech Review, The Verge, TechCrunch, Wired, VentureBeat, Eye on Design, Fast Company, Design Week, NNG, UX Collective*
---

Keep the tone informative but conversational. Use emojis sparingly for section headers only.
Do NOT fabricate articles. Only use what was provided. If a category has no articles, say so briefly."""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def markdown_to_html(text: str) -> str:
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'## (.+)', r'<h2>\1</h2>', text)
    text = re.sub(r'# (.+)', r'<h1>\1</h1>', text)
    text = re.sub(r'^- (.+)', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = text.replace('\n---\n', '<hr>')
    text = re.sub(r'\n{2,}', '</p><p>', text)
    return f'<div style="font-family:sans-serif;max-width:680px;margin:auto;line-height:1.6"><p>{text}</p></div>'


def send_email(newsletter_text: str):
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipient = os.environ.get("EMAIL_TO", sender)
    today_str = datetime.now(KST).strftime("%Y-%m-%d")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"AI & Design Morning Brief — {today_str}"
    msg["From"] = f"AI Newsletter <{sender}>"
    msg["To"] = recipient

    msg.attach(MIMEText(newsletter_text, "plain", "utf-8"))
    msg.attach(MIMEText(markdown_to_html(newsletter_text), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Newsletter sent to {recipient}")


def main():
    print(f"[{datetime.now(KST).isoformat()}] Fetching articles...")
    articles = fetch_articles()

    total = sum(len(v) for v in articles.values())
    print(f"Fetched {total} articles across {len(articles)} categories.")

    print("Generating newsletter with Claude...")
    newsletter = generate_newsletter(articles)

    print("Sending email...")
    send_email(newsletter)

    print("Done.")


if __name__ == "__main__":
    main()
