from pydantic_settings import BaseSettings
from minio import Minio

class Settings(BaseSettings):
    MONGODB_URL: str
    DATABASE_NAME: str
    
    # MinIO Settings
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "documentos"

    class Config:
        env_file = ".env"

settings = Settings()

# Inicialização do Cliente MinIO
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

# Criar o bucket automaticamente se não existir
if not minio_client.bucket_exists(settings.MINIO_BUCKET):
    minio_client.make_bucket(settings.MINIO_BUCKET)