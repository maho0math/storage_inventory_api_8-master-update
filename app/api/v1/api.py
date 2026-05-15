from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.storage import router as storage_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.yandex_auth import router as yandex_router

api_router = APIRouter()


api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(storage_router, prefix="/devices", tags=["Storage"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(yandex_router, prefix="/yandex", tags=["Yandex Auth"])