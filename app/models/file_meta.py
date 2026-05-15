from beanie import Document
from pydantic import Field
from uuid import UUID, uuid4
from datetime import datetime

class FileMeta(Document):
    id: UUID = Field(default_factory=uuid4)
    owner_id: UUID
    original_name: str
    object_key: str  
    size: int
    mimetype: str
    bucket: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    class Settings:
        name = "files_metadata"