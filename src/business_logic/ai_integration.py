from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain_core.chat_history import ChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.models.financial_model import FinancialState
from src.data.financial_tools import (
    fetch_stock_price, fetch_historical_data, fetch_dividends,
    fetch_market_data, fetch_currency_conversion, fetch_company_info
)
from src.business_logic.financial_logic import FinancialLogic
import os
from typing import Dict, Any

class AIIntegration:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize memory
        self.chat_history = ChatMessageHistory()
        self.memory = ConversationSummaryMemory(
            llm=self.model,
            chat_memory=self.chat_history,
            summarize_step=2
        )
        
        # Setup tools
        self.tools = [
            fetch_stock_price, fetch_historical_data, fetch_dividends,
            fetch_market_data, fetch_currency_conversion, fetch_company_info
        ]
        
        # Create the workflow graph
        self.graph = self._create_workflow_graph()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        tool_node = ToolNode(self.tools)
        
        graph = StateGraph(FinancialState)
        graph.add_node("agent", self._model_call)
        graph.add_node("tools", tool_node)
        
        graph.set_entry_point("agent")
        
        # Add conditional edges
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        graph.add_edge("tools", "agent")
        
        return graph.compile()
    
    def _model_call(self, state: FinancialState) -> Dict[str, Any]:
        """Handle model calls with memory and context"""
        try:
            # Get memory summary for context
            memory_summary = self.memory.load_memory_variables({})
            
            # Create system prompt
            system_prompt = SystemMessage(
                content="""You are a helpful financial assistant. You can help users with:
                - Stock analysis and market data
                - Investment advice and portfolio planning
                - Budgeting and financial planning
                - Currency conversion
                - Market insights
                
                Use the available tools when users ask for specific financial data.
                Provide personalized advice based on user's risk tolerance and financial goals.
                Always remind users that this is general guidance and they should consult professional advisors for major financial decisions."""
            )
            
            # Prepare messages
            messages = [system_prompt]
            
            # Add memory context if available
            if memory_summary.get("history"):
                context_message = SystemMessage(content=f"Previous conversation context: {memory_summary['history']}")
                messages.append(context_message)
            
            # Add conversation messages
            messages.extend(state["messages"])
            
            # Get model response
            response = self.model.invoke(messages)
            
            # Save to memory
            if state["messages"]:
                self.memory.save_context(
                    {"input": state["messages"][-1].content},
                    {"output": response.content}
                )
            
            return {"messages": [response]}
            
        except Exception as e:
            error_message = AIMessage(content=f"I apologize, but I encountered an error: {str(e)}. Please try again.")
            return {"messages": [error_message]}
    
    def _should_continue(self, state: FinancialState) -> str:
        """Determine if the workflow should continue to tools or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    async def process_message(self, state: FinancialState, user_message: str) -> Dict[str, Any]:
        """Process a user message and return response"""
        try:
            # Add user message to state
            human_message = HumanMessage(content=user_message)
            current_state = dict(state)
            current_state["messages"] = state.get("messages", []) + [human_message]
            
            # Use business logic to determine response type
            logic_response = FinancialLogic.process_financial_request(current_state, user_message)
            
            # If it's a simple response that doesn't need tools, return directly
            if not logic_response.get("requires_tools", False):
                ai_response = AIMessage(content=logic_response["response"])
                
                # Save to memory
                self.memory.save_context(
                    {"input": user_message},
                    {"output": ai_response.content}
                )
                
                return {
                    "response": ai_response.content,
                    "action": logic_response["action"],
                    "state": current_state
                }
            
            # For tool-requiring responses, use the graph
            final_state = await self.graph.ainvoke(current_state)
            
            # Get the final response
            final_response = final_state["messages"][-1].content if final_state["messages"] else "I'm sorry, I couldn't process your request."
            
            return {
                "response": final_response,
                "action": logic_response["action"],
                "state": final_state
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "action": "error",
                "state": state
            }
    
    def reset_memory(self):
        """Reset the conversation memory"""
        self.chat_history.clear()
        self.memory.clear()
    
    def get_memory_summary(self) -> str:
        """Get current memory summary"""
        summary = self.memory.load_memory_variables({})
        return summary.get("history", "No conversation history available.")
