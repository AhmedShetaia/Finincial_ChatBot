from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
from datetime import datetime

from api.schemas import WebSocketMessage
from business_logic.ai_integration import AIIntegration
from business_logic.financial_logic import FinancialLogic
from models.financial_model import FinancialState

router = APIRouter()

# In-memory storage for active WebSocket connections and chat sessions
active_connections: Dict[str, WebSocket] = {}
chat_sessions: Dict[str, FinancialState] = {}

# AI Integration instance
ai_integration = AIIntegration()

# WebSocket endpoint for real-time chat
@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    connection_id = None
    financial_state = None
    
    try:
        # Wait for initial user info
        data = await websocket.receive_text()
        init_data = json.loads(data)
        
        if init_data.get("type") != "init":
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": "First message must be initialization data"
            }))
            await websocket.close()
            return
        
        # Extract user info
        user_info = init_data.get("data", {})
        name = user_info.get("name", "User")
        investment_portfolio = user_info.get("investment_portfolio", {})
        risk_level = user_info.get("risk_level", "moderate")
        
        # Generate connection ID
        connection_id = f"user_{datetime.utcnow().timestamp()}"
        
        # Store connection
        active_connections[connection_id] = websocket
        
        # Create financial state
        financial_state = FinancialState(
            name=name,
            preferred_risk_level=risk_level,
            investment_portfolio=investment_portfolio,
            income=None,
            expenses=None,
            financial_goals=None,
            budgeting_details=None,
            messages=[]
        )
        
        # Store session
        chat_sessions[connection_id] = financial_state
        
        # Send welcome message
        welcome_msg = {
            "type": "message",
            "content": f"Hello {name}! I'm your financial assistant. How can I help you today?",
            "is_user": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["content"]
                
                # Process message with AI
                response = await ai_integration.process_message(financial_state, user_message)
                
                # Update state
                financial_state = response["state"]
                chat_sessions[connection_id] = financial_state
                
                # Send AI response
                ai_response = {
                    "type": "message",
                    "content": response["response"],
                    "is_user": False,
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": response["action"]
                }
                await websocket.send_text(json.dumps(ai_response))
                
            elif message_data["type"] == "financial_data":
                # Update financial state with new data
                financial_data = message_data["content"]
                financial_state.update(financial_data)
                chat_sessions[connection_id] = financial_state
                
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
                
                elif message_data.get("data_type") == "portfolio":
                    advice = FinancialLogic.generate_portfolio_advice(financial_state)
                    response_msg = {
                        "type": "message",
                        "content": advice,
                        "is_user": False,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_text(json.dumps(response_msg))
                
    except WebSocketDisconnect:
        # Clean up when client disconnects
        if connection_id:
            if connection_id in active_connections:
                del active_connections[connection_id]
            if connection_id in chat_sessions:
                del chat_sessions[connection_id]
        print(f"Client {connection_id} disconnected")
    
    except Exception as e:
        error_msg = {
            "type": "error",
            "content": f"An error occurred: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(error_msg))
        print(f"Error in WebSocket connection {connection_id}: {str(e)}")
        
        # Clean up on error
        if connection_id:
            if connection_id in active_connections:
                del active_connections[connection_id]
            if connection_id in chat_sessions:
                del chat_sessions[connection_id]

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
        "connection_ids": list(active_connections.keys()),
        "active_sessions": len(chat_sessions)
    }
