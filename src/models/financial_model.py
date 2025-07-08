from typing import TypedDict, Optional, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class FinancialState(TypedDict):
    # Permanent state
    name: str
    preferred_risk_level: str
    investment_portfolio: dict
    
    # Temporary state
    income: Optional[float]
    expenses: Optional[float]
    financial_goals: Optional[dict]
    budgeting_details: Optional[dict]
    
    # Conversation history
    messages: Annotated[Sequence[BaseMessage], add_messages]
