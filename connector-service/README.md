# Connector Service

> Telegram webhook handler and Bot Service connector built with Express.js + TypeScript

## Overview

The Connector Service acts as a gateway between Telegram and the Bot Service. It:

1. Receives messages from Telegram via webhook
2. Validates user whitelist from PostgreSQL
3. Forwards valid messages to Bot Service
4. Returns responses to users through Telegram

## Tech Stack

- **Node.js 20+**
- **Express.js** - Web framework
- **TypeScript** - Type-safe JavaScript
- **Zod** - Schema validation
- **node-telegram-bot-api** - Telegram Bot API client
- **pg** - PostgreSQL client
- **Vitest** - Testing framework

## Project Structure

```
connector-service/
├── src/
│   ├── routes/
│   │   ├── health.ts          # Health check endpoint
│   │   └── webhook.ts         # Telegram webhook handler
│   ├── services/
│   │   ├── botService.ts      # Bot Service API client
│   │   └── telegramService.ts # Telegram bot logic
│   ├── utils/
│   │   ├── config.ts          # Configuration with Zod
│   │   ├── database.ts        # PostgreSQL connection pool
│   │   └── logger.ts          # Structured JSON logging
│   └── index.ts               # Express application
├── tests/                     # Vitest tests
├── package.json
├── tsconfig.json
├── Dockerfile
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
# Install packages
npm install

# For development
npm install --save-dev
```

### 2. Configure Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker
CONNECTOR_SERVICE_HOST=0.0.0.0
CONNECTOR_SERVICE_PORT=3000
BOT_SERVICE_URL=http://localhost:8000
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 3. Build TypeScript

```bash
# Build for production
npm run build

# Type check only
npm run type-check
```

### 4. Start the Server

```bash
# Development (with hot reload)
npm run dev

# Production
npm start
```

## API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": "connected",
    "botService": "healthy"
  },
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

### Telegram Webhook

```http
POST /webhook
Content-Type: application/json

{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "first_name": "John"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "text": "Pizza 20 reais"
  }
}
```

**Response:**
```http
200 OK
```

## Services

### Telegram Service

Handles all Telegram-related operations:

- **Message Processing**: Validates and routes messages
- **Whitelist Check**: Ensures only authorized users can interact
- **Response Handling**: Sends formatted responses back to users
- **Webhook Management**: Sets up and maintains webhook

```typescript
import { telegramService } from './services/telegramService';

// Process a message
await telegramService.processMessage(message);

// Send a message
await telegramService.sendMessage(chatId, text);

// Set webhook
await telegramService.setWebhook('https://your-domain.com/webhook');
```

### Bot Service Client

HTTP client for communicating with the Bot Service:

- **Request Validation**: Uses Zod schemas
- **Error Handling**: Graceful degradation on failures
- **Retry Logic**: Axios timeout and retry configuration
- **Type Safety**: Full TypeScript support

```typescript
import { botServiceClient } from './services/botService';

// Process a message
const response = await botServiceClient.processMessage(userId, message);

// Check health
const isHealthy = await botServiceClient.healthCheck();
```

## Database

### Connection Pool

The service uses `pg` connection pool for efficient database operations:

```typescript
import { pool, isUserWhitelisted } from './utils/database';

// Check if user is whitelisted
const whitelisted = await isUserWhitelisted('123456789');

// Get user ID
const userId = await getUserId('123456789');

// Test connection
const healthy = await testConnection();
```

### Pool Configuration

- **Max Connections**: 20
- **Idle Timeout**: 30 seconds
- **Connection Timeout**: 2 seconds

## Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (for development)
npm run test:watch
```

### Test Structure

```typescript
import { describe, it, expect } from 'vitest';

describe('BotServiceClient', () => {
  it('should process message successfully', async () => {
    const response = await botServiceClient.processMessage(123, 'Pizza 20');
    expect(response.success).toBe(true);
  });
});
```

## Code Quality

```bash
# Run linter
npm run lint

# Fix linting issues
npm run lint:fix

# Check formatting
npm run format:check

# Format code
npm run format
```

### ESLint Configuration

Follows **Airbnb TypeScript Style Guide** with Prettier integration.

### Prettier Configuration

- Single quotes
- 2-space indentation
- 100 character line width
- Semicolons enabled

## Docker

```bash
# Build image
docker build -t expense-connector-service .

# Run container
docker run -p 3000:3000 \
  -e DATABASE_URL=postgresql://... \
  -e TELEGRAM_BOT_TOKEN=... \
  -e BOT_SERVICE_URL=http://bot-service:8000 \
  expense-connector-service
```

## Configuration

All configuration is validated using Zod schemas. See `src/utils/config.ts`.

### Required Variables

- `DATABASE_URL` - PostgreSQL connection string
- `BOT_SERVICE_URL` - Bot Service API URL
- `TELEGRAM_BOT_TOKEN` - Telegram Bot API token

### Optional Variables

- `CONNECTOR_SERVICE_HOST` - Host to bind (default: 0.0.0.0)
- `CONNECTOR_SERVICE_PORT` - Port to bind (default: 3000)
- `TELEGRAM_WEBHOOK_URL` - Webhook URL (optional for development)
- `LOG_LEVEL` - Logging level (default: INFO)
- `ENVIRONMENT` - Environment name (default: development)

## Logging

Structured JSON logging for easy parsing and analysis:

```typescript
import { createLogger } from './utils/logger';

const logger = createLogger('my-module');

logger.info('User message processed', { userId: 123, success: true });
logger.error('Failed to process message', error, { userId: 123 });
```

**Log Output:**
```json
{
  "timestamp": "2025-01-01T12:00:00.000Z",
  "level": "INFO",
  "name": "my-module",
  "message": "User message processed",
  "userId": 123,
  "success": true
}
```

## Setting Up Telegram Webhook

### Development (using ngrok)

```bash
# Start ngrok
ngrok http 3000

# Set webhook
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-ngrok-url.ngrok.io/webhook"

# Verify webhook
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
```

### Production

Set `TELEGRAM_WEBHOOK_URL` in environment variables, and the service will automatically set the webhook on startup.

## Integration with Bot Service

The connector communicates with Bot Service via REST API:

1. Receives message from Telegram
2. Checks user whitelist
3. Calls `POST /api/v1/process` on Bot Service
4. Returns response to user via Telegram

```
[Telegram] → [Connector] → [Bot Service] → [LLM]
                 ↓              ↓
            [Database]    [Database]
```
