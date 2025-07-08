# Financial Chatbot Backend

A production-ready, AI-powered financial chatbot backend built with FastAPI, MongoDB, and LangChain. This system provides personalized financial advice, real-time market data, and interactive chat capabilities through WebSocket connections.

## 🚀 Features

- **Real-time Chat**: WebSocket-based chat interface for instant communication
- **AI-Powered Advice**: Integration with OpenAI GPT-4 for intelligent financial guidance
- **Memory Management**: Conversation history and context using LangChain
- **Financial Tools**: Stock analysis, market data, currency conversion
- **User Management**: User profiles with personalized risk preferences
- **Session Management**: Persistent chat sessions with message history
- **Layered Architecture**: Clean separation of concerns with proper abstraction
- **Production Ready**: Docker support, Azure deployment, CI/CD pipeline

## 🏗️ Architecture

### Layered Architecture
```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│            (API Routes)             │
├─────────────────────────────────────┤
│          Business Logic Layer       │
│     (Financial Logic, AI Integration)│
├─────────────────────────────────────┤
│            Service Layer            │
│    (User Service, Financial Service)│
├─────────────────────────────────────┤
│             Data Layer              │
│    (Database, Financial Tools)      │
└─────────────────────────────────────┘
```

### Project Structure
```
chatbot-financial/
├── .github/workflows/
│   └── deploy.yml              # CI/CD pipeline
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── api/                    # Presentation Layer
│   │   ├── routes.py          # API endpoints and WebSocket handlers
│   │   └── schemas.py         # Pydantic models for API
│   ├── business_logic/         # Business Logic Layer
│   │   ├── financial_logic.py # Financial decision logic
│   │   └── ai_integration.py  # LangChain and AI integration
│   ├── data/                   # Data Layer
│   │   ├── database.py        # MongoDB connection and operations
│   │   └── financial_tools.py # Financial data tools (Yahoo Finance)
│   ├── services/               # Service Layer
│   │   ├── user_service.py    # User and session management
│   │   └── financial_service.py # Financial data services
│   └── models/                 # Data Models
│       ├── user_model.py      # User and chat models
│       └── financial_model.py # Financial state models
├── docker-compose.yml          # Local development setup
├── Dockerfile                  # Container configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (async Python)
- **Database**: MongoDB with Motor (async driver)
- **AI/ML**: LangChain, OpenAI GPT-4
- **Financial Data**: Yahoo Finance API (yfinance)
- **WebSocket**: FastAPI WebSocket support
- **Memory**: LangChain ConversationSummaryMemory
- **Containerization**: Docker, Docker Compose
- **Deployment**: Azure Container Apps
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- OpenAI API key
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-chatbot
   ```

2. **Set up environment variables**
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   ENVIRONMENT=development
   PORT=8000
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=financial_chatbot
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Install dependencies (for local development)**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   cd src
   python main.py
   ```

6. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

## 📚 API Documentation

### Core Endpoints

#### User Management
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user details
- `POST /api/v1/users/{user_id}/sessions` - Create chat session
- `GET /api/v1/users/{user_id}/sessions` - List user sessions

#### Financial Data
- `POST /api/v1/financial/stock-analysis` - Get stock analysis
- `GET /api/v1/financial/market-overview` - Get market overview
- `POST /api/v1/financial/currency-conversion` - Currency conversion

#### WebSocket
- `WS /api/v1/ws/chat/{session_id}?user_id={user_id}` - Real-time chat

### WebSocket Message Format

**Client to Server:**
```json
{
  "type": "message",
  "content": "What's the current price of AAPL?"
}
```

**Server to Client:**
```json
{
  "type": "message",
  "content": "The current price of AAPL is $150.25",
  "is_user": false,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🤖 AI Integration

### Conversation Flow
1. **User Message**: Received via WebSocket
2. **State Management**: Financial state updated with user context
3. **AI Processing**: LangChain processes message with memory context
4. **Tool Calling**: Financial tools called if needed (stock prices, etc.)
5. **Response Generation**: AI generates personalized response
6. **Memory Update**: Conversation history updated

### Financial Tools Available
- **Stock Analysis**: Real-time stock prices, company info, dividends
- **Market Data**: Major indices (S&P 500, Dow Jones, NASDAQ)
- **Currency Conversion**: Real-time exchange rates
- **Portfolio Analysis**: Risk-based recommendations
- **Budgeting Advice**: Personalized budget recommendations

### Bot Personalities
The system supports different bot personalities configured via environment variables:
- `financial_advisor`: Conservative, professional advice
- `investment_coach`: Growth-focused, educational approach
- `budget_helper`: Practical, savings-focused guidance

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | development |
| `PORT` | Server port | 8000 |
| `MONGODB_URL` | MongoDB connection string | mongodb://localhost:27017 |
| `DATABASE_NAME` | Database name | financial_chatbot |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `SECRET_KEY` | Application secret key | Required |
| `BOT_PERSONALITY` | Bot personality type | financial_advisor |
| `DEFAULT_RISK_LEVEL` | Default user risk level | moderate |

## 🚢 Deployment

### Azure Container Apps

1. **Set up Azure resources**
   ```bash
   # Create resource group
   az group create --name financial-chatbot-rg --location eastus

   # Create container app environment
   az containerapp env create --name financial-chatbot-env --resource-group financial-chatbot-rg --location eastus
   ```

2. **Configure GitHub Secrets**
   Add these secrets to your GitHub repository:
   - `AZURE_CREDENTIALS`
   - `AZURE_REGISTRY_USERNAME`
   - `AZURE_REGISTRY_PASSWORD`
   - `MONGODB_URL` (MongoDB Atlas connection string)
   - `OPENAI_API_KEY`
   - `SECRET_KEY`

3. **Deploy via GitHub Actions**
   Push to main branch to trigger automatic deployment.

### Manual Docker Deployment

```bash
# Build image
docker build -t financial-chatbot .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e MONGODB_URL=your_mongodb_url \
  financial-chatbot
```

## 🧪 Testing

### API Testing with curl

**Create a user:**
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "preferred_risk_level": "moderate"
  }'
```

**Get stock analysis:**
```bash
curl -X POST "http://localhost:8000/api/v1/financial/stock-analysis" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### WebSocket Testing

Use a WebSocket client to connect to:
```
ws://localhost:8000/api/v1/ws/chat/{session_id}?user_id={user_id}
```

## 📊 Monitoring

### Health Checks
- **Endpoint**: `GET /api/v1/health`
- **Docker Health Check**: Built-in container health monitoring
- **Active Connections**: `GET /api/v1/admin/connections`

### Logging
Application logs are structured and include:
- Request/response logs
- Error handling
- WebSocket connection events
- AI processing steps

## 🔒 Security

### Production Security Measures
- Environment-based configuration
- Non-root container user
- CORS configuration
- Input validation with Pydantic
- Secure WebSocket connections
- API rate limiting (implement as needed)

## 🤝 Contributing

### Development Guidelines
1. Follow the layered architecture pattern
2. Use type hints throughout
3. Implement proper error handling
4. Add logging for debugging
5. Write comprehensive tests
6. Update documentation

### Adding New Financial Tools
1. Create tool function in `src/data/financial_tools.py`
2. Add tool to AI integration in `src/business_logic/ai_integration.py`
3. Update business logic in `src/business_logic/financial_logic.py`
4. Add API endpoint if needed

### Adding New Bot Personalities
1. Update environment configuration
2. Modify system prompts in `src/business_logic/ai_integration.py`
3. Add personality-specific logic in business layer
4. Update documentation

## 📝 Memory System

### LangChain Integration
- **ConversationSummaryMemory**: Maintains conversation context
- **Automatic Summarization**: Reduces memory usage for long conversations
- **Persistent Storage**: Chat history stored in MongoDB
- **Context Retrieval**: Previous conversations inform current responses

### Memory Management
- Memory reset per session
- Summary generation every 2 messages
- Context preservation across WebSocket reconnections

## 🐛 Troubleshooting

### Common Issues

**Docker Connection Issues:**
```bash
# Reset Docker environment
docker-compose down -v
docker-compose up -d
```

**MongoDB Connection:**
- Check MongoDB URL in environment variables
- Ensure MongoDB service is running
- Verify network connectivity

**OpenAI API Issues:**
- Verify API key is correct
- Check API quota and usage
- Ensure model access permissions

**WebSocket Connection:**
- Check CORS configuration
- Verify user and session IDs
- Monitor server logs for errors

## 📋 Roadmap

### Upcoming Features
- [ ] Advanced portfolio analytics
- [ ] Real-time news integration
- [ ] Multi-language support
- [ ] Voice chat capabilities
- [ ] Advanced risk assessment
- [ ] Regulatory compliance features
- [ ] Mobile app integration
- [ ] Advanced charting and visualization

### Performance Improvements
- [ ] Redis caching layer
- [ ] Database indexing optimization
- [ ] API response compression
- [ ] Load balancing support
- [ ] Horizontal scaling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation for common solutions
- Review the troubleshooting section

---

**Built with ❤️ for financial empowerment**
