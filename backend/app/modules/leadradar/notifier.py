import httpx
import json
import logging
from typing import Dict, Any, List
from fastapi import WebSocket

logger = logging.getLogger("leadradar.notifier")

class ConnectionManager:
    """Manages active WebSocket connections for live lead streaming."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket client: {e}")
                self.disconnect(connection)

ws_manager = ConnectionManager()

class TelegramNotifier:
    """Dispatches instant Telegram notifications for high-intent buyer leads."""

    @staticmethod
    async def send_lead_alert(
        bot_token: str, 
        chat_id: str, 
        lead: Dict[str, Any]
    ) -> bool:
        if not bot_token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID is missing. Skipping notification.")
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # Badge emoji based on intent score
        score = lead.get("intent_score", 0)
        badge = "🔥 CRITICAL INTENT" if score >= 85 else "⚡ HIGH INTENT" if score >= 70 else "💡 MODERATE"

        text = (
            f"🚨 <b>[LeadRadar Alert] {badge} ({score}%)</b>\n\n"
            f"📍 <b>Source:</b> {lead.get('source', 'Unknown')}\n"
            f"👤 <b>Author:</b> @{lead.get('author', 'anonymous')}\n"
            f"🏷️ <b>Category:</b> {lead.get('category', 'General')}\n\n"
            f"📌 <b>Title:</b> {lead.get('title', '')}\n"
            f"💬 <b>Snippet:</b> <i>{lead.get('content', '')[:200]}...</i>\n\n"
            f"✍️ <b>1-Click AI Reply:</b>\n"
            f"<code>{lead.get('ai_suggested_reply', '')}</code>\n\n"
            f"🔗 <a href=\"{lead.get('source_url', '#')}\">👉 Open Original Post</a>"
        )

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    logger.info(f"[✓] Telegram alert successfully sent for lead {lead.get('source_id')}")
                    return True
                else:
                    logger.error(f"[!] Telegram API error {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"[!] Failed to send Telegram alert: {e}")
            return False

telegram_notifier = TelegramNotifier()
