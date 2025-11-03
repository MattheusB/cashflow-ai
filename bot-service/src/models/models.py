"""SQLAlchemy models for users and expenses."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """User model for whitelist management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Text, unique=True, nullable=False, index=True)

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id='{self.telegram_id}')>"


class Expense(Base):
    """Expense model for tracking user expenses."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    category = Column(Text, nullable=False, index=True)
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="expenses")

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, user_id={self.user_id}, description='{self.description}', amount={self.amount}, category='{self.category}')>"

    @property
    def amount_float(self) -> float:
        """Get amount as float for easier manipulation."""
        return float(self.amount) if isinstance(self.amount, Decimal) else self.amount
