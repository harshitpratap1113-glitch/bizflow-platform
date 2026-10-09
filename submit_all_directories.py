#!/usr/bin/env python3
"""
BizFlow AI - Master Directory Submission & SEO Backlink Supercharger Engine
Automatically formats and compiles submission packages for top 15+ AI/SaaS directories & Product Hunt.
"""

import os
import sys
import json
import urllib.request

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PRODUCT_DATA = {
    "name": "BizFlow AI LeadRadar",
    "tagline": "Real-time AI buyer intent radar across 100+ communities & Tri-Box system",
    "short_description": "Worldwide multi-industry buyer intent radar across 100+ communities with real-time live ticker, 10 industry fields, and Tri-Box routing for verified agency client acquisition.",
    "website_url": "https://bizflow-platform.vercel.app/",
    "logo_url": "https://bizflow-platform.vercel.app/android-chrome-512x512.png",
    "og_image_url": "https://bizflow-platform.vercel.app/og-image.png",
    "pricing_model": "Free / Freemium",
    "category": "Lead Generation, AI Sales Assistant, B2B SaaS, Agency Growth",
    "tags": ["AI", "Lead Generation", "Reddit Scraper", "Client Acquisition", "Cold Outreach", "B2B SaaS"],
    "maker": {
        "name": "Harshit Pratap",
        "email": "harshitpratap1113@gmail.com",
        "role": "Founder & Lead Architect"
    }
}

DIRECTORIES = [
    {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com/posts/new",
        "authority": "DA 91",
        "submission_type": "Live Launch / Upvote Engine",
        "status": "Ready (API Verified)"
    },
    {
        "name": "Toolify.ai",
        "url": "https://www.toolify.ai/submit",
        "authority": "DA 68",
        "submission_type": "Direct AI Directory Submission",
        "status": "Ready"
    },
    {
        "name": "Futurepedia",
        "url": "https://www.futurepedia.io/submit-tool",
        "authority": "DA 72",
        "submission_type": "AI Tool Directory",
        "status": "Ready"
    },
    {
        "name": "There's An AI For That (TAAFT)",
        "url": "https://theresanaiforthat.com/submit/",
        "authority": "DA 76",
        "submission_type": "World's Largest AI Aggregator",
        "status": "Ready"
    },
    {
        "name": "Uneed.best",
        "url": "https://www.uneed.best/submit-a-tool",
        "authority": "DA 55",
        "submission_type": "Curated SaaS Discovery",
        "status": "Ready"
    },
    {
        "name": "MicroLaunch",
        "url": "https://microlaunch.net/submit",
        "authority": "DA 48",
        "submission_type": "Indie Maker Community Launch",
        "status": "Ready"
    },
    {
        "name": "SaaSHub",
        "url": "https://www.saashub.com/submit",
        "authority": "DA 62",
        "submission_type": "Software Alternatives & Directory",
        "status": "Ready"
    },
    {
        "name": "BetaList",
        "url": "https://betalist.com/submit",
        "authority": "DA 65",
        "submission_type": "Startup Beta Launch Community",
        "status": "Ready"
    },
    {
        "name": "StartupBase",
        "url": "https://startupbase.io/submit",
        "authority": "DA 45",
        "submission_type": "Product Discovery Platform",
        "status": "Ready"
    },
    {
        "name": "PitchWall",
        "url": "https://pitchwall.co/submit",
        "authority": "DA 42",
        "submission_type": "Interactive Pitch Community",
        "status": "Ready"
    },
    {
        "name": "Insanely Cool Tools",
        "url": "https://insanelycooltools.com/submit",
        "authority": "DA 40",
        "submission_type": "Curated Weekly Newsletter Directory",
        "status": "Ready"
    }
]

def generate_markdown_pack():
    md = f"""# 🚀 BizFlow AI LeadRadar — Master Directory Submission & Backlink Pack

> **Platform:** [BizFlow AI LeadRadar]({PRODUCT_DATA['website_url']})  
> **Maker:** {PRODUCT_DATA['maker']['name']} ({PRODUCT_DATA['maker']['email']})  
> **Category:** {PRODUCT_DATA['category']}  
> **Pricing:** {PRODUCT_DATA['pricing_model']}

---

## ⚡ Master Submission Metadata

* **Product Name:** `{PRODUCT_DATA['name']}`
* **Tagline:** `{PRODUCT_DATA['tagline']}`
* **Live Website URL:** `{PRODUCT_DATA['website_url']}`
* **Logo URL (512x512):** `{PRODUCT_DATA['logo_url']}`
* **OpenGraph Banner (1200x630):** `{PRODUCT_DATA['og_image_url']}`
* **Keywords / Tags:** `{", ".join(PRODUCT_DATA['tags'])}`

---

## 📝 500-Character Pitch Copy

> {PRODUCT_DATA['short_description']}

---

## 💬 Maker First Comment (Product Hunt & Community Launches)

```text
Hey everyone! 👋 I'm Harshit, maker of BizFlow AI LeadRadar.

Like many freelance developers and agency owners, I was tired of spending 4+ hours every morning scrolling through subreddits (r/forhire, r/freelance, r/reactjs, r/SaaS) trying to find clients before someone else did.

So I built BizFlow AI — a real-time buyer intent radar that continuously ingests 100+ communities, scores buyer intent with semantic AI, routes spam into an isolated Level-10 vault, and lets you generate tailored 1-click pitches in seconds.

Would love to hear your thoughts and feedback! What community should we track next? 🚀
```

---

## 🌐 1-Click Submission Links (Top 11 High-Authority Backlink Directories)

| Directory Name | Authority | Submission Link | Submission Type |
|---|---|---|---|
"""
    for d in DIRECTORIES:
        md += f"| **{d['name']}** | `{d['authority']}` | [{d['name']} Submission Form]({d['url']}) | {d['submission_type']} |\n"

    md += """
---

## ⚡ Embeddable HTML Backlink Badge

Webmasters & agency blogs can embed this snippet for mutual dofollow backlinks:

```html
<a href="https://bizflow-platform.vercel.app/" target="_blank" title="Powered by BizFlow AI LeadRadar">
  <img src="https://bizflow-platform.vercel.app/badge.svg" alt="Powered by BizFlow AI LeadRadar" width="220" height="38" />
</a>
```
"""
    return md

if __name__ == "__main__":
    print("[*] Generating Master Directory Submission & Backlink Pack...")
    pack_md = generate_markdown_pack()
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DIRECTORIES_SUBMISSION_PACK.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(pack_md)
        
    print(f"[SUCCESS] Pack saved to: {out_path}")
    print("\n[+] Direct Submissions Available Across 11 High-Authority Directories:")
    for idx, d in enumerate(DIRECTORIES, 1):
        print(f"  {idx}. {d['name']} ({d['authority']}) -> {d['url']}")
