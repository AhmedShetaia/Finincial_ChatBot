from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "financial_chatbot")
    
    db.client = AsyncIOMotorClient(
        mongodb_url,
        server_api=ServerApi('1')
    )
    db.database = db.client[db_name]
    
    # Test the connection
    try:
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()

async def get_collection(collection_name: str):
    """Get a collection from the database"""
    database = await get_database()
    return database[collection_name]
