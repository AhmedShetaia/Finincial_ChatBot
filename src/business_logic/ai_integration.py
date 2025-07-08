from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
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
        # Set Azure OpenAI endpoint
        self.model = AzureChatOpenAI(
            deployment_name="gpt-4",
            temperature=0.7,
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        # Initialize memory
        self.chat_history = InMemoryChatMessageHistory()
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
                content="""You are a helpful and conversational financial assistant named FinBot. You should:

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
            
            # Use business logic to determine if tools are needed
            logic_response = FinancialLogic.process_financial_request(current_state, user_message)
            
            # Always use the AI model to generate responses, but check if tools are needed
            if logic_response.get("requires_tools", False):
                # For tool-requiring responses, use the graph
                final_state = await self.graph.ainvoke(current_state)
                final_response = final_state["messages"][-1].content if final_state["messages"] else "I'm sorry, I couldn't process your request."
                
                return {
                    "response": final_response,
                    "action": logic_response["action"],
                    "state": final_state
                }
            else:
                # For responses that don't need tools, still use the AI model but skip graph
                model_response = self._model_call(current_state)
                ai_response = model_response["messages"][0] if model_response["messages"] else AIMessage(content="I'm sorry, I couldn't process your request.")
                
                # Update state with the AI response
                current_state["messages"].append(ai_response)
                
                return {
                    "response": ai_response.content,
                    "action": logic_response["action"],
                    "state": current_state
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
