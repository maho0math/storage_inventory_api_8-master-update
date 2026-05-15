import asyncio 
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import init_db
from app.core.minio_client import init_minio  
from app.worker import start_worker 

@asynccontextmanager
async def lifespan(app: FastAPI):
   
    await init_db()
    
    init_minio()
    
    worker_task = asyncio.create_task(start_worker())
    
    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        print("[*] RabbitMQ consumer has been stopped")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Lab 8 - Storage Inventory & RabbitMQ Integration", 
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
    redoc_url=None,
    lifespan=lifespan
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Automated API documentation for Storage Inventory Project",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "database": "MongoDB",
        "storage": "MinIO", 
        "broker": "RabbitMQ", 
        "status": "online"
    }