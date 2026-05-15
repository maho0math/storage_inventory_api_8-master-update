import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Optional
from app.core.config import settings
from app.services.cache import cache_service
from app.core.security import security_helper
from app.models.user import User
# Добавленные импорты для работы с очередью
from app.api.v1.deps import get_queue
from app.services.queue import QueueService

router = APIRouter(tags=["Yandex OAuth"])

@router.get("/login")
async def yandex_login():
    url = (
        f"https://oauth.yandex.ru/authorize?response_type=code"
        f"&client_id={settings.YANDEX_CLIENT_ID}"
        f"&redirect_uri={settings.YANDEX_REDIRECT_URI}"
    )
    return {"login_url": url}

@router.get("/callback")
async def yandex_callback(
    code: str, 
    response: Response,
    # Внедряем зависимость очереди
    queue: QueueService = Depends(get_queue)
):
    async with httpx.AsyncClient() as client:
        # 1. Обмен кода на токен
        token_res = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET,
            }
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Yandex Token Error")
        
        access_token = token_res.json().get("access_token")

        # 2. Получение данных пользователя
        user_res = await client.get(
            "https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"}
        )
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Yandex User Info Error")
            
        user_data = user_res.json()

    yandex_user_id = user_data.get("id")
    email = user_data.get("default_email")
    
    # 3. Поиск или создание пользователя в БД
    user = await User.find_one(User.yandex_id == str(yandex_user_id))
    
    if not user:
        user = User(
            email=email, 
            yandex_id=str(yandex_user_id), 
            hashed_password="oauth_managed_login", 
            is_active=True
        )
        await user.insert() 
        
        # ОТПРАВКА СОБЫТИЯ В ОЧЕРЕДЬ
        # Вызываем воркер для отправки приветственного письма новому юзеру
        await queue.publish_registration_event(user) 
    
    if user.deleted_at is not None:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # 4. Создание сессии и JWT
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
        samesite="lax"
    )
    
    return {"status": "success", "user": email}