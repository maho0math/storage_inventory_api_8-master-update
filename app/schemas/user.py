from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com", description="User's primary email address")

class UserCreate(UserBase):
    """Schema for user registration. Includes password validation."""
    password: str = Field(..., min_length=8, example="Secret1234", description="Plain text password (min 8 chars, 1 digit)") 

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserRead(UserBase):
    """Schema for displaying user info. Sensitive data (password) is EXCLUDED."""
    id: UUID = Field(..., description="User's unique identifier")
    is_active: bool = Field(..., example=True, description="Account status")
 
    yandex_id: Optional[str] = Field(None, example="123456789", description="Yandex unique identifier")
    created_at: datetime = Field(..., description="Registration date")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "is_active": True,
                "yandex_id": "123456789",
                "created_at": "2026-03-01T12:00:00"
            }
        }
    )