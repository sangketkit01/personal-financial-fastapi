from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from passlib.context import CryptContext

from sqlalchemy import  Column, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db import db

from util import password_util, jwt_util

from middleware import auth_middleware



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
    

class CreateUserRequest(BaseModel):
    username : str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    email : str = EmailStr
    phone : str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=8)
    
class CreateUserResponse(BaseModel) :
    username : str
    name: str
    email: str
    phone: str
    created_at : datetime
    updated_at : datetime
    

router = APIRouter(
    tags=["users"],
)

@router.post("/", response_model=CreateUserResponse)
def create_user(req: CreateUserRequest, session=Depends(db.get_db)):
    hashed_pw = password_util.hash_password(req.password)
    user = User(
        username=req.username,
        name=req.name,
        email=req.email,
        phone=req.phone,
        password=hashed_pw
    )
    session.add(user)
    try:
        session.commit()
        session.refresh(user)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="username or email already exists"
        )
    return CreateUserResponse(
        username=user.username,
        name=user.name,
        email=user.email,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    
class LoginUserRequest(BaseModel) :
    username : str = Field(... , min_length=1)
    password : str = Field(... , min_length=8)

class LoginUserResponse(BaseModel) :
    username: str
    name: str
    email: str
    phone: str
    created_at : datetime
    updated_at : datetime
    token_id : str
    access_token : str
    issued_at : datetime
    expired_at : datetime
    
@router.post("/login", response_model=LoginUserResponse)
def login_user(req : LoginUserRequest, session: Session = Depends(db.get_db)):
    user = session.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )
    
    if not password_util.verify_password(req.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid password"
        )
    
    token_data = {"sub" : user.username}
    access_token, issued_at, expired_at, token_id = jwt_util.create_access_token(token_data, timedelta(hours=24))
    
    return LoginUserResponse(
        username=user.username,
        name=user.name,
        email=user.email,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at,
        token_id=token_id,
        access_token=access_token,
        issued_at=issued_at,
        expired_at=expired_at
    )
    
    
class UpdateUserPasswordRequest(BaseModel):
    current_password : str = Field(..., min_length=8)
    new_password : str = Field(..., min_length=8)
    confirm_password : str = Field(..., min_length=8)
    
@router.post("/update-password")
def update_user_password(*, payload : dict = Depends(auth_middleware.authentication), req : UpdateUserPasswordRequest, session : Session = Depends(db.get_db)) :
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
        
    if not password_util.verify_password(req.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
        
    if req.new_password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not match"
        )
        
    hashed_password = password_util.hash_password(req.new_password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    
    return {"message" : "Password updated successfully"}