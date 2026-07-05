"""Pytest configuration and shared fixtures."""

import pytest
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class MockDatabase:
    """Mock database for testing."""

    def __init__(self):
        self.applicants = {}
        self.applications = {}
        self.connected = True

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False

    def insert_applicant(self, data: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        app_id = data.get("applicant_id")
        self.applicants[app_id] = data
        return True

    def insert_loan_application(self, data: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        app_id = data.get("applicant_id")
        self.applications[app_id] = data
        return True

    def get_applicant(self, applicant_id: str) -> Dict[str, Any]:
        return self.applicants.get(applicant_id)

    def search_applicants(
        self, criteria: Dict[str, Any], limit: int = 100
    ) -> list:
        results = list(self.applicants.values())

        if "applicant_id" in criteria:
            results = [
                r
                for r in results
                if criteria["applicant_id"] in r.get("applicant_id", "")
            ]

        return results[:limit]


class MockUser:
    """Mock user for authentication tests."""

    def __init__(
        self,
        user_id: str = "test_user",
        role: str = "user",
        scopes: list = None,
    ):
        self.user_id = user_id
        self.role = role
        self.scopes = scopes or ["read", "write"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role,
            "scopes": self.scopes,
        }


@pytest.fixture
def mock_db():
    """Fixture for mock database."""
    db = MockDatabase()
    db.connect()
    yield db
    db.disconnect()


@pytest.fixture
def mock_user():
    """Fixture for mock user."""
    return MockUser()


@pytest.fixture
def admin_user():
    """Fixture for admin user."""
    return MockUser(user_id="admin_user", role="admin")


@pytest.fixture
def test_applicant() -> Dict[str, Any]:
    """Fixture for test applicant data."""
    return {
        "applicant_id": "APP-TEST-001",
        "age": 35,
        "income": 120000.0,
        "employment_type": "Salaried",
        "location": "New York, NY",
    }


@pytest.fixture
def test_application(test_applicant) -> Dict[str, Any]:
    """Fixture for test loan application."""
    return {
        "applicant_id": test_applicant["applicant_id"],
        "credit_score": 750,
        "loan_amount": 300000.0,
        "tenure_months": 360,
        "existing_liabilities": 50000.0,
        "risk_score": 78.5,
        "risk_level": "Low Risk",
    }


@pytest.fixture
def test_token():
    """Fixture for test JWT token."""
    from src.security.auth import create_token

    return create_token(user_id="test_user", role="user")


@pytest.fixture
def admin_token():
    """Fixture for admin JWT token."""
    from src.security.auth import create_token

    return create_token(user_id="admin_user", role="admin")


@pytest.fixture(autouse=True)
def reset_security_state():
    """Reset security state before each test."""
    from src.security.audit import AUDIT_LOGS

    AUDIT_LOGS.clear()
    yield
    AUDIT_LOGS.clear()
