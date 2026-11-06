import os, sys, requests, feedparser

SITE = "https://abdulelsayed.wuaze.com"
MODEL = "llama-3.3-70b-versatile"

feed = feedparser.parse("https://news.google.com/rss/search?q=Abdul+El-Sayed&hl=en-US")
items = feed.entries[:5]
if not items:
    print("No news items found in feed")
    sys.exit(1)

sources = "\n".join(f"- {e.title} ({e.link})" for e in items)

prompt = f"""Write a 300-word neutral news summary for an independent blog about
Abdul El-Sayed. Use ONLY the headlines below. Do not invent quotes, numbers or
facts. End with a Sources list.

{sources}"""

key = os.environ.get("GROQ_KEY", "").strip()
print("GROQ_KEY present:", bool(key))

r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]},
    timeout=60,
)
print("Groq status:", r.status_code)
data = r.json()
if "choices" not in data:
    print("Groq error:", data)
    sys.exit(1)

text = data["choices"][0]["message"]["content"]

wp = requests.post(
    f"{SITE}/wp-json/wp/v2/posts",
    auth=(os.environ["WP_USER"].strip(), os.environ["WP_APP_PASS"].strip()),
    json={"title": "Daily Update: Abdul El-Sayed",
          "content": text.replace("\n", "<br>"),
          "status": "draft"},
    timeout=60,
)
print("WordPress status:", wp.status_code)
print(wp.text[:500])
