from models.financial_model import FinancialState
from services.financial_service import FinancialService
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List, Dict, Any

class FinancialLogic:
    @staticmethod
    def process_financial_request(state: FinancialState, user_message: str) -> Dict[str, Any]:
        """Process user's financial request and determine appropriate response"""
        
        # Check if we need to collect missing information first
        missing_info_response = FinancialService.collect_financial_info(state)
        
        # If we have missing information, return the request for info
        if "missing information" in missing_info_response.content.lower():
            return {
                "response": missing_info_response.content,
                "action": "collect_info",
                "requires_tools": False
            }
        
        # Analyze the user message to determine what financial service they need
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ["stock", "ticker", "share", "equity"]):
            return {
                "response": "I'll help you with stock analysis. Please provide the ticker symbol.",
                "action": "stock_analysis",
                "requires_tools": True
            }
        
        elif any(keyword in message_lower for keyword in ["market", "index", "dow", "s&p", "nasdaq"]):
            return {
                "response": "Let me get you the current market overview.",
                "action": "market_overview",
                "requires_tools": True
            }
        
        elif any(keyword in message_lower for keyword in ["currency", "exchange", "conversion", "forex"]):
            return {
                "response": "I'll help you with currency conversion rates.",
                "action": "currency_rates",
                "requires_tools": True
            }
        
        elif any(keyword in message_lower for keyword in ["budget", "expense", "income", "saving"]):
            return {
                "response": "I'll help you with budgeting and financial planning.",
                "action": "budgeting_advice",
                "requires_tools": False
            }
        
        elif any(keyword in message_lower for keyword in ["portfolio", "investment", "diversify", "allocation"]):
            return {
                "response": "Let me help you with portfolio analysis and investment advice.",
                "action": "portfolio_advice",
                "requires_tools": False
            }
        
        else:
            return {
                "response": "I'm here to help with your financial needs. I can assist with stock analysis, market data, currency conversion, budgeting, and investment advice. What would you like to know?",
                "action": "general_help",
                "requires_tools": False
            }
    
    @staticmethod
    def generate_budgeting_advice(state: FinancialState) -> str:
        """Generate personalized budgeting advice based on user's financial state"""
        income = state.get("income", 0)
        expenses = state.get("expenses", 0)
        risk_level = state.get("preferred_risk_level", "moderate")
        
        if income <= 0:
            return "I need your monthly income information to provide budgeting advice."
        
        if expenses <= 0:
            return "I need your monthly expenses information to provide budgeting advice."
        
        savings_rate = (income - expenses) / income * 100
        
        advice = f"Based on your financial profile:\n\n"
        advice += f"Monthly Income: ${income:,.2f}\n"
        advice += f"Monthly Expenses: ${expenses:,.2f}\n"
        advice += f"Current Savings Rate: {savings_rate:.1f}%\n\n"
        
        if savings_rate < 10:
            advice += "⚠️ Your savings rate is below the recommended 10-20%. Consider:\n"
            advice += "• Reviewing and reducing non-essential expenses\n"
            advice += "• Looking for ways to increase income\n"
            advice += "• Creating a detailed budget to track spending\n"
        elif savings_rate < 20:
            advice += "✅ Good savings rate! Consider:\n"
            advice += "• Building an emergency fund (3-6 months of expenses)\n"
            advice += "• Starting to invest for long-term goals\n"
        else:
            advice += "🎉 Excellent savings rate! You're doing great!\n"
            advice += "• Consider maximizing retirement contributions\n"
            advice += "• Exploring investment opportunities\n"
            advice += "• Planning for major financial goals\n"
        
        return advice
    
    @staticmethod
    def generate_portfolio_advice(state: FinancialState) -> str:
        """Generate portfolio allocation advice based on user's risk profile"""
        risk_level = state.get("preferred_risk_level", "moderate").lower()
        portfolio = state.get("investment_portfolio", {})
        
        advice = f"Portfolio advice for {risk_level} risk investor:\n\n"
        
        if risk_level == "conservative":
            advice += "Recommended allocation:\n"
            advice += "• 60% Bonds/Fixed Income\n"
            advice += "• 30% Large Cap Stocks\n"
            advice += "• 10% Cash/Money Market\n\n"
            advice += "Focus on: Stability, capital preservation, dividend-paying stocks"
        
        elif risk_level == "aggressive":
            advice += "Recommended allocation:\n"
            advice += "• 80% Stocks (mix of large, mid, small cap)\n"
            advice += "• 15% International/Emerging Markets\n"
            advice += "• 5% Bonds\n\n"
            advice += "Focus on: Growth stocks, international diversification, higher potential returns"
        
        else:  # moderate
            advice += "Recommended allocation:\n"
            advice += "• 60% Stocks (large and mid cap)\n"
            advice += "• 30% Bonds\n"
            advice += "• 10% International/REITs\n\n"
            advice += "Focus on: Balanced growth and income, diversification"
        
        advice += f"\n\nCurrent portfolio: {portfolio if portfolio else 'No current holdings reported'}"
        advice += "\n\nRemember: This is general guidance. Consider consulting with a financial advisor for personalized advice."
        
        return advice
