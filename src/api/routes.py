from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from src.api.schemas import (
    UserCreate, UserResponse, ChatSessionCreate, ChatSessionResponse,
    ChatMessageRequest, ChatMessageResponse, FinancialDataRequest,
    StockAnalysisRequest, MarketDataResponse, CurrencyConversionRequest,
    WebSocketMessage
)
from src.services.user_service import UserService
from src.services.financial_service import FinancialService
from src.business_logic.ai_integration import AIIntegration
from src.business_logic.financial_logic import FinancialLogic
from src.models.financial_model import FinancialState

router = APIRouter()

# In-memory storage for active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# AI Integration instance
ai_integration = AIIntegration()

# User management endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_id = await UserService.create_user(user.dict())
        created_user = await UserService.get_user(user_id)
        return UserResponse(**created_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)

@router.post("/users/{user_id}/sessions", response_model=ChatSessionResponse)
async def create_chat_session(user_id: str, session: ChatSessionCreate):
    """Create a new chat session for a user"""
    try:
        session_id = await UserService.create_chat_session(user_id, session.session_name)
        return ChatSessionResponse(
            id=session_id,
            user_id=user_id,
            session_name=session.session_name,
            is_active=True
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(user_id: str):
    """Get all chat sessions for a user"""
    sessions = await UserService.get_user_sessions(user_id)
    return [ChatSessionResponse(**session) for session in sessions]

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(session_id: str):
    """Get all messages for a chat session"""
    messages = await UserService.get_session_messages(session_id)
    return [ChatMessageResponse(**message) for message in messages]

# Financial data endpoints
@router.post("/financial/stock-analysis")
async def get_stock_analysis(request: StockAnalysisRequest):
    """Get stock analysis for a ticker"""
    try:
        analysis = await FinancialService.get_stock_analysis(request.ticker)
        return JSONResponse(content=analysis)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/financial/market-overview")
async def get_market_overview():
    """Get market overview"""
    try:
        market_data = await FinancialService.get_market_overview()
        return JSONResponse(content={
            "data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/financial/currency-conversion")
async def get_currency_conversion(request: CurrencyConversionRequest):
    """Get currency conversion rates"""
    try:
        rates = await FinancialService.get_currency_rates(
            request.from_currency, 
            [request.to_currency]
        )
        return JSONResponse(content=rates)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# WebSocket endpoint for real-time chat
@router.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Store the connection
    connection_id = f"{session_id}_{user_id}"
    active_connections[connection_id] = websocket
    
    # Initialize financial state
    user_data = await UserService.get_user(user_id)
    if not user_data:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": "User not found"
        }))
        await websocket.close()
        return
    
    # Create initial state
    financial_state = FinancialState(
        name=user_data.get("name", ""),
        preferred_risk_level=user_data.get("preferred_risk_level", "moderate"),
        investment_portfolio=user_data.get("investment_portfolio", {}),
        income=None,
        expenses=None,
        financial_goals=None,
        budgeting_details=None,
        messages=[]
    )
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "message",
            "content": f"Hello {financial_state['name']}! I'm your financial assistant. How can I help you today?",
            "is_user": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # Save welcome message
        await UserService.add_message(session_id, user_id, welcome_msg["content"], False)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["content"]
                
                # Save user message
                await UserService.add_message(session_id, user_id, user_message, True)
                
                # Process message with AI
                response = await ai_integration.process_message(financial_state, user_message)
                
                # Update state
                financial_state = response["state"]
                
                # Send AI response
                ai_response = {
                    "type": "message",
                    "content": response["response"],
                    "is_user": False,
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": response["action"]
                }
                await websocket.send_text(json.dumps(ai_response))
                
                # Save AI response
                await UserService.add_message(session_id, user_id, response["response"], False)
                
            elif message_data["type"] == "financial_data":
                # Update financial state with new data
                financial_data = message_data["content"]
                financial_state.update(financial_data)
                
                # Generate appropriate response
                if message_data.get("data_type") == "budgeting":
                    advice = FinancialLogic.generate_budgeting_advice(financial_state)
                    response_msg = {
                        "type": "message",
                        "content": advice,
                        "is_user": False,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_text(json.dumps(response_msg))
                    await UserService.add_message(session_id, user_id, advice, False)
                
                elif message_data.get("data_type") == "portfolio":
                    advice = FinancialLogic.generate_portfolio_advice(financial_state)
                    response_msg = {
                        "type": "message",
                        "content": advice,
                        "is_user": False,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_text(json.dumps(response_msg))
                    await UserService.add_message(session_id, user_id, advice, False)
                
    except WebSocketDisconnect:
        # Remove connection when client disconnects
        if connection_id in active_connections:
            del active_connections[connection_id]
        print(f"Client {connection_id} disconnected")
    
    except Exception as e:
        error_msg = {
            "type": "error",
            "content": f"An error occurred: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(error_msg))
        print(f"Error in WebSocket connection {connection_id}: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Get active connections (for monitoring)
@router.get("/admin/connections")
async def get_active_connections():
    """Get number of active WebSocket connections"""
    return {
        "active_connections": len(active_connections),
        "connection_ids": list(active_connections.keys())
    }
