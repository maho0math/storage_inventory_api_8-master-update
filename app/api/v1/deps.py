from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status, Cookie, Depends, Request
from jose import jwt, JWTError

from app.models.user import User
from app.core.config import settings 
from app.services.cache import cache_service
from app.core.security import cookie_sec_scheme 
from app.services.queue import QueueService 

async def get_current_user(
    token_from_scheme: str = Depends(cookie_sec_scheme),
    access_token: Optional[str] = Cookie(None) 
) -> User:
    # Get current user from JWT in Cookie and check Redis session
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated: No session cookie found"
        )

    try: 
        token_data = access_token.split(" ")[1] if " " in access_token else access_token
        
        payload = jwt.decode(
            token_data, 
            settings.JWT_ACCESS_SECRET, 
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti") 
        
        if user_id is None or jti is None:
            raise HTTPException(status_code=401, detail="Invalid token: Missing sub or jti")

        session_key = f"auth:user:{user_id}:access:{jti}"
        active_session = cache_service.get(session_key)
        
        if not active_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Session has expired or was logged out"
            )
            
        current_user_uuid = UUID(user_id)
        
    except (JWTError, IndexError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials"
        )

    user = await User.get(current_user_uuid)

    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="User not found or account deleted")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_queue():
    # Dependency for RabbitMQ QueueService
    queue = QueueService()
    await queue.connect()
    try:
        yield queue
    finally:
        if queue.connection:
            await queue.connection.close()