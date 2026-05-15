import uuid
from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field

class RefreshToken(Document):
    # В MongoDB/Beanie мы наследуемся от Document
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
    is_revoked: bool = False

    class Settings:
        name = "refresh_tokens" # Имя коллекции в MongoDB