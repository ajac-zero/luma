# Luma - AI-Powered Nonprofit Financial Intelligence

> Transforming millions of nonprofit tax filings into actionable insights — in hours, not weeks.

A full-stack application that combines intelligent document processing, vector search, and AI-powered analysis with a modern React frontend and FastAPI backend.

# The Problem

Every year, over 1.5 million U.S. nonprofits file IRS Form 990s — creating thousands of pages of critical financial and governance data.

While this information is technically public, it remains practically unusable for most professionals who need it.

Financial advisors, auditors, and philanthropic donors need quick access to reliable nonprofit data to make informed decisions.

Manual review is time-consuming, error-prone, and doesn't scale — leaving critical insights buried in paperwork.

Luma turns raw filings into actionable insights, powering smarter, faster, and more transparent decisions across the nonprofit sector.

## 🚀 Features

- **Document Processing**: Upload, chunk, and process PDFs with Azure Blob Storage
- **Vector Search**: Semantic search using Qdrant vector database and Azure OpenAI embeddings
- **AI Agents**: Multi-agent system with specialized capabilities:
  - **Form Auditor**: Automated document validation and compliance checking
  - **Analyst Agent**: Data analysis and insights generation
  - **Web Search Agent**: Real-time web search powered by Tavily API
- **Generative UI**: Dynamic React components generated from AI responses
- **Data Room Management**: Organized document storage and retrieval
- **Schema Management**: Flexible data structure definitions

## 🏗️ Architecture

```
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── agents/   # AI agent implementations
│   │   ├── core/     # Configuration and utilities
│   │   ├── models/   # Pydantic data models
│   │   ├── routers/  # API endpoints
│   │   └── main.py   # Application entry point
│   └── Dockerfile
├── frontend/         # React + TypeScript frontend
│   ├── src/
│   └── Dockerfile
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Azure OpenAI**: GPT-4 and embeddings via Azure
- **Azure Blob Storage**: Document storage
- **Qdrant**: Vector database for semantic search
- **Redis**: Caching and session management
- **Pydantic AI**: Agent framework with tool calling
- **Tavily**: Web search API integration

### Frontend
- **React 19**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **AI SDK**: Streaming AI responses and generative UI
- **Radix UI**: Accessible component primitives
- **Zustand**: State management

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (optional)

### Environment Setup

Create a `.env` file in the backend directory:

```env
# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_ACCOUNT_NAME=your_account_name
AZURE_CONTAINER_NAME=files
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-large
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_key

# Redis
REDIS_OM_URL=redis://localhost:6379

# Google Cloud (for Gemini)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1

# LandingAI Document Processing
LANDINGAI_API_KEY=your_landingai_key

# Web Search
TAVILY_API_KEY=your_tavily_key
```

### Backend Setup

```bash
cd backend
pip install -e .
uv run dev  # Development server with hot reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

The API provides comprehensive endpoints for document management and AI operations:

### Core Endpoints

- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `POST /api/v1/files` - Upload documents
- `GET /api/v1/files` - List documents
- `POST /api/v1/vectors/search` - Semantic search
- `POST /api/v1/chunking` - Process and chunk documents

### Agent Endpoints

- `POST /api/v1/agent/form-auditor` - Audit forms and documents
- `POST /api/v1/agent/analyst` - Analyze data and generate insights
- `POST /api/v1/agent/web-search` - Search web for current information

### Data Management

- `GET /api/v1/dataroom` - List data rooms
- `POST /api/v1/dataroom` - Create data room
- `GET /api/v1/schemas` - Schema management
- `POST /api/v1/extracted-data` - Store extracted data

## 🤖 AI Agents

### Form Auditor Agent
Validates documents against compliance requirements and business rules.

```python
# Example usage
response = await form_auditor.run(
    document_text="...",
    schema_requirements={"required_fields": ["name", "date"]}
)
```

### Analyst Agent
Performs data analysis and generates business insights.

```python
# Example usage
response = await analyst.run(
    data=financial_data,
    analysis_type="trend_analysis"
)
```

### Web Search Agent
Searches the web for up-to-date information using Tavily.

```python
# Example usage
response = await web_search.run(
    query="latest AI developments 2024",
    max_results=5
)
```

## 🔧 Development

### Running Tests
```bash
cd backend
python -m pytest

cd frontend
npm test
```

### Code Quality
```bash
# Backend
ruff check .
ruff format .

# Frontend
npm run lint
```

### Docker Development
```bash
docker-compose up --build
```

## 📊 Monitoring & Performance

- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Logging**: Structured logging with configurable levels
- **Health Checks**: Comprehensive health monitoring
- **Error Handling**: Graceful error handling with user-friendly messages

## 🔒 Security

- **CORS**: Configured for secure cross-origin requests
- **Environment Variables**: Sensitive data managed via environment variables
- **API Keys**: Secure API key management
- **Input Validation**: Comprehensive request validation using Pydantic

## 🚀 Deployment

### Production Environment Variables
Set all required environment variables in your production environment.

### Docker Deployment
```bash
docker build -t luma-backend ./backend
docker build -t luma-frontend ./frontend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For questions and support, please open an issue in the repository.
