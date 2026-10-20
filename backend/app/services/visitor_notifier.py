"""
LeedsFlow AI - Real-time Visitor Alert Notification Engine
Dispatches instant, non-blocking email alerts to Harshit (harshitpratap1113@gmail.com)
whenever a new user lands on LeedsFlow AI (bizflow-platform.vercel.app).

Includes:
- Primary Google Authenticated SMTP (smtp.gmail.com:587)
- Fallback 1: Resend Cloud API (https://api.resend.com/emails)
- Fallback 2: Brevo Cloud API (https://api.brevo.com/v3/smtp/email)
- 15-Minute Session/IP Cooldown Deduplication (Anti-Spam / Anti-Flood)
- Strict Anti-Freeze 4.0s Command Timeouts
- Rich Responsive Branded Dark-Card HTML Email
"""

import os
import sys
import smtplib
import time
import logging
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("leedsflow.visitor_notifier")

# =====================================================================
# 🔐 CONFIGURATION & CREDENTIALS
# =====================================================================
import base64

def _decode_key(b64_str: str) -> str:
    try:
        return base64.b64decode(b64_str.encode()).decode("utf-8")
    except Exception:
        return ""

RECIPIENT_EMAIL = "harshitpratap1113@gmail.com"
PRIMARY_SMTP_USER = "harshitpratap1113@gmail.com"
PRIMARY_SMTP_PASS = os.environ.get("GOOGLE_SMTP_PASS", _decode_key("anlmemhmeHF2Y2h2ZGtyeA=="))
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", _decode_key("cmVfTDduaGZ2eFhfOEh4bkRxdnFTUEdqeUVCdWthTW5BUll5"))
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
APP_URL = "https://bizflow-platform.vercel.app"

# 15-Minute Deduplication Cooldown Cache (key -> timestamp)
_COOLDOWN_SECONDS = 900  # 15 minutes
_VISITOR_CACHE: Dict[str, float] = {}

# Comprehensive Country Code to Flag & Name Map
COUNTRY_MAP = {
    "IN": ("India", "🇮🇳"),
    "US": ("United States", "🇺🇸"),
    "GB": ("United Kingdom", "🇬🇧"),
    "CA": ("Canada", "🇨🇦"),
    "AU": ("Australia", "🇦🇺"),
    "DE": ("Germany", "🇩🇪"),
    "FR": ("France", "🇫🇷"),
    "NL": ("Netherlands", "🇳🇱"),
    "SG": ("Singapore", "🇸🇬"),
    "AE": ("United Arab Emirates", "🇦🇪"),
    "JP": ("Japan", "🇯🇵"),
    "BR": ("Brazil", "🇧🇷"),
    "ES": ("Spain", "🇪🇸"),
    "IT": ("Italy", "🇮🇹"),
    "SE": ("Sweden", "🇸🇪"),
    "CH": ("Switzerland", "🇨🇭"),
    "IE": ("Ireland", "🇮🇪"),
    "PK": ("Pakistan", "🇵🇰"),
    "BD": ("Bangladesh", "🇧🇩"),
    "ID": ("Indonesia", "🇮🇩"),
    "PH": ("Philippines", "🇵🇭"),
    "VN": ("Vietnam", "🇻🇳"),
    "MY": ("Malaysia", "🇲🇾"),
    "RU": ("Russia", "🇷🇺"),
    "ZA": ("South Africa", "🇿🇦"),
    "NG": ("Nigeria", "🇳🇬"),
    "EG": ("Egypt", "🇪🇬"),
    "IL": ("Israel", "🇮🇱"),
    "TR": ("Turkey", "🇹🇷"),
    "PL": ("Poland", "🇵🇱")
}

def resolve_geo_info(country_raw: Optional[str], city_raw: Optional[str]) -> tuple:
    """Returns (country_name, city_name, flag_emoji)."""
    country_code = (country_raw or "").strip().upper()
    city_name = (city_raw or "").strip()
    
    if country_code in COUNTRY_MAP:
        country_name, flag = COUNTRY_MAP[country_code]
    elif len(country_code) == 2:
        # Fallback for 2-letter ISO code
        country_name = country_code
        flag = "🌐"
    elif country_raw:
        country_name = country_raw
        flag = "🌐"
        for code, (cname, cflag) in COUNTRY_MAP.items():
            if cname.lower() in country_raw.lower():
                flag = cflag
                country_name = cname
                break
    else:
        country_name = "Global Explorer"
        flag = "🌍"
        
    if not city_name or city_name.lower() in ["unknown", "none", "null"]:
        city_name = "Regional Hub"
        
    return country_name, city_name, flag

def is_duplicate_visit(ip: str, session_id: str) -> bool:
    """
    Checks if this IP or session was alerted within the cooldown window.
    Prevents inbox flood if a user clicks around or reloads.
    """
    now = time.time()
    
    # Garbage collect entries older than 2 hours
    expired_keys = [k for k, ts in _VISITOR_CACHE.items() if now - ts > 7200]
    for k in expired_keys:
        _VISITOR_CACHE.pop(k, None)
        
    keys_to_check = []
    if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
        keys_to_check.append(f"ip:{ip}")
    if session_id and session_id not in ["sess_anon", "default", ""]:
        keys_to_check.append(f"sess:{session_id}")
        
    # Check if any key is currently in cooldown
    for k in keys_to_check:
        last_time = _VISITOR_CACHE.get(k)
        if last_time and (now - last_time) < _COOLDOWN_SECONDS:
            return True
            
    # Mark as seen now
    for k in keys_to_check:
        _VISITOR_CACHE[k] = now
    return False

def build_visitor_email(visitor: Dict[str, Any]) -> tuple:
    """Generates subject, plain text, and high-impact dark HTML email body."""
    ip = visitor.get("ip", "Unknown IP")
    country_name, city_name, flag = resolve_geo_info(
        visitor.get("country"),
        visitor.get("city")
    )
    device = visitor.get("device") or "Desktop"
    os_name = visitor.get("os") or "Unknown OS"
    browser = visitor.get("browser") or "Web Browser"
    referrer = visitor.get("referrer") or "Direct Navigation (.app domain)"
    path = visitor.get("path") or "/"
    session_id = visitor.get("session_id") or "sess_live"
    meta = visitor.get("metadata") or "Live Pageview"
    
    # Formatted IST and UTC timestamp
    utc_now = datetime.now(timezone.utc)
    ist_time = utc_now + timedelta(hours=5, minutes=30)
    formatted_ist = ist_time.strftime("%d %b %Y, %I:%M:%S %p IST")
    formatted_utc = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")

    subject = f"🚨 [LeedsFlow Alert] New Visitor from {flag} {city_name}, {country_name} on LeedsFlow AI!"
    
    plain_text = f"""
LEEDSFLOW AI — LIVE VISITOR ARRIVAL ALERT
=========================================
A new visitor just landed on your LeedsFlow AI platform!

📍 Location: {flag} {city_name}, {country_name}
🌐 Visitor IP: {ip}
🧭 Traffic Source: {referrer}
💻 Device & Platform: {device} • {os_name} • {browser}
📄 Landed Path: {path}
🕒 Time (IST): {formatted_ist}
🕒 Time (UTC): {formatted_utc}
🆔 Session ID: {session_id}
📊 Event / Meta: {meta}

👉 Open LeedsFlow Platform: {APP_URL}
=========================================
LeedsFlow AI Automated Radar Telemetry
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>New Visitor on LeedsFlow AI</title>
</head>
<body style="margin: 0; padding: 24px 12px; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #111827; border-radius: 16px; border: 1px solid #374151; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5); overflow: hidden;">
    <!-- Header Banner -->
    <tr>
      <td style="padding: 24px 28px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 2px solid #ea580c;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
          <tr>
            <td>
              <div style="display: inline-block; background-color: #ea580c; color: #ffffff; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; padding: 4px 10px; border-radius: 20px; margin-bottom: 8px;">
                ⚡ Live Traffic Beacon
              </div>
              <h1 style="margin: 0; font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                🚨 New Visitor Landed!
              </h1>
              <p style="margin: 6px 0 0 0; font-size: 13px; color: #94a3b8;">
                Real-time arrival on <strong style="color: #fb923c;">LeedsFlow AI LeadRadar</strong>
              </p>
            </td>
            <td align="right" valign="top">
              <span style="font-size: 38px;">{flag}</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- Main Card Body -->
    <tr>
      <td style="padding: 28px;">
        <!-- Location Hero Pill -->
        <div style="background-color: #1e293b; border-left: 4px solid #ea580c; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px;">
          <p style="margin: 0; font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Geographic Origin</p>
          <p style="margin: 4px 0 0 0; font-size: 18px; font-weight: 700; color: #ffffff;">
            {flag} {city_name}, {country_name}
          </p>
        </div>

        <!-- Telemetry Details Table -->
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="font-size: 14px; color: #e2e8f0;">
          <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #94a3b8; width: 140px;">
              🌐 <strong>Visitor IP:</strong>
            </td>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; font-family: monospace; color: #38bdf8; font-weight: 600;">
              {ip}
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #94a3b8;">
              🧭 <strong>Traffic Source:</strong>
            </td>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #f8fafc; font-weight: 500;">
              {referrer}
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #94a3b8;">
              💻 <strong>Device / OS:</strong>
            </td>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #f8fafc;">
              {device} &bull; {os_name}
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #94a3b8;">
              🧭 <strong>Browser:</strong>
            </td>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #cbd5e1;">
              {browser}
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #94a3b8;">
              📄 <strong>Landed URL:</strong>
            </td>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; font-family: monospace; color: #a78bfa;">
              {path}
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #94a3b8;">
              🕒 <strong>Timestamp (IST):</strong>
            </td>
            <td style="padding: 10px 0; border-bottom: 1px solid #1f2937; color: #fbbf24; font-weight: 600;">
              {formatted_ist}
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0; color: #94a3b8;">
              🆔 <strong>Session ID:</strong>
            </td>
            <td style="padding: 10px 0; font-family: monospace; color: #64748b; font-size: 12px;">
              {session_id}
            </td>
          </tr>
        </table>

        <!-- Action CTA Button -->
        <div style="margin-top: 30px; text-align: center;">
          <a href="{APP_URL}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: 10px; box-shadow: 0 4px 14px rgba(234, 88, 12, 0.4);">
            🚀 Open LeedsFlow Live Radar
          </a>
        </div>
      </td>
    </tr>

    <!-- Footer -->
    <tr>
      <td style="padding: 20px 28px; background-color: #0b0f19; border-top: 1px solid #1f2937; text-align: center; font-size: 12px; color: #64748b;">
        <p style="margin: 0;">
          Sent by <strong>LeedsFlow AI Autonomous Telemetry</strong> &bull; Harshit Pratap Founder Radar
        </p>
        <p style="margin: 4px 0 0 0; font-size: 11px; color: #475569;">
          Protected by 15-minute anti-flood session deduplication &bull; Zero spam guarantee
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, plain_text, html_content

def _send_via_google_smtp(subject: str, plain: str, html: str) -> bool:
    """Attempts direct delivery using Google Mail Authenticated SMTP (4.0s timeout)."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"LeedsFlow AI Radar <{PRIMARY_SMTP_USER}>"
        msg["To"] = RECIPIENT_EMAIL
        msg["Reply-To"] = PRIMARY_SMTP_USER
        
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        
        # Hard 4.0s socket timeout to enforce strict anti-freeze rule
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=4.0)
        server.starttls()
        server.login(PRIMARY_SMTP_USER, PRIMARY_SMTP_PASS)
        server.sendmail(PRIMARY_SMTP_USER, [RECIPIENT_EMAIL], msg.as_string())
        server.quit()
        logger.info(f"[✓] Google SMTP visitor alert successfully delivered to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        logger.warning(f"[!] Google SMTP delivery failed: {e}. Trying cloud fallback...")
        return False

def _send_via_resend_api(subject: str, html: str) -> bool:
    """Fallback 1: Resend HTTP API (4.0s timeout)."""
    if not RESEND_API_KEY:
        return False
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": "LeedsFlow AI <onboarding@resend.dev>",
            "to": [RECIPIENT_EMAIL],
            "subject": subject,
            "html": html
        }
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                logger.info(f"[✓] Resend API visitor alert delivered to {RECIPIENT_EMAIL}")
                return True
            else:
                logger.warning(f"[!] Resend API failed status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.warning(f"[!] Resend API exception: {e}")
        return False

def _send_via_brevo_api(subject: str, html: str) -> bool:
    """Fallback 2: Brevo v3 HTTP API (4.0s timeout)."""
    if not BREVO_API_KEY:
        return False
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        payload = {
            "sender": {"name": "LeedsFlow AI", "email": PRIMARY_SMTP_USER},
            "to": [{"email": RECIPIENT_EMAIL, "name": "Harshit Pratap"}],
            "subject": subject,
            "htmlContent": html
        }
        with httpx.Client(timeout=4.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code in [200, 201, 202]:
                logger.info(f"[✓] Brevo API visitor alert delivered to {RECIPIENT_EMAIL}")
                return True
            else:
                logger.warning(f"[!] Brevo API failed status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.warning(f"[!] Brevo API exception: {e}")
        return False

def notify_visitor_arrival(visitor: Dict[str, Any]) -> bool:
    """
    Main entrypoint for visitor notifications.
    Checks deduplication cooldown, then dispatches email via Google SMTP -> Resend -> Brevo.
    Returns True if sent, False if skipped/failed.
    """
    ip = visitor.get("ip", "")
    session_id = visitor.get("session_id", "")
    
    # Check 15-min cooldown
    if is_duplicate_visit(ip, session_id):
        logger.info(f"[ℹ] Visitor {ip} ({session_id}) within 15-min cooldown. Skipping duplicate email.")
        return False
        
    subject, plain, html = build_visitor_email(visitor)
    
    # 1. Try Google SMTP
    if _send_via_google_smtp(subject, plain, html):
        return True
        
    # 2. Try Resend Cloud API
    if _send_via_resend_api(subject, html):
        return True
        
    # 3. Try Brevo Cloud API
    if _send_via_brevo_api(subject, html):
        return True
        
    logger.error("[✗] All notification channels failed to deliver visitor alert.")
    return False

async def notify_visitor_arrival_async(visitor: Dict[str, Any]) -> bool:
    """Async wrapper for FastAPI BackgroundTasks execution without blocking event loop."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, notify_visitor_arrival, visitor)
