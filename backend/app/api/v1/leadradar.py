from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import MonitoredKeyword, Lead, User
from app.services.lead_radar import lead_radar_service

router = APIRouter(prefix="/leadradar", tags=["LeadRadar"])

class KeywordCreate(BaseModel):
    keyword: str
    platforms: str = "reddit,hackernews,twitter"
    min_intent_score: int = 70

class ScanRequest(BaseModel):
    keyword: Optional[str] = "saas tool alternative"
    subreddits: Optional[List[str]] = ["SaaS", "Entrepreneur", "smallbusiness", "webdev", "freelance"]

class ReplyGenerateRequest(BaseModel):
    title: str
    content: Optional[str] = ""
    author: str = "user"
    platform: str = "reddit"

class TelegramTestRequest(BaseModel):
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None

# Helper to get or create demo user
def get_or_create_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.email == "demo@bizflow.ai").first()
    if not user:
        user = User(
            email="demo@bizflow.ai",
            full_name="Harshit Pratap",
            plan="all_in_one"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.get("/keywords")
def get_keywords(db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    keywords = db.query(MonitoredKeyword).filter(MonitoredKeyword.user_id == user.id).all()
    if not keywords:
        # Seed default keywords
        defaults = ["alternative to", "need tool for", "how to automate", "looking for software"]
        for kw in defaults:
            k_obj = MonitoredKeyword(user_id=user.id, keyword=kw, min_intent_score=75)
            db.add(k_obj)
        db.commit()
        keywords = db.query(MonitoredKeyword).filter(MonitoredKeyword.user_id == user.id).all()
    return keywords

@router.post("/keywords")
def add_keyword(data: KeywordCreate, db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    k_obj = MonitoredKeyword(
        user_id=user.id,
        keyword=data.keyword.strip(),
        platforms=data.platforms,
        min_intent_score=data.min_intent_score
    )
    db.add(k_obj)
    db.commit()
    db.refresh(k_obj)
    return {"status": "success", "keyword": k_obj}

@router.delete("/keywords/{keyword_id}")
def delete_keyword(keyword_id: str, db: Session = Depends(get_db)):
    k_obj = db.query(MonitoredKeyword).filter(MonitoredKeyword.id == keyword_id).first()
    if not k_obj:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(k_obj)
    db.commit()
    return {"status": "deleted"}

@router.get("/leads")
def get_leads(platform: Optional[str] = None, min_score: Optional[int] = None, db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    query = db.query(Lead).filter(Lead.user_id == user.id)
    if platform and platform != "all":
        query = query.filter(Lead.platform == platform)
    if min_score:
        query = query.filter(Lead.intent_score >= min_score)
        
    leads = query.order_by(Lead.created_at.desc()).all()
    
    # If empty, run an initial scan to populate
    if not leads:
        scanned = lead_radar_service.scan_reddit("saas alternative tool")
        for item in scanned:
            lead = Lead(
                user_id=user.id,
                title=item["title"],
                content=item["content"],
                author=item["author"],
                platform=item["platform"],
                post_url=item["post_url"],
                intent_score=item["intent_score"],
                intent_type=item["intent_type"],
                suggested_reply=item["suggested_reply"],
                created_at=item["created_at"]
            )
            db.add(lead)
        db.commit()
        leads = db.query(Lead).filter(Lead.user_id == user.id).order_by(Lead.created_at.desc()).all()
        
    return leads

@router.post("/scan")
def trigger_scan(data: ScanRequest, db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    reddit_leads = lead_radar_service.scan_reddit(data.keyword or "tool", data.subreddits)
    hn_leads = lead_radar_service.scan_hackernews(data.keyword or "tool")
    
    combined = reddit_leads + hn_leads
    saved_count = 0
    
    for item in combined:
        # Check if already exists
        exists = db.query(Lead).filter(Lead.post_url == item["post_url"]).first()
        if not exists:
            lead = Lead(
                user_id=user.id,
                title=item["title"],
                content=item["content"],
                author=item["author"],
                platform=item["platform"],
                post_url=item["post_url"],
                intent_score=item["intent_score"],
                intent_type=item["intent_type"],
                suggested_reply=item["suggested_reply"],
                created_at=item["created_at"]
            )
            db.add(lead)
            saved_count += 1
            
            # Send Telegram alert if high intent
            if lead.intent_score >= 90:
                lead_radar_service.send_telegram_alert(item)
                lead.telegram_sent = True
                
    db.commit()
    return {
        "status": "success",
        "total_scanned": len(combined),
        "new_leads_saved": saved_count
    }

@router.post("/generate-reply")
def generate_custom_reply(data: ReplyGenerateRequest):
    reply = lead_radar_service.generate_smart_reply(data.title, data.content or "", data.platform, data.author)
    return {"reply": reply}

@router.post("/test-telegram")
def test_telegram(data: TelegramTestRequest):
    sample_lead = {
        "title": "Need an urgent alternative to expensive SaaS tools!",
        "author": "john_founder",
        "platform": "reddit",
        "intent_score": 98,
        "intent_type": "High Intent Purchase Request",
        "post_url": "https://reddit.com/r/SaaS",
        "suggested_reply": "Hey John! We solved this exact problem with BizFlow AI — fast, lightweight, and 1/5th the price."
    }
    success = lead_radar_service.send_telegram_alert(sample_lead, data.bot_token, data.chat_id)
    return {"status": "sent" if success else "failed", "success": success}
