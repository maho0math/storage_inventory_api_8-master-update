from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class StorageBase(BaseModel):
    model: str = Field(..., example="Kingston KC3000 1024GB", description="The commercial name of the storage device")
    serial_number: str = Field(..., example="K-SN-2026-XYZ", description="Unique manufacturer serial number")
    capacity_gb: int = Field(..., gt=0, example=1024, description="Storage capacity in Gigabytes")
    status: Optional[str] = Field("active", example="active", description="Current status: active, stored, or faulty")

class StorageCreate(StorageBase):
    pass

class StorageUpdate(BaseModel):
    model: Optional[str] = Field(None, example="Samsung 980 Pro")
    serial_number: Optional[str] = Field(None, example="S-SN-2026-ABC")
    capacity_gb: Optional[int] = Field(None, gt=0, example=2048)
    status: Optional[str] = Field(None, example="stored")

class StorageResponse(StorageBase):
    id: UUID = Field(..., description="Unique internal database ID (UUID)")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp of the last update")
    deleted_at: Optional[datetime] = Field(None, description="Soft-delete timestamp (null if active)")

    # Metadata for Swagger examples
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "82ee23d1-9ca1-4968-91b8-22507d378c2c",
                "model": "Kingston KC3000 1024GB",
                "serial_number": "K-SN-2026-XYZ",
                "capacity_gb": 1024,
                "status": "active",
                "created_at": "2026-03-19T23:07:16",
                "updated_at": "2026-03-19T23:07:16",
                "deleted_at": None
            }
        }
    )

class StorageListResponse(BaseModel):
    data: List[StorageResponse]
    meta: dict = Field(..., example={"total": 1, "page": 1, "limit": 10}, description="Pagination metadata")