from fastapi import Depends, Request, HTTPException, status, Path
from sqlalchemy.orm import Session
from .auth import auth_middleware
from routes.user import User
from models.financial import Financial
from db import db

def financial_middleware(request : Request, payload : dict = Depends(auth_middleware), session : Session = Depends(db.get_db), financial_id : int = Path(..., gt=0)) :
    if not payload :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid payload"
        )
        
    username = payload["sub"]
    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
        
    financial_data = session.query(Financial).filter(Financial.id == financial_id).first()
    if not financial_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="financian not found"
        )
    
    if financial_data.user_id != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not allowed to manage or view other's financials"
        )
        
    return payload, financial_data
       
    
    
    