from sqlalchemy import Column, String, DateTime, UniqueConstraint
from db import db
from datetime import datetime

class User(db.Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True, unique=True)
    phone = Column(String(10), nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("email"),
    )