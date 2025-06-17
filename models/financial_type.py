from sqlalchemy import Column, BigInteger, String
from db import db

class FinanCialType(db.Base) :
    __tablename__ = "financial_types"
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(String, nullable=False)
    