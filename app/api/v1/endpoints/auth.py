from fastapi import APIRouter, Depends, status, HTTPException, Response, Cookie
from typing import Optional
from uuid import UUID
from app.schemas.user import UserCreate, UserRead
from app.models.user import User
from app.core.security import security_helper
from app.api.v1.deps import get_current_user, get_queue  
from app.services.cache import cache_service
from app.services.queue import QueueService  

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, 
    queue: QueueService = Depends(get_queue) #сервис очереди
):
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = security_helper.hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    await new_user.insert()

    await queue.publish_registration_event(new_user)

    return new_user

@router.post("/login")
async def login(response: Response, user_data: UserCreate):
    user = await User.find_one(User.email == user_data.email)
    
    if not user or not security_helper.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="User is inactive or deleted")

    token = security_helper.create_access_token(data={"sub": str(user.id)})
    payload = security_helper.decode_token(token)
    jti = payload.get("jti")

    session_key = f"auth:user:{user.id}:access:{jti}"
    cache_service.set(session_key, "active", ttl=3600) 
    
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {token}", 
        httponly=True,
        max_age=3600,
        samesite="lax",
        secure=False 
    )
    
    return {"status": "success", "message": "Logged in and session registered"}

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    access_token: Optional[str] = Cookie(None)
):
    if access_token:
        token_data = access_token.split(" ")[1] if " " in access_token else access_token
        payload = security_helper.decode_token(token_data)
        
        if payload:
            jti = payload.get("jti")
            user_id = payload.get("sub")
            session_key = f"auth:user:{user_id}:access:{jti}"
            cache_service.delete(session_key)
    
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully and session invalidated"}