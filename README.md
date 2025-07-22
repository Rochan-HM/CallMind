# CallMind 📞

CallMind is an intelligent voice call transcription and search system that automatically records, transcribes, and stores phone conversations in a searchable vector database. It provides both REST API access and Model Context Protocol (MCP) integration for AI agents to query call transcriptions.

## 🚀 What It Does

- **Automatic Call Recording**: Handles incoming Twilio voice calls and records them with real-time transcription
- **Intelligent Storage**: Stores transcriptions in ChromaDB with vector embeddings for semantic search
- **Smart Search**: Search through call transcriptions using natural language queries
- **AI Integration**: Provides MCP server for AI agents to access conversation history
- **REST API**: Full REST endpoints for searching recent and historical call transcriptions

## 🛠️ Tech Stack

### Backend & APIs
- **FastAPI** - Modern Python web framework for the main API server
- **Twilio Voice API** - Voice call handling, recording, and transcription
- **ChromaDB** - Vector database for storing and searching transcriptions
- **FastMCP** - Model Context Protocol server for AI agent integration

### AI & Embeddings
- **Google Generative AI** - Embedding generation for semantic search
- **Vector Search** - Semantic similarity search through call transcriptions

### Development & Deployment
- **Python 3.13+** - Modern Python runtime
- **uv** - Fast Python package manager and project management
- **poethepoet (poe)** - Task runner for development commands
- **Docker** - Containerized deployment
- **python-dotenv** - Environment variable management

## 📋 Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Twilio account with Voice API access
- ChromaDB cloud account
- Google AI API key for embeddings

## ⚙️ Setup

### 1. Install Dependencies

First, install `uv` if you haven't already:
```bash
brew install uv  # macOS
# or
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Windows
```

Install the project dependencies:
```bash
uv sync
```

### 2. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
BASE_URL=https://your-domain.com  # Your server's public URL for webhooks

# ChromaDB Configuration  
CHROMA_API_KEY=your_chromadb_api_key
CHROMA_TENANT=your_chromadb_tenant

# Google AI Configuration
GEMINI_API_KEY=your_google_ai_api_key
```

### 3. Twilio Webhook Setup

Configure your Twilio phone number to send webhooks to your server:
- **Voice URL**: `https://your-domain.com/webhooks/voice`
- **Voice Method**: `POST`

## 🚀 Running the Services

The project includes multiple services that can be run independently:

### Twilio Server (Main API)
```bash
uv run python twilio_server/app.py
```
The main FastAPI server will start on `http://localhost:8000`

### MCP Server (AI Integration)
```bash
uv run poe run_mcp_server
```
The MCP server will start on `http://localhost:9000`

### Docker Deployment
```bash
docker build -t callmind .
docker run -p 9000:9000 --env-file .env callmind
```

## 📖 API Documentation

### Main Endpoints

- **GET** `/` - Health check
- **GET** `/health` - Configuration status
- **POST** `/webhooks/voice` - Twilio voice webhook (handles incoming calls)
- **POST** `/webhooks/transcription` - Twilio transcription webhook
- **POST** `/webhooks/recording-complete` - Recording completion webhook
- **GET** `/transcriptions/search` - Search transcriptions
- **GET** `/transcriptions/recent` - Get recent transcriptions

### Search Transcriptions
```bash
curl "http://localhost:8000/transcriptions/search?query=meeting&n_results=5"
```

### Get Recent Transcriptions
```bash
curl "http://localhost:8000/transcriptions/recent?limit=10"
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🤖 MCP Integration

The MCP server provides AI agents with access to call transcriptions through the Model Context Protocol:

```python
# MCP Tool: query_collection
# Search for relevant transcripts based on natural language queries
```

AI agents can use this to:
- Search conversation history
- Find specific topics discussed in calls
- Retrieve context for follow-up conversations

## 🔄 How It Works

1. **Incoming Call**: Twilio receives a call and sends a webhook to `/webhooks/voice`
2. **Call Handling**: The server responds with TwiML to record the call with transcription
3. **Recording**: Twilio records the call and generates a transcription
4. **Storage**: Transcription is sent to `/webhooks/transcription` and stored in ChromaDB
5. **Search**: Users can search transcriptions via REST API or AI agents via MCP

## 🏗️ Project Structure

```
CallMind/
├── twilio_server/          # Main FastAPI application
│   └── app.py             # Twilio webhooks and search endpoints
├── mcp_server/            # Model Context Protocol server
│   └── callmind_mcp.py   # MCP integration for AI agents
├── chromadb_utils/        # Database utilities
│   └── utils.py          # ChromaDB connection and operations
├── infobip/              # Additional integrations (future)
├── pyproject.toml        # Project dependencies and configuration
├── Dockerfile           # Container deployment
└── README.md           # This file
```

## 🛡️ Security Considerations

- Store all API keys and sensitive credentials in environment variables
- Use HTTPS for all webhook endpoints in production
- Validate Twilio webhook signatures (recommended for production)
- Implement rate limiting for public endpoints
- Consider encryption for stored transcriptions containing sensitive information

## 🔧 Development

### Available Tasks
```bash
uv run poe run_twilio_server    # Start Twilio server
uv run poe run_mcp_server       # Start MCP server
```

### Adding Dependencies
```bash
uv add package_name
```

### Environment Activation
```bash
uv shell  # Activate virtual environment
```
