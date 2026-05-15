from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import security_helper

class AuthService:
    @staticmethod
    async def register_new_user(user_data: UserCreate) -> User:
        # Асинхронный поиск в Beanie
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        new_user = User(
            email=user_data.email,
            hashed_password=security_helper.hash_password(user_data.password),
            is_active=True
        )
        await new_user.insert() # Вставка в MongoDB
        return new_user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> User | None:
        # Асинхронный поиск
        user = await User.find_one(User.email == email)
        if not user or user.deleted_at is not None:
            return None
        if not security_helper.verify_password(password, user.hashed_password):
            return None
        return user

auth_service = AuthService()