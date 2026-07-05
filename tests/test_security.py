"""Security module tests."""

import pytest
import time
from datetime import datetime, timedelta

from src.security.auth import (
    create_token,
    verify_token,
    get_current_user,
    hash_password,
    verify_password,
)
from src.security.rbac import (
    check_permission,
    check_scope,
    require_role,
    grant_permission,
    revoke_permission,
)
from src.security.audit import (
    AuditLog,
    audit_log,
    log_sensitive_operation,
    log_failed_operation,
    get_audit_logs,
    AUDIT_LOGS,
)


class TestAuthentication:
    """Test JWT authentication functionality."""

    @pytest.mark.unit
    def test_create_token(self):
        """Test token creation."""
        token = create_token("test_user", role="user")
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.unit
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        token = create_token("test_user", role="user")
        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == "test_user"
        assert payload["role"] == "user"

    @pytest.mark.unit
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        payload = verify_token("invalid.token.string")
        assert payload is None

    @pytest.mark.unit
    def test_get_current_user(self):
        """Test getting current user from token."""
        token = create_token("test_user", role="analyst")
        user = get_current_user(token)
        assert user is not None
        assert user["user_id"] == "test_user"
        assert user["role"] == "analyst"

    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    @pytest.mark.unit
    def test_token_scopes(self):
        """Test token scopes."""
        scopes = ["read", "write", "audit"]
        token = create_token("test_user", scopes=scopes)
        payload = verify_token(token)
        assert payload["scopes"] == scopes

    @pytest.mark.unit
    def test_admin_token(self):
        """Test admin token creation."""
        token = create_token("admin_user", role="admin")
        user = get_current_user(token)
        assert user["role"] == "admin"


class TestRBAC:
    """Test role-based access control."""

    @pytest.mark.unit
    def test_admin_permissions(self):
        """Test admin has all permissions."""
        assert check_permission("admin", "applicants", "read")
        assert check_permission("admin", "applicants", "write")
        assert check_permission("admin", "applicants", "delete")

    @pytest.mark.unit
    def test_analyst_permissions(self):
        """Test analyst permissions."""
        assert check_permission("analyst", "applicants", "read")
        assert check_permission("analyst", "applicants", "write")
        assert not check_permission("analyst", "applicants", "delete")

    @pytest.mark.unit
    def test_user_permissions(self):
        """Test user permissions."""
        assert check_permission("user", "applications", "read")
        assert check_permission("user", "applications", "write")
        assert not check_permission("user", "audit_logs", "read")

    @pytest.mark.unit
    def test_check_scope(self):
        """Test scope checking."""
        scopes = ["read", "write"]
        assert check_scope(scopes, "read")
        assert check_scope(scopes, "write")
        assert not check_scope(scopes, "delete")

    @pytest.mark.unit
    def test_grant_permission(self):
        """Test granting permissions."""
        initial_allowed = check_permission("viewer", "applicants", "read")
        grant_permission("viewer", "applicants", "read")
        assert check_permission("viewer", "applicants", "read")

    @pytest.mark.unit
    def test_revoke_permission(self):
        """Test revoking permissions."""
        grant_permission("viewer", "applications", "read")
        assert check_permission("viewer", "applications", "read")
        revoke_permission("viewer", "applications", "read")
        assert not check_permission("viewer", "applications", "read")

    @pytest.mark.unit
    def test_require_role_decorator(self):
        """Test role requirement decorator."""

        @require_role(["admin"])
        def admin_only_function(current_user=None):
            return "success"

        # Should work with admin
        admin_user = {"user_id": "admin", "role": "admin"}
        result = admin_only_function(current_user=admin_user)
        assert result == "success"

        # Should fail with regular user
        user = {"user_id": "user", "role": "user"}
        with pytest.raises(PermissionError):
            admin_only_function(current_user=user)


class TestAuditLogging:
    """Test audit logging functionality."""

    @pytest.mark.unit
    def test_audit_log_entry(self):
        """Test creating audit log entry."""
        entry = AuditLog(
            user_id="test_user",
            action="CREATE",
            resource="applicant",
            resource_id="APP-001",
        )
        assert entry.user_id == "test_user"
        assert entry.action == "CREATE"
        assert entry.status == "success"

    @pytest.mark.unit
    def test_audit_log_to_dict(self):
        """Test converting audit log to dict."""
        entry = AuditLog(
            user_id="test_user",
            action="UPDATE",
            resource="application",
            resource_id="LOAN-001",
            details={"credit_score": 750},
        )
        log_dict = entry.to_dict()
        assert log_dict["user_id"] == "test_user"
        assert log_dict["action"] == "UPDATE"
        assert log_dict["details"]["credit_score"] == 750

    @pytest.mark.unit
    def test_audit_log_sensitive_operation(self):
        """Test logging sensitive operation."""
        log_sensitive_operation(
            user_id="analyst_user",
            action="APPROVE",
            resource="application",
            resource_id="LOAN-001",
            changes={"status": "APPROVED"},
        )
        logs = get_audit_logs(user_id="analyst_user")
        assert len(logs) == 1
        assert logs[0].action == "APPROVE"

    @pytest.mark.unit
    def test_audit_log_failed_operation(self):
        """Test logging failed operation."""
        log_failed_operation(
            user_id="user",
            action="DELETE",
            resource="applicant",
            resource_id="APP-001",
            error="Permission denied",
        )
        logs = get_audit_logs(user_id="user")
        assert len(logs) == 1
        assert logs[0].status == "failed"
        assert logs[0].error == "Permission denied"

    @pytest.mark.unit
    def test_get_audit_logs_filtered(self):
        """Test retrieving filtered audit logs."""
        # Create multiple logs
        log_sensitive_operation("user1", "CREATE", "applicant", "APP-001")
        log_sensitive_operation("user1", "UPDATE", "applicant", "APP-002")
        log_sensitive_operation("user2", "DELETE", "application", "LOAN-001")

        # Filter by user
        user1_logs = get_audit_logs(user_id="user1")
        assert len(user1_logs) == 2

        # Filter by action
        create_logs = get_audit_logs(action="CREATE")
        assert len(create_logs) == 1

        # Filter by resource
        app_logs = get_audit_logs(resource="applicant")
        assert len(app_logs) == 2


class TestIntegratedSecurity:
    """Test integrated security workflows."""

    @pytest.mark.security
    def test_complete_auth_flow(self):
        """Test complete authentication flow."""
        # Create token
        token = create_token("user@example.com", role="analyst")
        assert token is not None

        # Verify token
        payload = verify_token(token)
        assert payload is not None

        # Get user
        user = get_current_user(token)
        assert user["user_id"] == "user@example.com"

        # Check permissions
        assert check_permission(user["role"], "applicants", "read")

    @pytest.mark.security
    def test_audit_trail_for_admin_operation(self):
        """Test audit trail for sensitive admin operation."""
        admin_token = create_token("admin@example.com", role="admin")
        admin_user = get_current_user(admin_token)

        # Perform sensitive operation
        if check_permission(admin_user["role"], "applicants", "delete"):
            log_sensitive_operation(
                user_id=admin_user["user_id"],
                action="DELETE",
                resource="applicant",
                resource_id="APP-DELETE-001",
                changes={"deleted": True},
            )

        # Verify audit trail
        logs = get_audit_logs(user_id=admin_user["user_id"])
        assert len(logs) == 1
        assert logs[0].action == "DELETE"
