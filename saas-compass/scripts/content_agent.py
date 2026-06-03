#!/usr/bin/env python3
"""
SaaSCompass Automated Content Agent
Uses Ollama (local) to generate affiliate blog posts automatically.
Run: python scripts/content_agent.py
"""

import os, json, re, datetime, subprocess, time, random
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
OLLAMA_MODEL = "llama3.2:3b"          # swap to qwen3-coder:latest if preferred
POSTS_DIR    = Path("_posts")
POSTS_DIR.mkdir(exist_ok=True)

# ── TOPIC QUEUE ───────────────────────────────────────────────────────────────
# Add more topics here freely. The agent picks from this list.
TOPICS = [
    # VPN topics
    {"title": "NordVPN vs ExpressVPN: Which Is Better in 2024?",    "category": "vpn",              "affiliate": "NordVPN",     "kw": "nordvpn vs expressvpn"},
    {"title": "Best VPN for Streaming Netflix in 2024",             "category": "vpn",              "affiliate": "NordVPN",     "kw": "best vpn netflix"},
    {"title": "Is a Free VPN Safe? (The Honest Truth)",             "category": "vpn",              "affiliate": "NordVPN",     "kw": "free vpn safe"},
    # Hosting topics
    {"title": "Hostinger vs Bluehost: Which Should You Choose?",    "category": "hosting",          "affiliate": "Hostinger",   "kw": "hostinger vs bluehost"},
    {"title": "Best WordPress Hosting for Beginners 2024",          "category": "hosting",          "affiliate": "Hostinger",   "kw": "best wordpress hosting beginners"},
    {"title": "Cheapest Web Hosting That Actually Works",           "category": "hosting",          "affiliate": "Hostinger",   "kw": "cheapest web hosting"},
    # AI tools
    {"title": "Jasper AI Review 2024: Worth the Price?",            "category": "ai-tools",         "affiliate": "Jasper AI",   "kw": "jasper ai review"},
    {"title": "Best AI Tools for Content Creators in 2024",         "category": "ai-tools",         "affiliate": "Jasper AI",   "kw": "best ai tools content creators"},
    {"title": "ChatGPT vs Jasper: Which Writes Better Content?",    "category": "ai-tools",         "affiliate": "Jasper AI",   "kw": "chatgpt vs jasper"},
    # Email marketing
    {"title": "ConvertKit Review: Is It the Best Email Tool?",      "category": "email-marketing",  "affiliate": "ConvertKit",  "kw": "convertkit review"},
    {"title": "Mailchimp vs ConvertKit: Which Is Better?",          "category": "email-marketing",  "affiliate": "ConvertKit",  "kw": "mailchimp vs convertkit"},
    # SEO
    {"title": "SEMrush Review 2024: Is It Worth $129/Month?",       "category": "seo",              "affiliate": "SEMrush",     "kw": "semrush review"},
    {"title": "Best SEO Tools for Bloggers (Free & Paid)",          "category": "seo",              "affiliate": "SEMrush",     "kw": "best seo tools bloggers"},
    # Productivity
    {"title": "Notion Review 2024: The All-in-One Workspace",       "category": "productivity",     "affiliate": "Notion",      "kw": "notion review"},
    {"title": "Best Project Management Tools for Freelancers",      "category": "productivity",     "affiliate": "Notion",      "kw": "project management tools freelancers"},
]

AFFILIATE_LINKS = {
    "NordVPN":    "https://nordvpn.com/?aff=YOUR_AFFILIATE_ID",
    "Hostinger":  "https://hostinger.com/?aff=YOUR_AFFILIATE_ID",
    "Jasper AI":  "https://jasper.ai/?aff=YOUR_AFFILIATE_ID",
    "ConvertKit": "https://convertkit.com/?aff=YOUR_AFFILIATE_ID",
    "SEMrush":    "https://semrush.com/?aff=YOUR_AFFILIATE_ID",
    "Notion":     "https://notion.so/?aff=YOUR_AFFILIATE_ID",
}

# ── HELPERS ───────────────────────────────────────────────────────────────────

def slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:60]

def post_exists(title: str) -> bool:
    s = slug(title)
    return any(s in f.name for f in POSTS_DIR.glob("*.md"))

def ollama(prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL],
        input=prompt, capture_output=True, text=True, timeout=120
    )
    return result.stdout.strip()

def generate_post(topic: dict) -> str:
    aff_link = AFFILIATE_LINKS.get(topic["affiliate"], "#")
    aff_name = topic["affiliate"]
    
    prompt = f"""Write a detailed, honest blog post for an affiliate marketing website.

Title: {topic["title"]}
Target keyword: {topic["kw"]}
Primary affiliate product: {aff_name}

Requirements:
- 800-1200 words
- Markdown format
- Include an H2 for each major section
- Include a comparison table if relevant (use markdown table syntax)
- Write honestly — mention real pros AND cons
- Include one natural mention of {aff_name} with this exact HTML affiliate box at the end:

<div class="affiliate-box">
  <div class="affiliate-box-text">
    <h4>Try {aff_name} Today</h4>
    <p>Click below to get the best current deal.</p>
  </div>
  <a href="{aff_link}" class="btn btn-primary" rel="nofollow sponsored" target="_blank">Get {aff_name} →</a>
</div>

Write the body content only (no frontmatter). Start directly with the intro paragraph."""

    return ollama(prompt)

def save_post(topic: dict, body: str):
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = POSTS_DIR / f"{today}-{slug(topic['title'])}.md"
    reading_time = max(4, len(body.split()) // 200)
    
    frontmatter = f"""---
layout: post
title: "{topic['title']}"
excerpt: "An in-depth look at {topic['title'].lower()}. We break down features, pricing, and whether it's worth it."
category: {topic['category']}
tags: [{topic['category']}]
reading_time: {reading_time}
date: {today}
---

"""
    filename.write_text(frontmatter + body)
    print(f"  ✓ Saved: {filename.name}")
    return filename

# ── MAIN ──────────────────────────────────────────────────────────────────────

def run(count: int = 3):
    print(f"\n🧭 SaaSCompass Content Agent")
    print(f"   Model: {OLLAMA_MODEL}")
    print(f"   Generating {count} post(s)...\n")

    pending = [t for t in TOPICS if not post_exists(t["title"])]
    if not pending:
        print("✅ All topics already generated!")
        return

    batch = random.sample(pending, min(count, len(pending)))

    for i, topic in enumerate(batch, 1):
        print(f"[{i}/{len(batch)}] Generating: {topic['title']}")
        try:
            body = generate_post(topic)
            if len(body) < 200:
                print(f"  ⚠ Output too short, skipping.")
                continue
            save_post(topic, body)
            time.sleep(2)  # be nice to local model
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\n✅ Done! Run 'bundle exec jekyll build' to rebuild the site.")
    print(f"   Then push to GitHub to publish.\n")

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run(count)
