# Postgres integration
from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

# Database engine
engine = create_engine(settings.postgres_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Creator(Base):
    __tablename__ = "creators"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    handle = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    followers = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    categories = Column(JSON, default=[])
    demographics = Column(JSON, default={})
    content_style = Column(String)
    language = Column(String, default="English")
    location = Column(String)
    collaboration_rate = Column(String)
    response_rate = Column(Integer, default=0)
    embedding = Column(JSON)  # Store vector embeddings
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True, index=True)
    brand_name = Column(String, nullable=False)
    campaign_name = Column(String, nullable=False)
    description = Column(String)
    target_audience = Column(String)
    budget_range = Column(String)
    timeline = Column(String)
    deliverables = Column(JSON, default=[])
    status = Column(String, default="draft")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Collaboration(Base):
    __tablename__ = "collaborations"
    
    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, nullable=False)
    creator_id = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, negotiating, accepted, rejected, completed
    outreach_message = Column(String)
    negotiation_history = Column(JSON, default=[])
    final_terms = Column(JSON, default={})
    contract_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True, index=True)
    collaboration_id = Column(String, nullable=False)
    contract_text = Column(String)
    terms = Column(JSON, default={})
    status = Column(String, default="draft")  # draft, sent, signed, executed
    created_at = Column(DateTime, default=datetime.utcnow)
    signed_at = Column(DateTime)

# Database utilities
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get database session for direct use"""
    return SessionLocal()