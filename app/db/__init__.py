from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

MONGO_URI = settings.MONGO_DB_URL
client = AsyncIOMotorClient(MONGO_URI)
db = client[settings.MONGO_DB_NAME]