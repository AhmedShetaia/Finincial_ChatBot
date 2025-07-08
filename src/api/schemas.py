from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class UserCreate(BaseModel):
    name: str
    email: str
    preferred_risk_level: str
    investment_portfolio: Dict[str, Any] = {}

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    preferred_risk_level: str
    investment_portfolio: Dict[str, Any]

class ChatSessionCreate(BaseModel):
    session_name: str

class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    session_name: str
    is_active: bool

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    user_id: str
    message: str
    is_user: bool

class FinancialDataRequest(BaseModel):
    income: Optional[float] = None
    expenses: Optional[float] = None
    financial_goals: Optional[Dict[str, Any]] = None
    budgeting_details: Optional[Dict[str, Any]] = None

class StockAnalysisRequest(BaseModel):
    ticker: str

class MarketDataResponse(BaseModel):
    data: Dict[str, Any]
    timestamp: str

class CurrencyConversionRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: Optional[float] = 1.0

class WebSocketMessage(BaseModel):
    type: str  # "message", "financial_data", "session_info"
    content: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
