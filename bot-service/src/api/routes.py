"""FastAPI route handlers."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..models import get_db
from ..schemas import ExpenseResponse, HealthResponse, MessageRequest
from ..services import ExpenseService, LLMService
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

llm_service = LLMService()
expense_service = ExpenseService(llm_service)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Health check endpoint to verify service status.

    Returns:
        HealthResponse: Service health status
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    llm_status = "configured" if llm_service.is_configured() else "not_configured"

    overall_status = (
        "healthy" if db_status == "connected" and llm_status == "configured" else "unhealthy"
    )

    return HealthResponse(status=overall_status, database=db_status, llm=llm_status)


@router.post("/process", response_model=ExpenseResponse)
async def process_message(
    request: MessageRequest, db: Session = Depends(get_db)
) -> ExpenseResponse:
    """
    Process a user message and extract expense information.

    Args:
        request: Message request containing user_id and message
        db: Database session

    Returns:
        ExpenseResponse: Processing result

    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(f"Processing message from user {request.user_id}")

        telegram_id = str(request.user_id)
        user = expense_service.get_user_by_telegram_id(telegram_id, db)

        if not user:
            logger.warning(f"User {telegram_id} not found, auto-creating...")
            user = expense_service.create_user(telegram_id, db)

        numeric_user_id = user.id

        response = await expense_service.process_message(numeric_user_id, request.message, db)

        return response

    except Exception as e:
        logger.error(f"Error in process_message endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing message")


@router.get("/users/{telegram_id}/expenses")
async def get_user_expenses(
    telegram_id: str, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)
):
    """
    Get expenses for a specific user (optional feature).

    Args:
        telegram_id: Telegram user ID
        limit: Maximum number of expenses to return
        offset: Number of expenses to skip
        db: Database session

    Returns:
        List of expenses

    Raises:
        HTTPException: If user not found
    """
    user = expense_service.get_user_by_telegram_id(telegram_id, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expenses = expense_service.get_user_expenses(user.id, db, limit=limit, offset=offset)

    return {
        "telegram_id": telegram_id,
        "total_expenses": len(expenses),
        "expenses": [
            {
                "id": exp.id,
                "description": exp.description,
                "amount": float(exp.amount),
                "category": exp.category,
                "added_at": exp.added_at.isoformat(),
            }
            for exp in expenses
        ],
    }
