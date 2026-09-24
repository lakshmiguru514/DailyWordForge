"""
WordForge — Daily Business English via WhatsApp
================================================
100% FREE — Google Gemini + CallMeBot + GitHub Actions
"""

import os
import json
import urllib.request
import urllib.parse
import ssl

# ── Configuration ──────────────────────────────────────────────
PHONE = os.environ["CALLMEBOT_PHONE"]
APIKEY = os.environ["CALLMEBOT_APIKEY"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

# ── Step 1: Generate words via Google Gemini (FREE) ────────────
def generate_words():
    prompt = """You are a vocabulary coach for business professionals.
Generate exactly 5 advanced business English words that someone would
encounter in boardrooms, audit reports, financial statements, consulting,
or corporate emails.

Rules:
- Mix parts of speech (nouns, verbs, adjectives, adverbs).
- Avoid very common words like "strategy", "meeting", "revenue".
- Pick words that are useful but not obscure — a professional should know them.
- Each example sentence must feel like it came from a real work situation.

Respond ONLY with a valid JSON array (no markdown, no backticks, no text before or after):
[
  {
    "word": "Prudent",
    "pos": "adjective",
    "def": "Acting with care and thought for the future, especially in business decisions.",
    "example": "The CFO took a prudent approach by building a six-month cash reserve before the expansion."
  }
]

Generate 5 words. Make them different from common vocabulary lists."""

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024}
    }).encode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"

    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    ctx = ssl.create_default_context()

    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    words = json.loads(text)
    if not isinstance(words, list) or len(words) < 5:
        raise ValueError(f"Expected 5 words, got {len(words) if isinstance(words, list) else 'non-list'}")
    return words[:5]


# ── Step 2: Format the WhatsApp message ────────────────────────
def format_message(words):
    from datetime import datetime, timezone, timedelta
    uae_tz = timezone(timedelta(hours=4))
    today = datetime.now(uae_tz).strftime("%A, %d %B %Y")

    lines = [f"📖 *WordForge — {today}*", ""]
    for i, w in enumerate(words, 1):
        lines.append(f"*{i}. {w['word']}* ({w['pos']})")
        lines.append(f"   {w['def']}")
        lines.append(f"   💬 _{w['example']}_")
        lines.append("")
    lines.append("— Keep learning, one word at a time. 🔨")
    return "\n".join(lines)


# ── Step 3: Send via CallMeBot ─────────────────────────────────
def send_whatsapp(message):
    encoded = urllib.parse.quote(message)
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={urllib.parse.quote(PHONE)}"
        f"&text={encoded}"
        f"&apikey={urllib.parse.quote(APIKEY)}"
    )
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, method="GET")

    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        status = resp.status
        body = resp.read().decode()

    if status != 200:
        raise RuntimeError(f"CallMeBot returned {status}: {body}")
    print(f"✅ Message sent successfully (HTTP {status})")
    return body


# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔨 WordForge — generating today's words...")
    words = generate_words()
    for w in words:
        print(f"  • {w['word']} ({w['pos']})")
    message = format_message(words)
    print(f"\n📱 Sending to WhatsApp ({PHONE})...")
    send_whatsapp(message)
    print("🎉 Done!")
