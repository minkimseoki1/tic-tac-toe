import os
import sys
import json
import feedparser
import anthropic
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
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


def send_to_slack(newsletter_text: str):
    token = os.environ["SLACK_BOT_TOKEN"]
    user_id = os.environ["SLACK_USER_ID"]

    client = WebClient(token=token)

    dm = client.conversations_open(users=user_id)
    channel_id = dm["channel"]["id"]

    # Slack has a 3000-char limit per block; split if needed
    chunks = [newsletter_text[i:i+2900] for i in range(0, len(newsletter_text), 2900)]
    for i, chunk in enumerate(chunks):
        client.chat_postMessage(
            channel=channel_id,
            text=chunk,
            mrkdwn=True,
        )

    print(f"Newsletter sent to Slack DM ({user_id})")


def main():
    print(f"[{datetime.now(KST).isoformat()}] Fetching articles...")
    articles = fetch_articles()

    total = sum(len(v) for v in articles.values())
    print(f"Fetched {total} articles across {len(articles)} categories.")

    print("Generating newsletter with Claude...")
    newsletter = generate_newsletter(articles)

    print("Sending to Slack...")
    send_to_slack(newsletter)

    print("Done.")


if __name__ == "__main__":
    main()
