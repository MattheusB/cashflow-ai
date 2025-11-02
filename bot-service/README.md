# Bot Service

> LLM-powered expense extraction and categorization service using FastAPI + LangChain

## Overview

The Bot Service is the core of the expense tracking system. It uses LangChain to interact with Large Language Models (OpenAI GPT-4 or Anthropic Claude) to:

1. Validate if a message represents an expense
2. Extract description, amount, and category
3. Store expenses in PostgreSQL database

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern async web framework
- **LangChain** - LLM orchestration framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **pytest** - Testing framework

## Project Structure

```
bot-service/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # FastAPI endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py        # Database connection
│   │   └── models.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py     # LangChain + LLM logic
│   │   └── expense_service.py # Expense CRUD operations
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Structured logging
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── tests/                     # Unit tests
├── requirements.txt
├── Dockerfile
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker
BOT_SERVICE_HOST=0.0.0.0
BOT_SERVICE_PORT=8000
OPENAI_API_KEY=your_openai_key
LLM_MODEL=gpt-4
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 3. Run Migrations

```bash
# Run all migrations
alembic upgrade head

# Create a new migration (if needed)
alembic revision --autogenerate -m "description"
```

### 4. Start the Server

```bash
# Development (with auto-reload)
uvicorn src.main:app --reload

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "llm": "configured"
}
```

### Process Message

```http
POST /api/v1/process
Content-Type: application/json

{
  "user_id": 123456789,
  "message": "Pizza 20 reais"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Food expense added ✅",
  "expense_id": 42
}
```

### Get User Expenses

```http
GET /api/v1/users/{telegram_id}/expenses?limit=10&offset=0
```

**Response:**
```json
{
  "telegram_id": "123456789",
  "total_expenses": 2,
  "expenses": [
    {
      "id": 42,
      "description": "Pizza",
      "amount": 20.0,
      "category": "Food",
      "added_at": "2025-01-01T12:00:00"
    }
  ]
}
```

## LLM Service

The `LLMService` class handles all LLM interactions:

- **Retry Mechanism**: Automatic retry with exponential backoff
- **Prompt Engineering**: Carefully crafted prompts for accurate extraction
- **Model Agnostic**: Supports both OpenAI and Anthropic models
- **Structured Output**: Uses Pydantic for type-safe responses

### Supported Models

- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Anthropic: `claude-3-sonnet-20240229`, `claude-3-opus-20240229`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_llm_service.py

# Run with verbose output
pytest -v
```

### Test Coverage

We maintain >80% test coverage for:
- Unit tests for all services
- API endpoint tests
- Database operation tests
- Mock LLM responses for consistent testing

## Code Quality

```bash
# Format code
black src/
isort src/

# Check formatting
black --check src/
isort --check-only src/

# Run linter
flake8 src/

# Type checking
mypy src/
```

## Docker

```bash
# Build image
docker build -t expense-bot-service .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e OPENAI_API_KEY=... \
  expense-bot-service
```

## Configuration

All configuration is managed through environment variables. See `src/utils/config.py` for the complete list.

### Required Variables

- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - LLM provider API key

### Optional Variables

- `BOT_SERVICE_HOST` - Host to bind (default: 0.0.0.0)
- `BOT_SERVICE_PORT` - Port to bind (default: 8000)
- `LLM_MODEL` - Model to use (default: gpt-4)
- `LOG_LEVEL` - Logging level (default: INFO)
- `ENVIRONMENT` - Environment name (default: development)
