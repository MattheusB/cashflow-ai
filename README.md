# Cashflow AI

> AI-powered Telegram bot for automatic expense tracking and categorization using LangChain + LLM

## Overview

This project implements an intelligent expense tracking system through Telegram. Users can simply send messages like "Pizza 20 reais" and the system automatically extracts the expense details, categorizes them using AI, and stores them in a database.

### Key Features

- **Natural Language Processing**: Send expenses in plain text
- **Automatic Categorization**: AI-powered category assignment
- **User Whitelist**: Only authorized users can access the bot
- **Microservices Architecture**: Scalable and maintainable design
- **Production-Ready**: Docker, CI/CD, health checks, structured logging
- **High Test Coverage**: >80% code coverage with automated tests

## Architecture

The system consists of two independent microservices:

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│   Telegram  │─────▶│  Connector       │─────▶│ Bot Service │
│   Webhook   │      │  Service         │      │ (FastAPI)   │
└─────────────┘      │  (Express.js)    │      │             │
                     │                  │      │  LangChain  │
                     │  - Whitelist     │      │  + LLM      │
                     │  - Validation    │      │             │
                     └──────────────────┘      └─────────────┘
                              │                        │
                              └────────┬───────────────┘
                                       ▼
                                  ┌──────────┐
                                  │PostgreSQL│
                                  └──────────┘
```

### Bot Service (Python 3.11+)
- **Framework**: FastAPI with async support
- **AI/ML**: LangChain + OpenAI GPT-4 / Anthropic Claude
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Testing**: pytest with >80% coverage

### Connector Service (Node.js 20+)
- **Framework**: Express.js with TypeScript + ESM
- **Telegram**: node-telegram-bot-api
- **Validation**: Zod schemas
- **Testing**: Vitest with coverage

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 16+ (or use Docker)
- Telegram Bot Token
- OpenAI API Key or Anthropic API Key

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/expense-tracker-bot.git
cd expense-tracker-bot

# Copy environment variables template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your credentials:

```env
# Database
DATABASE_URL=postgresql://expense_user:your_password@localhost:5432/expense_tracker

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

# LLM (choose one)
OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
LLM_MODEL=gpt-4
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify services are healthy
curl http://localhost:8000/api/v1/health
curl http://localhost:3000/health
```

### 4. Add Users to Whitelist

```bash
# Connect to database
docker-compose exec postgres psql -U expense_user -d expense_tracker

# Add your Telegram user ID
INSERT INTO users (telegram_id) VALUES ('YOUR_TELEGRAM_USER_ID');
```

### 5. Set Telegram Webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-domain.com/webhook"
```

## Usage

Once configured, simply message your bot:

```
You: Pizza 20 reais
Bot: Food expense added ✅

You: Uber to office 15
Bot: Transportation expense added ✅

You: Netflix subscription 29.90
Bot: Entertainment expense added ✅

You: Hello
Bot: This doesn't look like an expense. Try something like: 'Pizza 20 reais'
```

### Supported Categories

- Housing
- Transportation
- Food
- Utilities
- Insurance
- Medical/Healthcare
- Savings
- Debt
- Education
- Entertainment
- Other

## Development

### Bot Service (Python)

```bash
cd bot-service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run tests
pytest --cov=src

# Run linters
black src/
isort src/
flake8 src/

# Start dev server
uvicorn src.main:app --reload
```

### Connector Service (Node.js)

```bash
cd connector-service

# Install dependencies
npm install

# Run tests
npm test
npm run test:coverage

# Run linters
npm run lint
npm run format

# Start dev server
npm run dev

# Build for production
npm run build
npm start
```

## Project Structure

```
expense-tracker-bot/
├── bot-service/                 # Python FastAPI service
│   ├── src/
│   │   ├── api/                # API routes
│   │   ├── services/           # Business logic (LLM, expenses)
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── utils/              # Config, logging
│   │   └── main.py             # FastAPI app
│   ├── alembic/                # Database migrations
│   ├── tests/                  # pytest tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── connector-service/          # Node.js Express service
│   ├── src/
│   │   ├── routes/             # Express routes
│   │   ├── services/           # Telegram, Bot API client
│   │   ├── utils/              # Config, logging, database
│   │   └── index.ts            # Express app
│   ├── tests/                  # Vitest tests
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── README.md
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml
├── .env.example
└── README.md                   # This file
```

## Testing

The project has comprehensive test coverage (>80%) with automated tests:

### Run All Tests

```bash
# Bot Service
cd bot-service && pytest --cov=src

# Connector Service
cd connector-service && npm run test:coverage

# Integration tests with Docker
docker-compose up -d
# Run your integration tests here
docker-compose down
```

### Continuous Integration

GitHub Actions automatically runs:
- Linting (black, isort, flake8, eslint, prettier)
- Type checking (mypy, TypeScript)
- Unit tests with coverage
- Docker builds
- Integration tests

## API Documentation

### Bot Service API

**Base URL**: `http://localhost:8000`

#### Health Check
```http
GET /api/v1/health
```

#### Process Message
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

### Connector Service API

**Base URL**: `http://localhost:3000`

#### Health Check
```http
GET /health
```

#### Webhook (Telegram)
```http
POST /webhook
Content-Type: application/json

{
  "update_id": 123,
  "message": { ... }
}
```

### Database connection issues
- Ensure PostgreSQL is running: `docker-compose ps postgres`
- Check DATABASE_URL format
- Verify credentials


### Code Style

- **Python**: Follow PEP 8, use Black + isort
- **TypeScript**: Follow Airbnb Style Guide, use Prettier + ESLint
- **Commits**: Use conventional commits format

## Acknowledgments

- [LangChain](https://langchain.com/) for LLM orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for the Python API framework
- [Express.js](https://expressjs.com/) for the Node.js framework
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Happy expense tracking!** 📊💰
