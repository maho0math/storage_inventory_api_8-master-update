import io
from uuid import UUID, uuid4
from fastapi import HTTPException, status, UploadFile
from minio.error import S3Error
from datetime import datetime
from app.models.file_meta import FileMeta
from app.core.minio_client import minio_client
from app.core.config import settings
from app.services.cache import cache_service

class StorageService:
    async def upload_file(self, file: UploadFile, user_id: UUID) -> FileMeta:
        
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        object_key = f"{user_id}/{uuid4()}_{file.filename}"
        
        try:
            minio_client.put_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=object_key,
                data=file.file, 
                length=file.size,
                content_type=file.content_type
            )
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

        file_meta = FileMeta(
            owner_id=user_id,
            original_name=file.filename,
            object_key=object_key,
            size=file.size,
            mimetype=file.content_type,
            bucket=settings.MINIO_BUCKET
        )
        await file_meta.insert()
        
       
        cache_service.delete(f"wp:files:user:{user_id}")
        
        return file_meta

    async def get_file_stream(self, file_id: UUID, user_id: UUID):
        
        cache_key = f"wp:files:{file_id}:meta"
        cached_meta = cache_service.get(cache_key)
        
        if cached_meta:
            file_meta = FileMeta.model_validate(cached_meta)
        else:
            file_meta = await FileMeta.find_one(
                FileMeta.id == file_id, 
                FileMeta.deleted_at == None
            )
            if file_meta:
                
                cache_service.set(cache_key, file_meta.model_dump(mode='json'), ttl=300)

        if not file_meta or file_meta.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied or file not found")

        try:
            response = minio_client.get_object(file_meta.bucket, file_meta.object_key)
            return response, file_meta
        except S3Error:
            raise HTTPException(status_code=404, detail="File not found in storage")

    async def delete_file(self, file_id: UUID, user_id: UUID):
       
        file_meta = await FileMeta.find_one(
            FileMeta.id == file_id, 
            FileMeta.deleted_at == None
        )

        if not file_meta or file_meta.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="File not found"
            )

        try:
            minio_client.remove_object(file_meta.bucket, file_meta.object_key)
        except S3Error:
            pass # Если в MinIO файла уже нет, продолжаем удаление в БД [cite: 2026-04-23]

        file_meta.deleted_at = datetime.utcnow()
        await file_meta.save()

        # Чистим кэш после удаления
        cache_service.delete(f"wp:files:{file_id}:meta")
        cache_service.delete(f"wp:files:user:{user_id}")

    async def get_all_by_user(self, user_id: UUID, page: int = 1, limit: int = 10):
    
        skip = (page - 1) * limit
        query = FileMeta.find(
            FileMeta.owner_id == user_id, 
            FileMeta.deleted_at == None
        )
        
        total = await query.count()
        items = await query.skip(skip).limit(limit).to_list()
        
        return items, total

    async def file_exists(self, object_key: str) -> bool:
        try:
            minio_client.stat_object(settings.MINIO_BUCKET, object_key)
            return True
        except S3Error:
            return False


storage_service = StorageService()