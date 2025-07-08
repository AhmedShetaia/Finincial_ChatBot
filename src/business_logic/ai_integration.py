from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from models.financial_model import FinancialState
from data.financial_tools import (
    fetch_stock_price, fetch_historical_data, fetch_dividends,
    fetch_market_data, fetch_currency_conversion, fetch_company_info
)
from business_logic.financial_logic import FinancialLogic
import os
from typing import Dict, Any

class AIIntegration:
    def __init__(self):
        # Initialize Azure OpenAI model
        self.model = AzureChatOpenAI(
            deployment_name="gpt-4.1",
            temperature=0.7,
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        # Setup tools
        self.tools = [
            fetch_stock_price, fetch_historical_data, fetch_dividends,
            fetch_market_data, fetch_currency_conversion, fetch_company_info
        ]

        # Bind tools to the model
        self.model_with_tools = self.model.bind_tools(self.tools)

        # Initialize checkpointer for memory
        self.checkpointer = InMemorySaver()

        # Create the workflow graph
        self.graph = self._create_workflow_graph()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow using best practices"""
        # Create tool node
        tool_node = ToolNode(self.tools)
        
        # Create state graph
        graph = StateGraph(FinancialState)
        
        # Add nodes
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", tool_node)
        
        # Set entry point
        graph.set_entry_point("agent")
        
        # Add conditional edges using tools_condition
        graph.add_conditional_edges(
            "agent",
            tools_condition,
        )
        
        # Add edge from tools back to agent
        graph.add_edge("tools", "agent")
        
        # Compile with checkpointer
        return graph.compile(checkpointer=self.checkpointer)
    
    def _agent_node(self, state: FinancialState) -> Dict[str, Any]:
        """Main agent node that handles all conversation logic"""
        try:
            messages = state.get("messages", [])
            
            # Add system prompt if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                system_prompt = SystemMessage(
                    content="""You are FinBot, a helpful and conversational financial assistant. You should:

1. Always respond directly to the user's question or message
2. Be friendly, conversational, and personable
3. Provide helpful financial advice and information
4. Ask follow-up questions when you need more details
5. Explain financial concepts in simple terms
6. Use the available tools when users ask for specific financial data like stock prices, market data, etc.
7. Provide personalized advice based on user's risk tolerance and financial goals when known
8. Always remind users that this is general guidance and they should consult professional advisors for major financial decisions

Available capabilities:
- Stock analysis and market data
- Investment advice and portfolio planning  
- Budgeting and financial planning
- Currency conversion
- Market insights
- General financial education

Respond naturally to whatever the user says, whether it's a greeting, question, or request for help."""
                )
                messages = [system_prompt] + messages
            
            # Call the model with tools
            response = self.model_with_tools.invoke(messages)
            
            return {"messages": [response]}
            
        except Exception as e:
            error_message = AIMessage(
                content=f"I apologize, but I encountered an error: {str(e)}. Please try again."
            )
            return {"messages": [error_message]}
    
    async def process_message(self, user_message: str, thread_id: str = "default") -> Dict[str, Any]:
        """Process a user message and return response"""
        try:
            # Create initial state with user message
            initial_state = {
                "messages": [HumanMessage(content=user_message)]
            }
            
            # Create config for this conversation thread
            config = {"configurable": {"thread_id": thread_id}}
            
            # Use business logic to determine response type
            logic_response = FinancialLogic.process_financial_request(initial_state, user_message)
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # Get the final AI response
            if final_state.get("messages"):
                final_response = final_state["messages"][-1]
                if hasattr(final_response, 'content'):
                    response_content = final_response.content
                else:
                    response_content = str(final_response)
            else:
                response_content = "I'm sorry, I couldn't process your request."
            
            return {
                "response": response_content,
                "action": logic_response.get("action", "general_response"),
                "state": final_state
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "action": "error",
                "state": {"messages": []}
            }
    
    def reset_memory(self, thread_id: str = "default"):
        """Reset the conversation memory for a specific thread"""
        try:
            # Clear the checkpointer for this thread
            config = {"configurable": {"thread_id": thread_id}}
            # Note: InMemorySaver doesn't have a direct clear method for specific threads
            # For production, consider using a different checkpointer like PostgresSaver
            pass
        except Exception as e:
            print(f"Error resetting memory: {e}")
    
    def get_memory_summary(self, thread_id: str = "default") -> str:
        """Get current memory summary for a thread"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            # Get the current state from checkpointer
            current_state = self.graph.get_state(config)
            if current_state and current_state.values.get("messages"):
                return f"Conversation has {len(current_state.values['messages'])} messages"
            return "No conversation history available."
        except Exception as e:
            return f"Error retrieving memory: {e}"
