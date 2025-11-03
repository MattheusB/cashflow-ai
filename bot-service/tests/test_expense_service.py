"""Tests for ExpenseService."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal

from src.services.expense_service import ExpenseService
from src.schemas import ExpenseCreate, ExpenseExtraction, ExpenseCategory
from src.models.models import User, Expense


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    mock = Mock()
    mock.extract_expense = AsyncMock()
    return mock


@pytest.fixture
def expense_service(mock_llm_service):
    """Create an ExpenseService instance with mocked LLM."""
    return ExpenseService(mock_llm_service)


class TestProcessMessage:
    """Test process_message method."""

    @pytest.mark.asyncio
    async def test_process_valid_expense(self, expense_service, mock_llm_service, db_session, sample_user):
        """Test processing a valid expense message."""
        mock_llm_service.extract_expense.return_value = ExpenseExtraction(
            is_expense=True, description="Pizza", amount=20.0, category=ExpenseCategory.FOOD
        )

        response = await expense_service.process_message(sample_user.id, "Pizza 20 reais", db_session)

        assert response.success is True
        assert "Food expense added" in response.message
        assert response.expense_id is not None

        expense = db_session.query(Expense).filter(Expense.id == response.expense_id).first()
        assert expense is not None
        assert expense.description == "Pizza"
        assert float(expense.amount) == 20.0
        assert expense.category == "Food"

    @pytest.mark.asyncio
    async def test_process_non_expense(self, expense_service, mock_llm_service, db_session, sample_user):
        """Test processing a non-expense message."""
        mock_llm_service.extract_expense.return_value = ExpenseExtraction(
            is_expense=False, description=None, amount=None, category=None
        )

        response = await expense_service.process_message(sample_user.id, "Hello", db_session)

        assert response.success is False
        assert "doesn't look like an expense" in response.message
        assert response.expense_id is None

    @pytest.mark.asyncio
    async def test_process_incomplete_extraction(
        self, expense_service, mock_llm_service, db_session, sample_user
    ):
        """Test processing with incomplete extraction."""
        mock_llm_service.extract_expense.return_value = ExpenseExtraction(
            is_expense=True, description="Pizza", amount=None, category=ExpenseCategory.FOOD
        )

        response = await expense_service.process_message(sample_user.id, "Pizza", db_session)

        assert response.success is False
        assert "Could not extract all expense details" in response.message

    @pytest.mark.asyncio
    async def test_process_llm_error(self, expense_service, mock_llm_service, db_session, sample_user):
        """Test handling of LLM errors."""
        mock_llm_service.extract_expense.side_effect = Exception("LLM API error")

        response = await expense_service.process_message(sample_user.id, "Pizza 20", db_session)

        assert response.success is False
        assert "error processing your expense" in response.message


class TestCreateExpense:
    """Test create_expense method."""

    def test_create_expense_success(self, expense_service, db_session, sample_user):
        """Test successfully creating an expense."""
        expense_data = ExpenseCreate(
            user_id=sample_user.id,
            description="Lunch",
            amount=Decimal("15.50"),
            category=ExpenseCategory.FOOD,
        )

        expense = expense_service.create_expense(expense_data, db_session)

        assert expense.id is not None
        assert expense.user_id == sample_user.id
        assert expense.description == "Lunch"
        assert expense.amount == Decimal("15.50")
        assert expense.category == "Food"


class TestGetUserExpenses:
    """Test get_user_expenses method."""

    def test_get_user_expenses_empty(self, expense_service, db_session, sample_user):
        """Test getting expenses for user with no expenses."""
        expenses = expense_service.get_user_expenses(sample_user.id, db_session)
        assert len(expenses) == 0

    def test_get_user_expenses_with_data(self, expense_service, db_session, sample_user):
        """Test getting expenses for user with expenses."""
        for i in range(5):
            expense = Expense(
                user_id=sample_user.id,
                description=f"Expense {i}",
                amount=Decimal(f"{i * 10}.00"),
                category="Food",
            )
            db_session.add(expense)
        db_session.commit()

        expenses = expense_service.get_user_expenses(sample_user.id, db_session)

        assert len(expenses) == 5
        assert expenses[0].description == "Expense 4"

    def test_get_user_expenses_with_limit(self, expense_service, db_session, sample_user):
        """Test getting expenses with limit."""
        for i in range(10):
            expense = Expense(
                user_id=sample_user.id,
                description=f"Expense {i}",
                amount=Decimal("10.00"),
                category="Food",
            )
            db_session.add(expense)
        db_session.commit()

        expenses = expense_service.get_user_expenses(sample_user.id, db_session, limit=3)
        assert len(expenses) == 3

    def test_get_user_expenses_with_offset(self, expense_service, db_session, sample_user):
        """Test getting expenses with offset."""
        for i in range(5):
            expense = Expense(
                user_id=sample_user.id,
                description=f"Expense {i}",
                amount=Decimal("10.00"),
                category="Food",
            )
            db_session.add(expense)
        db_session.commit()

        expenses = expense_service.get_user_expenses(sample_user.id, db_session, offset=2)
        assert len(expenses) == 3


class TestUserManagement:
    """Test user management methods."""

    def test_user_exists_true(self, expense_service, db_session, sample_user):
        """Test user_exists returns True for existing user."""
        exists = expense_service.user_exists(sample_user.telegram_id, db_session)
        assert exists is True

    def test_user_exists_false(self, expense_service, db_session):
        """Test user_exists returns False for non-existing user."""
        exists = expense_service.user_exists("nonexistent", db_session)
        assert exists is False

    def test_create_user(self, expense_service, db_session):
        """Test creating a new user."""
        user = expense_service.create_user("999888777", db_session)

        assert user.id is not None
        assert user.telegram_id == "999888777"

        found_user = db_session.query(User).filter(User.telegram_id == "999888777").first()
        assert found_user is not None

    def test_get_user_by_telegram_id_exists(self, expense_service, db_session, sample_user):
        """Test getting existing user by telegram_id."""
        user = expense_service.get_user_by_telegram_id(sample_user.telegram_id, db_session)

        assert user is not None
        assert user.id == sample_user.id
        assert user.telegram_id == sample_user.telegram_id

    def test_get_user_by_telegram_id_not_exists(self, expense_service, db_session):
        """Test getting non-existing user by telegram_id."""
        user = expense_service.get_user_by_telegram_id("nonexistent", db_session)
        assert user is None
