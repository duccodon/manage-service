from motor.motor_asyncio import AsyncIOMotorClient
from app.configs import config

client = AsyncIOMotorClient(config.MONGO_URI)

database = client[config.MONGODB_NAME]  # Database name
location_collection = database.get_collection(config.LOCATION_COLLECTION)
notification_collection = database.get_collection(config.NOTIFICATION_COLLECTION)
