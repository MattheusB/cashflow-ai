"""Tests for database models."""

import pytest
from decimal import Decimal
from datetime import datetime

from src.models.models import User, Expense


def test_create_user(db_session):
    """Test creating a user."""
    user = User(telegram_id="987654321")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.telegram_id == "987654321"
    assert len(user.expenses) == 0


def test_user_repr(sample_user):
    """Test user string representation."""
    repr_str = repr(sample_user)
    assert "User" in repr_str
    assert str(sample_user.id) in repr_str
    assert sample_user.telegram_id in repr_str


def test_create_expense(db_session, sample_user):
    """Test creating an expense."""
    expense = Expense(
        user_id=sample_user.id,
        description="Lunch",
        amount=Decimal("15.50"),
        category="Food",
        added_at=datetime.utcnow(),
    )
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)

    assert expense.id is not None
    assert expense.user_id == sample_user.id
    assert expense.description == "Lunch"
    assert expense.amount == Decimal("15.50")
    assert expense.category == "Food"
    assert expense.added_at is not None


def test_expense_repr(sample_expense):
    """Test expense string representation."""
    repr_str = repr(sample_expense)
    assert "Expense" in repr_str
    assert str(sample_expense.id) in repr_str
    assert sample_expense.description in repr_str


def test_expense_amount_float(sample_expense):
    """Test expense amount_float property."""
    assert isinstance(sample_expense.amount_float, float)
    assert sample_expense.amount_float == 20.0


def test_user_expense_relationship(db_session, sample_user):
    """Test relationship between user and expenses."""
    expense1 = Expense(
        user_id=sample_user.id,
        description="Expense 1",
        amount=Decimal("10.00"),
        category="Food",
        added_at=datetime.utcnow(),
    )
    expense2 = Expense(
        user_id=sample_user.id,
        description="Expense 2",
        amount=Decimal("20.00"),
        category="Transportation",
        added_at=datetime.utcnow(),
    )

    db_session.add_all([expense1, expense2])
    db_session.commit()
    db_session.refresh(sample_user)

    assert len(sample_user.expenses) == 2
    assert expense1 in sample_user.expenses
    assert expense2 in sample_user.expenses


def test_expense_user_relationship(sample_expense, sample_user):
    """Test relationship from expense to user."""
    assert sample_expense.user == sample_user
    assert sample_expense.user.telegram_id == sample_user.telegram_id


def test_user_unique_telegram_id(db_session, sample_user):
    """Test that telegram_id is unique."""
    duplicate_user = User(telegram_id=sample_user.telegram_id)
    db_session.add(duplicate_user)

    with pytest.raises(Exception):
        db_session.commit()


def test_cascade_delete(db_session, sample_user):
    """Test that deleting a user cascades to expenses."""
    expense = Expense(
        user_id=sample_user.id,
        description="Test",
        amount=Decimal("10.00"),
        category="Food",
        added_at=datetime.utcnow(),
    )
    db_session.add(expense)
    db_session.commit()

    expense_id = expense.id

    db_session.delete(sample_user)
    db_session.commit()

    deleted_expense = db_session.query(Expense).filter(Expense.id == expense_id).first()
    assert deleted_expense is None
