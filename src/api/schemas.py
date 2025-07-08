from pydantic import BaseModel
from typing import Optional, Dict, Any

class WebSocketMessage(BaseModel):
    type: str  # "message", "financial_data", "init"
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class InitData(BaseModel):
    name: str
    investment_portfolio: Dict[str, Any] = {}
    risk_level: str = "moderate"
