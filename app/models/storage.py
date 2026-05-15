import uuid
from datetime import datetime
from typing import Optional, Annotated 
from pydantic import Field
from beanie import Document, Indexed

class StorageDevice(Document):

    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    user_id: Annotated[uuid.UUID, Indexed()]
    
    model: str  
   
    serial_number: Annotated[str, Indexed(unique=True)]
    
    capacity_gb: int
    status: str = "active"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 
    
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "storage_devices"

    def __repr__(self):
        return f"<StorageDevice(model={self.model}, sn={self.serial_number}, user_id={self.user_id})>"