from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from db import db
from sqlalchemy.orm import Session
from datetime import datetime
from middleware import auth, financial
from .user import User
from models.financial import Financial
from models.financial_type import FinanCialType

financial_router = APIRouter(
    tags=["financials"],
)

class NewFinancialRequest(BaseModel) :
    amount : int = Field(..., )
    type : str = Field(..., min_length=1)
    

@financial_router.post("/new-financial")
def add_new_financial(*, req : NewFinancialRequest, payload : dict = Depends(auth.auth_middleware), session : Session = Depends(db.get_db)):
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid payload"
        )
    
    username = payload["sub"]
    user = session.query(User).filter(User.username == username).first()
    if not user :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    type_id = 0 
    req_type = req.type[0].upper() + req.type[1:].lower()
    financial_type_data = session.query(FinanCialType).filter(FinanCialType.type == req_type).first()
    if not financial_type_data :
        type_id = 10
    else :
        type_id = financial_type_data.id
        
    if req.amount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount cannot be zero"
        )
    
    direction = "in"
    if req.amount < 0 :
        direction = "out"
        
    insert_data = Financial(
        user_id=username,
        amount = abs(req.amount),
        direction=direction,
        type_id = type_id,
    )
    
    session.add(insert_data)
    session.commit()
    
    return {"message" : "create new financial successfully"}

class FinancialResponse(BaseModel):
    id : int
    user_id : str
    amount : int
    direction : str
    type_id : int
    created_at : datetime
    
@financial_router.get("/my-financial", response_model=List[FinancialResponse])
def my_financial(session : Session = Depends(db.get_db), payload : dict = Depends(auth.auth_middleware)) :
    username = payload["sub"]
    financials = session.query(Financial).filter(Financial.user_id == username).all()

    return financials

@financial_router.get("/financial/{financial_id}", response_model=FinancialResponse)
def get_financial_by_id(session : Session = Depends(db.get_db), payload_and_data : Tuple[dict, Financial] = Depends(financial.financial_middleware)):
    _, financial_data = payload_and_data
    
    return financial_data

class UpdateFinancialRequest(BaseModel):
    amount : int = Field(...)
    type : str = Field(..., min_length=1)

@financial_router.put("/financial/{financial_id}")
def update_financial(req : UpdateFinancialRequest, session : Session = Depends(db.get_db), payload_and_data : Tuple[dict, Financial] = Depends(financial.financial_middleware)) :
    _, financial_data = payload_and_data
    
    if req.amount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount cannot be zero"
        )
        
    type_id = 0
    req_type = req.type[0].upper() + req.type[1:].lower()
    financial_type = session.query(FinanCialType).filter(FinanCialType.type == req_type).first()
    if not financial_type:
        type_id = 10
    else :
        type_id = financial_type.id
        
    direction = "in"
    if req.amount < 0:
        direction = "out"  
        
    abs_amount = abs(req.amount)
    
    financial_data.amount = abs_amount
    financial_data.type_id = type_id
    financial_data.direction = direction
    
    session.commit()
    session.refresh(financial_data)
    
    return {
        "message" : "Financial updated successfully",
        "updated_data" : financial_data
    }

@financial_router.delete("/financial/{financial_id}")
def delete_financial(session : Session = Depends(db.get_db), payload_and_data : Tuple[dict, Financial] = Depends(financial.financial_middleware)) :
    _, financial_data = payload_and_data
    session.delete(financial_data)
    session.commit()
    
    return {
        "message" : "Financial deleted successfully.",
        "deleted_data" : financial_data
    }