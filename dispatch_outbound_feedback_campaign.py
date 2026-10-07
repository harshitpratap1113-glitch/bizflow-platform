import os
import sys
import smtplib
import json
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bizflow.feedback_campaign")

# Configuration from Environment
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER or "feedback@bizflow.ai")
FROM_NAME = "BizFlow AI Team"
APP_URL = os.environ.get("APP_URL", "https://bizflow-platform.vercel.app")

# Curated List of Beta Testers & Agency Founders (Target ICPs)
TARGET_RECIPIENTS = [
    {
        "name": "Alex Morgan",
        "email": "alex.dev@agencyflow.io",
        "niche": "Web & Next.js Development",
        "role": "Agency Founder",
        "recent_topic": "Struggling with Upwork 15% fees and low cold email reply rates"
    },
    {
        "name": "Sarah Jenkins",
        "email": "sarah@lumina-creative.design",
        "niche": "UI/UX & Brand Design",
        "role": "Design Lead & Freelancer",
        "recent_topic": "Need steady high-ticket design client pipeline"
    },
    {
        "name": "Vikram Sethi",
        "email": "vikram@aix-solutions.tech",
        "niche": "AI Automation & LLM Pipelines",
        "role": "Automation Consultant",
        "recent_topic": "Finding business owners looking to automate workflows"
    },
    {
        "name": "David Miller",
        "email": "david@hypermotion.video",
        "niche": "High-Retention Video Editing",
        "role": "Video Studio Founder",
        "recent_topic": "YouTube creators and brands needing fast turnaround edits"
    },
    {
        "name": "Elena Rostova",
        "email": "elena@ecomboost.co",
        "niche": "Shopify CRO & Performance",
        "role": "E-Commerce Consultant",
        "recent_topic": "Store owners asking for checkout optimization"
    }
]

def generate_email_content(recipient: dict) -> tuple:
    subject = f"Quick question about finding {recipient['niche']} clients (Free Beta Access)"
    
    text_content = f"""Hi {recipient['name']},

I noticed your recent discussions around {recipient['recent_topic']}. 

Like many {recipient['role']}s, the biggest bottleneck is finding clients who actually have a real budget without paying 10-20% Upwork fees or burning domains on cold email.

We built BizFlow LeadRadar (https://bizflow-platform.vercel.app) — a real-time buyer intent engine that monitors 100+ communities across {recipient['niche']} and 9 other industries 24/7. It filters out spam/$0 gigs and gives you verified buyer leads with 1-click custom proposals.

Could you test it for 2 minutes and give us your brutal feedback?
Live App: {APP_URL}

3 Quick Questions for You:
1. Did the verified feed show real hiring leads for {recipient['niche']}?
2. What 1 community or feature should we add for your workflow?
3. Would a tool like this be worth $19/mo once out of beta?

You can test the live tool directly at: {APP_URL}
Or simply reply directly to this email with your thoughts.

Thanks a ton for your honest review!

Best regards,
Harshit & The BizFlow AI Team
{APP_URL}
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }}
    .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 28px; max-width: 600px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
    .header {{ border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 20px; }}
    .badge {{ display: inline-block; background: #ea580c; color: white; padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
    h2 {{ color: #f8fafc; margin-top: 10px; font-size: 20px; }}
    p {{ line-height: 1.6; color: #cbd5e1; font-size: 14px; }}
    .btn {{ display: inline-block; background: linear-gradient(135deg, #ea580c, #f59e0b); color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 12px; font-weight: bold; font-size: 14px; margin: 18px 0; text-align: center; }}
    .box {{ background: #0f172a; border-left: 4px solid #ea580c; padding: 14px; border-radius: 8px; margin: 16px 0; font-size: 13px; color: #94a3b8; }}
    .footer {{ margin-top: 24px; font-size: 12px; color: #64748b; border-top: 1px solid #334155; padding-top: 14px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <span class="badge">VIP Beta Feedback Invitation</span>
      <h2>Hey {recipient['name']}, need your honest feedback on BizFlow LeadRadar</h2>
    </div>

    <p>I saw your focus on <strong>{recipient['niche']}</strong>. Finding steady client projects without paying massive Upwork commissions or getting 0 replies on cold emails is brutal.</p>

    <p>We built <strong>BizFlow LeadRadar</strong> to solve this: it tracks <strong>100+ communities 24/7</strong> for real-time buyer intent, filters out $0/unpaid gigs using AI, and gives you instant 1-click pitches tailored to your service.</p>

    <div style="text-align: center;">
      <a href="{APP_URL}" class="btn" target="_blank">🚀 Open Free Live App ({APP_URL})</a>
    </div>

    <div class="box">
      <strong>🎯 3 Quick Questions for Your Review:</strong>
      <ol style="margin: 8px 0 0 16px; padding: 0;">
        <li>Does the Verified stream surface relevant client leads for {recipient['niche']}?</li>
        <li>Which specific community or feature is currently missing for your agency?</li>
        <li>Would you pay $19-$29/month if this delivered 5 fresh verified leads daily?</li>
      </ol>
    </div>

    <p>You can reply directly to this email or click the <strong>"⭐ Give Feedback"</strong> button inside the app. Your raw, unfiltered thoughts mean the world to us!</p>

    <div class="footer">
      Sent with ❤️ by BizFlow AI Team &bull; <a href="{APP_URL}" style="color: #ea580c;">bizflow-platform.vercel.app</a>
    </div>
  </div>
</body>
</html>
"""
    return subject, text_content, html_content

def send_campaign():
    logger.info(f"[*] Initializing BizFlow Direct Feedback Campaign to {len(TARGET_RECIPIENTS)} ICP recipients...")
    logger.info(f"[*] Target Application URL: {APP_URL}")
    
    can_send_smtp = bool(SMTP_USER and SMTP_PASS)
    if can_send_smtp:
        logger.info(f"[*] Active SMTP Connection detected ({SMTP_HOST}:{SMTP_PORT}). Sending live emails...")
    else:
        logger.info("[!] SMTP credentials not set in env (SMTP_USER/SMTP_PASS). Running in AUDIT & LOG MODE (Generating email payloads & dispatch logs).")

    dispatched = []

    for r in TARGET_RECIPIENTS:
        subject, text_body, html_body = generate_email_content(r)
        
        if can_send_smtp:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
                msg["To"] = r["email"]
                
                msg.attach(MIMEText(text_body, "plain"))
                msg.attach(MIMEText(html_body, "html"))
                
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASS)
                    server.sendmail(FROM_EMAIL, r["email"], msg.as_string())
                
                logger.info(f"[✓] LIVE EMAIL SENT to {r['name']} ({r['email']})")
                dispatched.append({"recipient": r["email"], "status": "sent", "mode": "smtp_live"})
            except Exception as e:
                logger.error(f"[X] Failed to send email to {r['email']}: {e}")
                dispatched.append({"recipient": r["email"], "status": "error", "error": str(e)})
        else:
            logger.info(f"[✓] DISPATCH PACKET READY for {r['name']} ({r['email']}) -> Niche: {r['niche']}")
            dispatched.append({
                "recipient": r["email"],
                "name": r["name"],
                "niche": r["niche"],
                "subject": subject,
                "app_url": APP_URL,
                "status": "ready_for_dispatch",
                "mode": "simulated_audit"
            })

    # Save campaign log
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feedback_campaign_results.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "app_url": APP_URL,
            "total_recipients": len(TARGET_RECIPIENTS),
            "dispatched": dispatched
        }, f, indent=2)

    logger.info(f"[✓] Campaign processing completed! Summary saved to {log_file}")
    return dispatched

if __name__ == "__main__":
    send_campaign()
