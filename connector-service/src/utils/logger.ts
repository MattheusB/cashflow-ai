/**
 * Structured logging utility
 */

import { config } from './config.js';

/**
 * Log levels
 */
enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARNING = 2,
  ERROR = 3,
  CRITICAL = 4,
}

/**
 * Get numeric log level from string
 */
function getLogLevel(level: string): LogLevel {
  return LogLevel[level as keyof typeof LogLevel] ?? LogLevel.INFO;
}

const currentLogLevel = getLogLevel(config.logLevel);

/**
 * Logger class for structured logging
 */
class Logger {
  private name: string;

  constructor(name: string) {
    this.name = name;
  }

  private log(level: LogLevel, message: string, meta?: Record<string, unknown>): void {
    if (level < currentLogLevel) {
      return;
    }

    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level: LogLevel[level],
      name: this.name,
      message,
      ...meta,
    };

    const output = JSON.stringify(logEntry);

    if (level >= LogLevel.ERROR) {
      console.error(output);
    } else {
      console.log(output);
    }
  }

  debug(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, message, meta);
  }

  info(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, message, meta);
  }

  warning(message: string, meta?: Record<string, unknown>): void {
    this.log(LogLevel.WARNING, message, meta);
  }

  error(message: string, error?: Error, meta?: Record<string, unknown>): void {
    this.log(LogLevel.ERROR, message, {
      ...meta,
      error: error
        ? {
            message: error.message,
            stack: error.stack,
            name: error.name,
          }
        : undefined,
    });
  }

  critical(message: string, error?: Error, meta?: Record<string, unknown>): void {
    this.log(LogLevel.CRITICAL, message, {
      ...meta,
      error: error
        ? {
            message: error.message,
            stack: error.stack,
            name: error.name,
          }
        : undefined,
    });
  }
}

/**
 * Create a logger instance
 */
export function createLogger(name: string): Logger {
  return new Logger(name);
}
