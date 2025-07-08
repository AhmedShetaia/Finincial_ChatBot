from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    preferred_risk_level: str
    investment_portfolio: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class ChatSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    session_name: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_active: bool = True

class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    user_id: str
    message: str
    is_user: bool
    timestamp: datetime = datetime.utcnow()
