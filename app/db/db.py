from pymongo import AsyncMongoClient
from app.core.config import settings

client = AsyncMongoClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]