from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.storage import StorageDevice
from app.models.file_meta import FileMeta  
from app.models.auth import RefreshToken 

async def init_db():
    client = AsyncIOMotorClient(
        settings.MONGO_URI,
        uuidRepresentation="standard" 
    )
    
    db = client.get_database(settings.DB_NAME)
    
    await init_beanie(
        database=db,
        document_models=[User, StorageDevice, FileMeta, RefreshToken] 
    )