/**
 * Database connection and user whitelist management
 */

import pg from 'pg';
import { config } from './config.js';
import { createLogger } from './logger.js';

const logger = createLogger('database');
const { Pool } = pg;

/**
 * Database connection pool
 */
export const pool = new Pool({
  connectionString: config.databaseUrl,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  logger.error('Unexpected error on idle client', err);
});

/**
 * Check if user is whitelisted
 */
export async function isUserWhitelisted(telegramId: string): Promise<boolean> {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT id FROM users WHERE telegram_id = $1', [telegramId]);
    return result.rows.length > 0;
  } catch (error) {
    logger.error('Error checking user whitelist', error as Error, { telegramId });
    throw error;
  } finally {
    client.release();
  }
}

/**
 * Get user ID by telegram ID
 */
export async function getUserId(telegramId: string): Promise<number | null> {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT id FROM users WHERE telegram_id = $1', [telegramId]);
    return result.rows.length > 0 ? result.rows[0].id : null;
  } catch (error) {
    logger.error('Error getting user ID', error as Error, { telegramId });
    throw error;
  } finally {
    client.release();
  }
}

/**
 * Test database connection
 */
export async function testConnection(): Promise<boolean> {
  try {
    const client = await pool.connect();
    await client.query('SELECT 1');
    client.release();
    logger.info('Database connection successful');
    return true;
  } catch (error) {
    logger.error('Database connection failed', error as Error);
    return false;
  }
}

/**
 * Close database pool
 */
export async function closePool(): Promise<void> {
  await pool.end();
  logger.info('Database pool closed');
}
