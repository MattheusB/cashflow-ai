/**
 * Configuration management using environment variables
 */

import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

/**
 * Configuration schema with validation
 */
const configSchema = z.object({
  databaseUrl: z.string().url('Invalid DATABASE_URL'),

  connectorServiceHost: z.string().default('0.0.0.0'),
  connectorServicePort: z.coerce.number().int().positive().default(3000),

  botServiceUrl: z.string().url('Invalid BOT_SERVICE_URL'),

  telegramBotToken: z.string().min(1, 'TELEGRAM_BOT_TOKEN is required'),
  telegramWebhookUrl: z.string().url('Invalid TELEGRAM_WEBHOOK_URL').optional(),

  logLevel: z.enum(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']).default('INFO'),
  environment: z.enum(['development', 'staging', 'production']).default('development'),
});

/**
 * Configuration type
 */
export type Config = z.infer<typeof configSchema>;

/**
 * Parse and validate configuration from environment variables
 */
function loadConfig(): Config {
  const config = {
    databaseUrl: process.env.DATABASE_URL,
    connectorServiceHost: process.env.CONNECTOR_SERVICE_HOST,
    connectorServicePort: process.env.CONNECTOR_SERVICE_PORT,
    botServiceUrl: process.env.BOT_SERVICE_URL,
    telegramBotToken: process.env.TELEGRAM_BOT_TOKEN,
    telegramWebhookUrl: process.env.TELEGRAM_WEBHOOK_URL,
    logLevel: process.env.LOG_LEVEL,
    environment: process.env.ENVIRONMENT,
  };

  try {
    return configSchema.parse(config);
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('Configuration validation failed:');
      error.errors.forEach((err) => {
        console.error(`  - ${err.path.join('.')}: ${err.message}`);
      });
      throw new Error('Invalid configuration');
    }
    throw error;
  }
}

/**
 * Singleton configuration instance
 */
export const config = loadConfig();
