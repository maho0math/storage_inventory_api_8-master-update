from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.file_meta import FileMeta
from app.services.cache import cache_service

router = APIRouter(tags=["Users"])

@router.get("/me")
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/profile")
async def update_profile(
    avatar_file_id: UUID, 
    current_user: User = Depends(get_current_user)
):
    file_meta = await FileMeta.find_one(FileMeta.id == avatar_file_id)

    if not file_meta or file_meta.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="File not found"
        )
    
    if not file_meta.mimetype.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="Only image"
        )

    current_user.avatar_file_id = avatar_file_id
    await current_user.save()
    
    cache_service.delete(f"wp:profile:{current_user.id}")
    
    return current_user