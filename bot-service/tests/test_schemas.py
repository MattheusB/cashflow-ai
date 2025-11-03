"""Tests for Pydantic schemas."""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from src.schemas import (
    ExpenseCategory,
    MessageRequest,
    ExpenseExtraction,
    ExpenseResponse,
    ExpenseCreate,
)


class TestMessageRequest:
    """Test MessageRequest schema."""

    def test_valid_message_request(self):
        """Test creating a valid message request."""
        request = MessageRequest(user_id=123456, message="Pizza 20 reais")
        assert request.user_id == 123456
        assert request.message == "Pizza 20 reais"

    def test_invalid_user_id(self):
        """Test that negative user_id raises error."""
        with pytest.raises(ValidationError):
            MessageRequest(user_id=-1, message="test")

    def test_invalid_zero_user_id(self):
        """Test that zero user_id raises error."""
        with pytest.raises(ValidationError):
            MessageRequest(user_id=0, message="test")

    def test_empty_message(self):
        """Test that empty message raises error."""
        with pytest.raises(ValidationError):
            MessageRequest(user_id=123, message="")

    def test_long_message(self):
        """Test that too long message raises error."""
        with pytest.raises(ValidationError):
            MessageRequest(user_id=123, message="a" * 501)


class TestExpenseExtraction:
    """Test ExpenseExtraction schema."""

    def test_valid_expense_extraction(self):
        """Test creating a valid expense extraction."""
        extraction = ExpenseExtraction(
            is_expense=True,
            description="Pizza",
            amount=20.50,
            category=ExpenseCategory.FOOD,
        )
        assert extraction.is_expense is True
        assert extraction.description == "Pizza"
        assert extraction.amount == 20.50
        assert extraction.category == ExpenseCategory.FOOD

    def test_non_expense(self):
        """Test extraction for non-expense message."""
        extraction = ExpenseExtraction(
            is_expense=False, description=None, amount=None, category=None
        )
        assert extraction.is_expense is False
        assert extraction.description is None
        assert extraction.amount is None
        assert extraction.category is None

    def test_amount_rounding(self):
        """Test that amount is rounded to 2 decimal places."""
        extraction = ExpenseExtraction(
            is_expense=True,
            description="Test",
            amount=20.999,
            category=ExpenseCategory.OTHER,
        )
        assert extraction.amount == 21.0

    def test_negative_amount(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValidationError):
            ExpenseExtraction(
                is_expense=True,
                description="Test",
                amount=-10.0,
                category=ExpenseCategory.FOOD,
            )


class TestExpenseResponse:
    """Test ExpenseResponse schema."""

    def test_success_response(self):
        """Test creating a successful response."""
        response = ExpenseResponse(success=True, message="Food expense added ✅", expense_id=42)
        assert response.success is True
        assert "Food" in response.message
        assert response.expense_id == 42

    def test_failure_response(self):
        """Test creating a failure response."""
        response = ExpenseResponse(success=False, message="Not an expense", expense_id=None)
        assert response.success is False
        assert response.expense_id is None


class TestExpenseCreate:
    """Test ExpenseCreate schema."""

    def test_valid_expense_create(self):
        """Test creating a valid expense."""
        expense = ExpenseCreate(
            user_id=1,
            description="Lunch",
            amount=Decimal("15.50"),
            category=ExpenseCategory.FOOD,
        )
        assert expense.user_id == 1
        assert expense.description == "Lunch"
        assert expense.amount == Decimal("15.50")
        assert expense.category == ExpenseCategory.FOOD

    def test_invalid_user_id(self):
        """Test that invalid user_id raises error."""
        with pytest.raises(ValidationError):
            ExpenseCreate(
                user_id=0,
                description="Test",
                amount=Decimal("10.00"),
                category=ExpenseCategory.FOOD,
            )

    def test_empty_description(self):
        """Test that empty description raises error."""
        with pytest.raises(ValidationError):
            ExpenseCreate(
                user_id=1, description="", amount=Decimal("10.00"), category=ExpenseCategory.FOOD
            )

    def test_negative_amount(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValidationError):
            ExpenseCreate(
                user_id=1,
                description="Test",
                amount=Decimal("-10.00"),
                category=ExpenseCategory.FOOD,
            )


class TestExpenseCategory:
    """Test ExpenseCategory enum."""

    def test_all_categories_exist(self):
        """Test that all expected categories are defined."""
        expected_categories = [
            "Housing",
            "Transportation",
            "Food",
            "Utilities",
            "Insurance",
            "Medical/Healthcare",
            "Savings",
            "Debt",
            "Education",
            "Entertainment",
            "Other",
        ]

        category_values = [cat.value for cat in ExpenseCategory]
        assert len(category_values) == len(expected_categories)

        for category in expected_categories:
            assert category in category_values

    def test_category_is_string(self):
        """Test that category values are strings."""
        for category in ExpenseCategory:
            assert isinstance(category.value, str)
