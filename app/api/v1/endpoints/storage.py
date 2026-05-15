from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile 
from fastapi.responses import StreamingResponse
from uuid import UUID
from urllib.parse import quote  # Для поддержки русских имен файлов
from typing import List, Optional
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.storage import storage_service
from app.schemas.storage import StorageCreate, StorageUpdate, StorageResponse, StorageListResponse

router = APIRouter(tags=["Storage"])

@router.get("/", response_model=StorageListResponse)
async def read_devices(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    items, total = await storage_service.get_multi_by_owner(
        user_id=current_user.id, page=page, limit=limit
    )
    
    total_pages = (total + limit - 1) // limit
    return {
        "data": items,
        "meta": {
            "total": total, 
            "page": page, 
            "limit": limit, 
            "totalPages": total_pages
        }
    }

@router.post("/", response_model=StorageResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    obj_in: StorageCreate, 
    current_user: User = Depends(get_current_user)
):
    return await storage_service.create_with_owner(
        obj_in=obj_in, 
        user_id=current_user.id
    )

@router.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user)
):
    return await storage_service.upload_file(file, current_user.id)

@router.get("/files/{file_id}")
async def download_file(
    file_id: UUID, 
    current_user: User = Depends(get_current_user)
):

    stream, meta = await storage_service.get_file_stream(file_id, current_user.id)

    encoded_filename = quote(meta.original_name)

    def iter_file():
        try:
            for chunk in stream.stream(32 * 1024):
                yield chunk
        finally:
            stream.close()
            stream.release_conn()

    return StreamingResponse(
        iter_file(), 
        media_type=meta.mimetype,
        headers={
            "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}",
            "Content-Length": str(meta.size)
        }
    )

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID, 
    current_user: User = Depends(get_current_user)
):
    await storage_service.delete_file(file_id, current_user.id)
    return None