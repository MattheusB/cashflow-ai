"""Pydantic schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ExpenseCategory(str, Enum):
    """Valid expense categories."""

    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    FOOD = "Food"
    UTILITIES = "Utilities"
    INSURANCE = "Insurance"
    MEDICAL_HEALTHCARE = "Medical/Healthcare"
    SAVINGS = "Savings"
    DEBT = "Debt"
    EDUCATION = "Education"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


class MessageRequest(BaseModel):
    """Request schema for processing user messages."""

    user_id: int = Field(..., description="Telegram user ID", gt=0)
    message: str = Field(..., description="User message text", min_length=1, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123456789,
                "message": "Pizza 20 reais",
            }
        }


class ExpenseExtraction(BaseModel):
    """Schema for extracted expense data from LLM."""

    is_expense: bool = Field(..., description="Whether the message is an expense")
    description: str | None = Field(None, description="Expense description")
    amount: float | None = Field(None, description="Expense amount", gt=0)
    category: ExpenseCategory | None = Field(None, description="Expense category")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float | None) -> float | None:
        """Validate and round amount to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v


class ExpenseResponse(BaseModel):
    """Response schema for expense processing."""

    success: bool = Field(..., description="Whether processing was successful")
    message: str = Field(..., description="Response message to user")
    expense_id: int | None = Field(None, description="Created expense ID if successful")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Food expense added ✅",
                "expense_id": 42,
            }
        }


class ExpenseCreate(BaseModel):
    """Schema for creating a new expense."""

    user_id: int = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category: ExpenseCategory

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123456789,
                "description": "Pizza",
                "amount": "20.00",
                "category": "Food",
            }
        }


class ExpenseRead(BaseModel):
    """Schema for reading expense data."""

    id: int
    user_id: int
    description: str
    amount: Decimal
    category: str
    added_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    database: Literal["connected", "disconnected"] = Field(
        ..., description="Database connection status"
    )
    llm: Literal["configured", "not_configured"] = Field(..., description="LLM configuration status")
