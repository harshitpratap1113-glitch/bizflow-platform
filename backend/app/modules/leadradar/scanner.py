import asyncio
import httpx
import logging
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from app.db.database import get_db
from app.modules.leadradar.intent_analyzer import intent_analyzer
from app.modules.leadradar.notifier import ws_manager, telegram_notifier

logger = logging.getLogger("leadradar.scanner")

class LeadRadarScanner:
    """
    Multi-platform Social Stream & Buyer Intent Scraper.
    Fetches real-time feeds from Reddit (Atom RSS) and HackerNews.
    """

    HEADERS = {
        "User-Agent": "bizflow-radar-app:v1.0.0 (by /u/harshit_founder)"
    }

    async def scan_reddit_subreddit(self, client: httpx.AsyncClient, subreddit: str) -> List[Dict[str, Any]]:
        """
        Scans Reddit subreddit using Atom RSS feed with authorized custom User-Agent.
        """
        url = f"https://www.reddit.com/r/{subreddit}/new.rss?limit=25"
        discovered_leads = []
        try:
            res = await client.get(url, headers=self.HEADERS, timeout=12.0, follow_redirects=True)
            if res.status_code == 200:
                root = ET.fromstring(res.text)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('atom:entry', ns)

                for entry in entries:
                    id_elem = entry.find('atom:id', ns)
                    raw_id = id_elem.text if id_elem is not None else ""
                    source_id = f"reddit_{raw_id.split('/')[-1] if raw_id else ''}"

                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text if title_elem is not None else ""

                    link_elem = entry.find('atom:link', ns)
                    source_url = link_elem.attrib.get('href', '') if link_elem is not None else f"https://reddit.com/r/{subreddit}"

                    author_elem = entry.find('atom:author/atom:name', ns)
                    author = author_elem.text.replace("/u/", "") if author_elem is not None else "unknown"

                    content_elem = entry.find('atom:content', ns)
                    raw_html = content_elem.text if content_elem is not None else ""
                    content = ""
                    if raw_html:
                        soup = BeautifulSoup(raw_html, "html.parser")
                        content = soup.get_text(separator=" ", strip=True)

                    # Analyze Intent & Problem
                    analysis = intent_analyzer.analyze_post(title, content)

                    discovered_leads.append({
                        "source": f"Reddit (r/{subreddit})",
                        "source_id": source_id,
                        "source_url": source_url,
                        "title": title,
                        "content": content,
                        "author": author,
                        "intent_score": analysis["intent_score"],
                        "matched_keywords": json.dumps(analysis["matched_keywords"]),
                        "category": analysis["category"],
                        "ai_suggested_reply": analysis["suggested_reply"]
                    })
                logger.info(f"[✓] Fetched {len(discovered_leads)} live posts from r/{subreddit}")
            else:
                logger.warning(f"Failed to fetch r/{subreddit} (HTTP {res.status_code})")
        except Exception as e:
            logger.error(f"Error scanning r/{subreddit}: {e}")

        return discovered_leads

    async def scan_hackernews(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """
        Scans HackerNews 'Ask HN' for founders and developers asking for software solutions.
        """
        url = "https://hacker-news.firebaseio.com/v0/askstories.json"
        discovered_leads = []
        try:
            res = await client.get(url, timeout=10.0)
            if res.status_code == 200:
                story_ids = res.json()[:15]
                for story_id in story_ids:
                    story_res = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=6.0)
                    if story_res.status_code == 200:
                        story = story_res.json()
                        if not story:
                            continue
                        source_id = f"hn_{story.get('id')}"
                        title = story.get("title", "")
                        raw_content = story.get("text", "") or ""
                        content = BeautifulSoup(raw_content, "html.parser").get_text(separator=" ", strip=True) if raw_content else ""
                        author = story.get("by", "unknown")
                        source_url = f"https://news.ycombinator.com/item?id={story_id}"

                        analysis = intent_analyzer.analyze_post(title, content)

                        discovered_leads.append({
                            "source": "HackerNews (Ask HN)",
                            "source_id": source_id,
                            "source_url": source_url,
                            "title": title,
                            "content": content,
                            "author": author,
                            "intent_score": analysis["intent_score"],
                            "matched_keywords": json.dumps(analysis["matched_keywords"]),
                            "category": analysis["category"],
                            "ai_suggested_reply": analysis["suggested_reply"]
                        })
                logger.info(f"[✓] Fetched {len(discovered_leads)} live stories from HackerNews")
        except Exception as e:
            logger.error(f"Error scanning HackerNews: {e}")

        return discovered_leads

    async def run_full_scan(self) -> Dict[str, Any]:
        """
        Executes a complete scan across all configured communities and dispatches alerts.
        """
        db = await get_db()
        try:
            cursor = await db.execute("SELECT target_name, platform FROM monitored_targets WHERE is_active = 1")
            targets = await cursor.fetchall()

            cursor_settings = await db.execute("SELECT key, value FROM settings")
            settings_rows = await cursor_settings.fetchall()
            settings_dict = {row["key"]: row["value"] for row in settings_rows}

            min_score = int(settings_dict.get("min_intent_score", "60"))
            tg_token = settings_dict.get("telegram_bot_token", "")
            tg_chat = settings_dict.get("telegram_chat_id", "")
            tg_enabled = settings_dict.get("telegram_enabled", "0") == "1"

            all_raw_leads: List[Dict[str, Any]] = []

            async with httpx.AsyncClient(timeout=15.0) as client:
                for target in targets:
                    platform = target["platform"]
                    target_name = target["target_name"]
                    if platform == "reddit":
                        leads = await self.scan_reddit_subreddit(client, target_name)
                        all_raw_leads.extend(leads)
                    elif platform == "hackernews":
                        leads = await self.scan_hackernews(client)
                        all_raw_leads.extend(leads)
                    
                    # Polite rate-limiting between target requests
                    await asyncio.sleep(1.2)

            new_leads_saved = 0
            high_intent_alerts = 0

            for lead in all_raw_leads:
                async with db.execute("SELECT id FROM leads WHERE source_id = ?", (lead["source_id"],)) as check_cur:
                    exists = await check_cur.fetchone()
                
                if not exists:
                    cursor_ins = await db.execute("""
                    INSERT INTO leads (
                        source, source_id, source_url, title, content, author, 
                        intent_score, matched_keywords, category, ai_suggested_reply
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        lead["source"], lead["source_id"], lead["source_url"],
                        lead["title"], lead["content"], lead["author"],
                        lead["intent_score"], lead["matched_keywords"],
                        lead["category"], lead["ai_suggested_reply"]
                    ))
                    lead_id = cursor_ins.lastrowid
                    lead["id"] = lead_id
                    new_leads_saved += 1

                    # Real-time WebSocket Broadcast
                    await ws_manager.broadcast({
                        "event": "new_lead",
                        "lead": lead
                    })

                    # Telegram alert if high intent
                    if lead["intent_score"] >= min_score:
                        high_intent_alerts += 1
                        if tg_enabled and tg_token and tg_chat:
                            sent = await telegram_notifier.send_lead_alert(tg_token, tg_chat, lead)
                            if sent:
                                await db.execute("UPDATE leads SET is_notified = 1 WHERE id = ?", (lead_id,))

            await db.commit()
            logger.info(f"[✓] Full Scan Finished. Total: {len(all_raw_leads)}, New: {new_leads_saved}, High Intent: {high_intent_alerts}")
            return {
                "status": "success",
                "total_scanned": len(all_raw_leads),
                "new_leads": new_leads_saved,
                "high_intent_alerts": high_intent_alerts,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            await db.close()

scanner = LeadRadarScanner()
