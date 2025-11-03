"""Tests for API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock

from src.schemas import ExpenseExtraction, ExpenseCategory


class TestHealthEndpoint:
    """Test /health endpoint."""

    def test_health_check_healthy(self, client, db_session):
        """Test health check when all services are healthy."""
        with patch("src.api.routes.llm_service.is_configured", return_value=True):
            response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["llm"] == "configured"

    def test_health_check_llm_not_configured(self, client):
        """Test health check when LLM is not configured."""
        with patch("src.api.routes.llm_service.is_configured", return_value=False):
            response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["llm"] == "not_configured"


class TestProcessEndpoint:
    """Test /process endpoint."""

    @pytest.mark.asyncio
    async def test_process_valid_expense(self, client, sample_user):
        """Test processing a valid expense message."""
        with patch(
            "src.api.routes.expense_service.process_message",
            new_callable=AsyncMock,
        ) as mock_process:
            mock_process.return_value = type(
                "Response", (), {"success": True, "message": "Food expense added ✅", "expense_id": 1}
            )()

            response = client.post(
                "/api/v1/process", json={"user_id": int(sample_user.telegram_id), "message": "Pizza 20 reais"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Food expense added" in data["message"]

    def test_process_invalid_user_id(self, client):
        """Test processing with invalid user_id."""
        response = client.post("/api/v1/process", json={"user_id": -1, "message": "Pizza 20"})

        assert response.status_code == 422

    def test_process_empty_message(self, client):
        """Test processing with empty message."""
        response = client.post("/api/v1/process", json={"user_id": 123456, "message": ""})

        assert response.status_code == 422

    def test_process_missing_fields(self, client):
        """Test processing with missing fields."""
        response = client.post("/api/v1/process", json={"user_id": 123456})

        assert response.status_code == 422


class TestGetUserExpensesEndpoint:
    """Test /users/{telegram_id}/expenses endpoint."""

    def test_get_expenses_success(self, client, sample_user, sample_expense):
        """Test getting expenses for existing user."""
        response = client.get(f"/api/v1/users/{sample_user.telegram_id}/expenses")

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == sample_user.telegram_id
        assert len(data["expenses"]) > 0
        assert data["expenses"][0]["description"] == sample_expense.description

    def test_get_expenses_user_not_found(self, client):
        """Test getting expenses for non-existing user."""
        response = client.get("/api/v1/users/nonexistent/expenses")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_expenses_with_limit(self, client, sample_user, db_session):
        """Test getting expenses with limit parameter."""
        from src.models.models import Expense
        from decimal import Decimal

        for i in range(5):
            expense = Expense(
                user_id=sample_user.id,
                description=f"Expense {i}",
                amount=Decimal("10.00"),
                category="Food",
            )
            db_session.add(expense)
        db_session.commit()

        response = client.get(f"/api/v1/users/{sample_user.telegram_id}/expenses?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["expenses"]) == 3

    def test_get_expenses_with_offset(self, client, sample_user, db_session):
        """Test getting expenses with offset parameter."""
        from src.models.models import Expense
        from decimal import Decimal

        for i in range(5):
            expense = Expense(
                user_id=sample_user.id,
                description=f"Expense {i}",
                amount=Decimal("10.00"),
                category="Food",
            )
            db_session.add(expense)
        db_session.commit()

        response = client.get(f"/api/v1/users/{sample_user.telegram_id}/expenses?offset=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["expenses"]) == 3


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "Expense Tracker Bot Service" in data["service"]
        assert data["status"] == "running"
