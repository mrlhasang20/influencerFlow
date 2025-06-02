from sqlalchemy import Column, String, Integer, Float, JSON, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Creator(Base):
    __tablename__ = "creators"

    id = Column(String, primary_key=True)
    name = Column(String)
    handle = Column(String)
    platform = Column(String)
    followers = Column(Integer)
    engagement_rate = Column(Float)
    categories = Column(JSON)
    demographics = Column(JSON)
    content_style = Column(JSON)
    location = Column(String)
    collaboration_rate = Column(String)
    response_rate = Column(Float)
    language = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
