from typing import List, Dict, Any, Optional
from models.user_model import User, ChatSession, ChatMessage
from data.database import get_collection
from bson import ObjectId
from datetime import datetime

class UserService:
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        collection = await get_collection("users")
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        result = await collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        collection = await get_collection("users")
        user = await collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user["_id"])
            del user["_id"]
        return user
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        collection = await get_collection("users")
        user = await collection.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            del user["_id"]
        return user
    
    @staticmethod
    async def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        collection = await get_collection("users")
        update_data["updated_at"] = datetime.utcnow()
        result = await collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def create_chat_session(user_id: str, session_name: str) -> str:
        """Create a new chat session"""
        collection = await get_collection("chat_sessions")
        session_data = {
            "user_id": user_id,
            "session_name": session_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        result = await collection.insert_one(session_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user"""
        collection = await get_collection("chat_sessions")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
        sessions = []
        async for session in cursor:
            session["id"] = str(session["_id"])
            del session["_id"]
            sessions.append(session)
        return sessions
    
    @staticmethod
    async def add_message(session_id: str, user_id: str, message: str, is_user: bool) -> str:
        """Add a message to a chat session"""
        collection = await get_collection("chat_messages")
        message_data = {
            "session_id": session_id,
            "user_id": user_id,
            "message": message,
            "is_user": is_user,
            "timestamp": datetime.utcnow()
        }
        result = await collection.insert_one(message_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a chat session"""
        collection = await get_collection("chat_messages")
        cursor = collection.find({"session_id": session_id}).sort("timestamp", 1)
        messages = []
        async for message in cursor:
            message["id"] = str(message["_id"])
            del message["_id"]
            messages.append(message)
        return messages
