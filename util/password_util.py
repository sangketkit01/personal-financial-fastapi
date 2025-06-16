from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password : str, hash_password : str):
    return pwd_context.verify(plain_password, hash_password)
