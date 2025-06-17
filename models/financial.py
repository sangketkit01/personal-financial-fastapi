from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
from datetime import datetime
from db import db

class Financial(db.Base):
    __tablename__ = "financials"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    amount = Column(BigInteger, ForeignKey("users.username"),nullable=False)
    direction = Column(String, nullable=False)
    type_id = Column(BigInteger, ForeignKey("financial_types.id"),nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)