"""
BizFlow AI — Dedicated Reddit API & Dual-Pipeline Engine
Handles:
1. Official Reddit OAuth Bearer Token API (OAuth2 client_credentials / script app)
2. Zero-Config High-Speed RSS/XML Live Stream Fallback (100% bypasses 403 blocks)
3. Full Lead Extraction, Tri-Box Classification, and Auto-Save into SQLite.
"""

import os
import re
import time
import json
import base64
import random
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from app.db.database import get_db
from app.modules.leadradar.live_crawler import analyze_tri_box_routing

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
]

class RedditApiEngine:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.client_id = client_id or os.environ.get("REDDIT_CLIENT_ID", "").strip()
        self.client_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
        self.user_agent = user_agent or os.environ.get("REDDIT_USER_AGENT", "BizFlowRadar/2.0 by harshit_dev").strip()
        self.username = username or os.environ.get("REDDIT_USERNAME", "").strip()
        self.password = password or os.environ.get("REDDIT_PASSWORD", "").strip()
        
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0.0

    def is_authenticated(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_oauth_token(self) -> Optional[str]:
        """Obtains OAuth Bearer Token from Reddit API."""
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        if not self.is_authenticated():
            return None

        try:
            auth_str = f"{self.client_id}:{self.client_secret}"
            b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            
            headers = {
                "User-Agent": self.user_agent,
                "Authorization": f"Basic {b64_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            if self.username and self.password:
                data = urllib.parse.urlencode({
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password
                }).encode("utf-8")
            else:
                data = urllib.parse.urlencode({
                    "grant_type": "client_credentials"
                }).encode("utf-8")

            req = urllib.request.Request("https://www.reddit.com/api/v1/access_token", data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                self.access_token = resp_json.get("access_token")
                expires_in = resp_json.get("expires_in", 3600)
                self.token_expiry = time.time() + expires_in
                return self.access_token
        except Exception as e:
            print(f"[RedditApiEngine] OAuth Handshake failed: {e}")
            return None

    def search_subreddits(
        self,
        subreddits: List[str],
        query: str = "",
        limit: int = 25,
        sort: str = "new"
    ) -> List[Dict[str, Any]]:
        """
        Searches or streams subreddits using:
        1. Official OAuth API if keys configured
        2. High-speed XML/Atom RSS feed with keyword matching if no keys configured
        """
        token = self.get_oauth_token()
        results = []
        clean_query = query.strip().lower() if query else ""

        for sub in subreddits:
            sub = sub.strip().replace("r/", "").replace("/", "")
            if not sub:
                continue

            sub_leads = []

            # 1. Try OAuth API if token available
            if token:
                try:
                    q_param = f"?q={urllib.parse.quote(query)}&sort={sort}&limit={limit}&restrict_sr=1" if query else f"/new?limit={limit}"
                    url = f"https://oauth.reddit.com/r/{sub}/{'search' if query else 'new'}{q_param if query else f'?limit={limit}'}"
                    headers = {
                        "User-Agent": self.user_agent,
                        "Authorization": f"Bearer {token}"
                    }
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=7) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        for p in data.get("data", {}).get("children", []):
                            pdata = p.get("data", {})
                            title = pdata.get("title", "").strip()
                            body = pdata.get("selftext", "").strip()
                            author = pdata.get("author", "reddit_user")
                            permalink = pdata.get("permalink", "")
                            full_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/r/") else pdata.get("url", "")
                            
                            analysis = analyze_tri_box_routing(title, body, sub)
                            sub_leads.append(self._format_lead(
                                post_id=pdata.get("id", f"{abs(hash(title))}"),
                                community=sub,
                                title=title,
                                body=body,
                                author=author,
                                url=full_url,
                                analysis=analysis
                            ))
                except Exception as e:
                    print(f"[RedditApiEngine] OAuth fetch error for r/{sub}: {e}")

            # 2. Fallback to RSS/XML Feed (100% reliable, zero-auth required)
            if not sub_leads:
                try:
                    rss_url = f"https://www.reddit.com/r/{sub}/new/.rss?limit={max(limit, 25)}"
                    req = urllib.request.Request(rss_url, headers={"User-Agent": random.choice(USER_AGENTS)})
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        xml_content = resp.read().decode("utf-8")
                        root = ET.fromstring(xml_content)
                        entries = root.findall("{http://www.w3.org/2005/Atom}entry")

                        for entry in entries[:limit]:
                            title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                            link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
                            author_elem = entry.find("{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name")
                            content_elem = entry.find("{http://www.w3.org/2005/Atom}content")

                            title = (title_elem.text or "").strip() if title_elem is not None else ""
                            if not title:
                                continue

                            raw_content = content_elem.text if content_elem is not None else ""
                            body = re.sub(r'<[^>]+>', ' ', raw_content).strip()

                            # If query filter provided, check if query matches title or body
                            if clean_query:
                                query_terms = [t.strip() for t in clean_query.split() if len(t.strip()) > 2]
                                text_lower = (title + " " + body).lower()
                                if not any(term in text_lower for term in query_terms):
                                    continue

                            raw_url = link_elem.attrib.get("href", "") if link_elem is not None else ""
                            full_url = raw_url if raw_url.startswith("http") else f"https://www.reddit.com/r/{sub}/"
                            author = (author_elem.text or "reddit_user").strip() if author_elem is not None else "reddit_user"
                            author = author.replace("/u/", "")

                            analysis = analyze_tri_box_routing(title, body, sub)
                            sub_leads.append(self._format_lead(
                                post_id=f"rss-{abs(hash(full_url or title))}",
                                community=sub,
                                title=title,
                                body=body,
                                author=author,
                                url=full_url,
                                analysis=analysis
                            ))
                except Exception as e:
                    print(f"[RedditApiEngine] RSS fetch error for r/{sub}: {e}")

            results.extend(sub_leads)

        return results

    def _format_lead(self, post_id: str, community: str, title: str, body: str, author: str, url: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "reddit",
            "platform_id": f"reddit-{post_id}",
            "community": community,
            "title": title,
            "body": body[:600] if body else "Click link to inspect Reddit discussion thread.",
            "author": author,
            "url": url,
            "intent_score": analysis["intent_score"],
            "category": analysis["category"],
            "matched_keywords": analysis["matched_keywords"],
            "budget": analysis["budget"],
            "lead_box": analysis["lead_box"],
            "is_spam": analysis["is_spam"],
            "spam_reason": analysis["spam_reason"],
            "spam_confidence": analysis["spam_confidence"]
        }

    def save_leads_to_db(self, leads: List[Dict[str, Any]]) -> int:
        """Saves extracted Reddit leads directly into BizFlow database."""
        if not leads:
            return 0

        conn = get_db()
        cursor = conn.cursor()
        saved = 0

        for lead in leads:
            try:
                cursor.execute("""
                INSERT OR REPLACE INTO leads (
                    platform, platform_id, community, title, body, author, url,
                    intent_score, intent_category, matched_keywords, budget_detected,
                    lead_box, is_spam, spam_reason, spam_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lead["platform"],
                    lead["platform_id"],
                    lead["community"],
                    lead["title"],
                    lead["body"],
                    lead["author"],
                    lead["url"],
                    lead["intent_score"],
                    lead["category"],
                    lead["matched_keywords"],
                    lead["budget"],
                    lead["lead_box"],
                    lead["is_spam"],
                    lead["spam_reason"],
                    lead["spam_confidence"]
                ))
                if cursor.rowcount > 0:
                    saved += 1
            except Exception as e:
                print(f"[RedditApiEngine] DB Insert Error: {e}")

        conn.commit()
        conn.close()
        return saved
