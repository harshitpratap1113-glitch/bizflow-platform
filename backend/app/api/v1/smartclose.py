from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Proposal, User

router = APIRouter(prefix="/smartclose", tags=["SmartClose"])

class ProposalCreate(BaseModel):
    client_name: str
    client_email: Optional[str] = ""
    client_phone: Optional[str] = ""
    project_title: str
    project_scope: Optional[str] = ""
    total_amount: float
    deposit_amount: float
    currency: str = "USD"

def get_or_create_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.email == "demo@bizflow.ai").first()
    if not user:
        user = User(email="demo@bizflow.ai", full_name="Harshit Pratap", plan="all_in_one")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.get("/proposals")
def get_proposals(db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    proposals = db.query(Proposal).filter(Proposal.user_id == user.id).order_by(Proposal.created_at.desc()).all()
    
    if not proposals:
        # Seed initial sample proposals
        sample1 = Proposal(
            user_id=user.id,
            client_name="Acme Corp (Sarah Miller)",
            client_email="sarah@acmecorp.com",
            client_phone="+1 555-0192",
            project_title="Brand Identity & Web Redesign",
            project_scope="Complete UI/UX redesign, Next.js frontend, and mobile optimization.",
            total_amount=2400.0,
            deposit_amount=1200.0,
            status="viewed",
            view_count=4
        )
        sample2 = Proposal(
            user_id=user.id,
            client_name="Apex Media Solutions",
            client_email="contact@apexmedia.io",
            client_phone="+91 9876543210",
            project_title="Monthly Video Editing Package (10 Videos)",
            project_scope="10 Reels/Shorts + 2 Long-form YouTube videos per month.",
            total_amount=1500.0,
            deposit_amount=750.0,
            status="deposit_paid",
            view_count=8
        )
        db.add_all([sample1, sample2])
        db.commit()
        proposals = db.query(Proposal).filter(Proposal.user_id == user.id).all()
        
    return proposals

@router.post("/proposals")
def create_proposal(data: ProposalCreate, db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    proposal = Proposal(
        user_id=user.id,
        client_name=data.client_name,
        client_email=data.client_email,
        client_phone=data.client_phone,
        project_title=data.project_title,
        project_scope=data.project_scope,
        total_amount=data.total_amount,
        deposit_amount=data.deposit_amount,
        currency=data.currency,
        status="sent"
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return {"status": "success", "proposal": proposal}

@router.get("/view/{proposal_id}")
def view_proposal_client(proposal_id: str, db: Session = Depends(get_db)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Increment view count
    proposal.view_count += 1
    if proposal.status == "sent":
        proposal.status = "viewed"
    db.commit()
    db.refresh(proposal)
    
    return {
        "id": proposal.id,
        "client_name": proposal.client_name,
        "project_title": proposal.project_title,
        "project_scope": proposal.project_scope,
        "total_amount": proposal.total_amount,
        "deposit_amount": proposal.deposit_amount,
        "currency": proposal.currency,
        "status": proposal.status,
        "view_count": proposal.view_count,
        "created_at": proposal.created_at
    }
