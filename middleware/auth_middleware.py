from fastapi import HTTPException, Request, status
from util import jwt_util

bearer = "bearer"

def authentication(request: Request) :
    headers = request.headers.get("authorization")
    if not headers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
        
    auth = headers.split(" ", 1)
    if len(auth) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    authorization_header = auth[0]
    if authorization_header.lower() != bearer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unsupported authorization header type"
        )
    
    token = auth[1]
    payload = jwt_util.verify_access_token(token=token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )
    
    return payload
    