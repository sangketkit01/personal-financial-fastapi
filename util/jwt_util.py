from datetime import datetime, timedelta
from typing import Optional
import uuid
from config import config
from jose import JWTError, jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) :
    issued_at = datetime.utcnow()
    expired_at = issued_at + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    payload = data.copy()
    
    token_id = str(uuid.uuid4())
    payload.update(
        {
            "jti": token_id,
            "iat" : int(issued_at.timestamp()),
            "exp": int(expired_at.timestamp()),
        }
    )
    
    encoded_jwt = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt, issued_at, expired_at, token_id

def verify_access_token(token: str) :
    try :
        payload = jwt.decode(token=token, key=config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except JWTError:
        return None
    
