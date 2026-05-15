import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import APIKeyCookie

from app.core.config import settings 

if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type('About', (object,), {'__version__': bcrypt.__version__})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

cookie_sec_scheme = APIKeyCookie(name="access_token", auto_error=False)

class SecurityHelper:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:

        to_encode = data.copy()
        
        jti = str(uuid.uuid4())
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "jti": jti
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_ACCESS_SECRET, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
            payload = jwt.decode(
                token, 
                settings.JWT_ACCESS_SECRET, 
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

security_helper = SecurityHelper()