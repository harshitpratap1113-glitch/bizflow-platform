import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), default="Founder")
    plan = Column(String(50), default="all_in_one")  # 'free', 'single', 'all_in_one'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    keywords = relationship("MonitoredKeyword", back_populates="user")
    leads = relationship("Lead", back_populates="user")
    proposals = relationship("Proposal", back_populates="user")

class MonitoredKeyword(Base):
    __tablename__ = "monitored_keywords"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    keyword = Column(String(100), nullable=False)
    platforms = Column(String(255), default="reddit,hackernews,twitter")  # comma separated
    min_intent_score = Column(Integer, default=70)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="keywords")
    leads = relationship("Lead", back_populates="keyword_rel")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    keyword_id = Column(String(36), ForeignKey("monitored_keywords.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    author = Column(String(100), default="anonymous")
    platform = Column(String(50), default="reddit")  # 'reddit', 'twitter', 'hackernews'
    post_url = Column(Text, nullable=False)
    intent_score = Column(Integer, default=85)  # 0 to 100
    intent_type = Column(String(100), default="Looking for Tool / Alternative")
    suggested_reply = Column(Text, nullable=True)
    status = Column(String(50), default="new")  # 'new', 'replied', 'converted', 'archived'
    telegram_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="leads")
    keyword_rel = relationship("MonitoredKeyword", back_populates="leads")

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    client_name = Column(String(150), nullable=False)
    client_email = Column(String(150), nullable=True)
    client_phone = Column(String(50), nullable=True)
    project_title = Column(String(255), nullable=False)
    project_scope = Column(Text, nullable=True)
    total_amount = Column(Float, default=0.0)
    deposit_amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="sent")  # 'sent', 'viewed', 'deposit_paid', 'completed'
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="proposals")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    business_name = Column(String(150), nullable=False)
    business_category = Column(String(100), default="Clinic")
    google_review_url = Column(Text, nullable=False)
    whatsapp_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    feedbacks = relationship("CustomerFeedback", back_populates="business")

class CustomerFeedback(Base):
    __tablename__ = "customer_feedbacks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("business_profiles.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    customer_name = Column(String(100), default="Anonymous")
    customer_phone = Column(String(50), nullable=True)
    feedback_text = Column(Text, nullable=True)
    redirected_to_google = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    business = relationship("BusinessProfile", back_populates="feedbacks")

class DocumentJob(Base):
    __tablename__ = "document_jobs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="completed")  # 'processing', 'completed', 'failed'
    extracted_rows = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    excel_download_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
