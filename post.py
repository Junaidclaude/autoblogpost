import os, requests, feedparser

SITE = "https://abdulelsayed.wuaze.com"
feed = feedparser.parse("https://news.google.com/rss/search?q=Abdul+El-Sayed&hl=en-US")
items = feed.entries[:5]
sources = "\n".join(f"- {e.title} ({e.link})" for e in items)

prompt = f"""Write a 300-word neutral news summary for an independent blog about
Abdul El-Sayed. Use ONLY the headlines below. Do not invent quotes, numbers or
facts. End with a Sources list.

{sources}"""

r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['GROQ_KEY']}"},
    json={"model": "llama-3.3-70b-versatile",
          "messages": [{"role": "user", "content": prompt}]},
)
text = r.json()["choices"][0]["message"]["content"]

requests.post(
    f"{SITE}/wp-json/wp/v2/posts",
    auth=(os.environ["WP_USER"], os.environ["WP_APP_PASS"]),
    json={"title": "Daily Update: Abdul El-Sayed",
          "content": text.replace("\n", "<br>"),
          "status": "draft"},
)
