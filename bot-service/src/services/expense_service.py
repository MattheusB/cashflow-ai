"""Service for managing expense operations."""

from decimal import Decimal

from sqlalchemy.orm import Session

from ..models import Expense, User
from ..schemas import ExpenseCreate, ExpenseExtraction, ExpenseResponse
from ..utils.logger import log_expense_processing, setup_logger
from .llm_service import LLMService

logger = setup_logger(__name__)


class ExpenseService:
    """Service for processing and managing expenses."""

    def __init__(self, llm_service: LLMService) -> None:
        """Initialize expense service with LLM service."""
        self.llm_service = llm_service

    async def process_message(self, user_id: int, message: str, db: Session) -> ExpenseResponse:
        """
        Process a user message and create expense if valid.

        Args:
            user_id: Telegram user ID
            message: User message text
            db: Database session

        Returns:
            ExpenseResponse: Processing result
        """
        try:
            extraction: ExpenseExtraction = await self.llm_service.extract_expense(message)

            if not extraction.is_expense:
                logger.info(f"Message from user {user_id} is not an expense")
                return ExpenseResponse(
                    success=False,
                    message="This doesn't look like an expense. Try something like: 'Pizza 20 reais'",
                )

            if not all([extraction.description, extraction.amount, extraction.category]):
                logger.warning(f"Incomplete extraction for user {user_id}: {extraction}")
                return ExpenseResponse(
                    success=False,
                    message="Could not extract all expense details. Please provide description, amount, and try again.",
                )

            expense_create = ExpenseCreate(
                user_id=user_id,
                description=extraction.description,
                amount=Decimal(str(extraction.amount)),
                category=extraction.category,
            )

            expense = self.create_expense(expense_create, db)

            log_expense_processing(
                logger,
                user_id,
                message,
                {
                    "expense_id": expense.id,
                    "category": expense.category,
                    "amount": float(expense.amount),
                },
            )

            return ExpenseResponse(
                success=True,
                message=f"{extraction.category.value} expense added ✅",
                expense_id=expense.id,
            )

        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {e}", exc_info=True)
            return ExpenseResponse(
                success=False,
                message="Sorry, there was an error processing your expense. Please try again.",
            )

    def create_expense(self, expense_data: ExpenseCreate, db: Session) -> Expense:
        """
        Create a new expense in the database.

        Args:
            expense_data: Expense data to create
            db: Database session

        Returns:
            Expense: Created expense object
        """
        expense = Expense(
            user_id=expense_data.user_id,
            description=expense_data.description,
            amount=expense_data.amount,
            category=expense_data.category.value,
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        logger.info(f"Created expense {expense.id} for user {expense_data.user_id}")
        return expense

    def get_user_expenses(
        self, user_id: int, db: Session, limit: int = 10, offset: int = 0
    ) -> list[Expense]:
        """
        Get expenses for a specific user.

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of expenses to return
            offset: Number of expenses to skip

        Returns:
            List of expenses
        """
        return (
            db.query(Expense)
            .filter(Expense.user_id == user_id)
            .order_by(Expense.added_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def user_exists(self, telegram_id: str, db: Session) -> bool:
        """
        Check if a user exists in the database (whitelist check).

        Args:
            telegram_id: Telegram user ID
            db: Database session

        Returns:
            bool: True if user exists (is whitelisted)
        """
        return db.query(User).filter(User.telegram_id == telegram_id).first() is not None

    def create_user(self, telegram_id: str, db: Session) -> User:
        """
        Create a new user (add to whitelist).

        Args:
            telegram_id: Telegram user ID
            db: Database session

        Returns:
            User: Created user object
        """
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created user with telegram_id: {telegram_id}")
        return user

    def get_user_by_telegram_id(self, telegram_id: str, db: Session) -> User | None:
        """
        Get user by telegram ID.

        Args:
            telegram_id: Telegram user ID
            db: Database session

        Returns:
            User object or None
        """
        return db.query(User).filter(User.telegram_id == telegram_id).first()
