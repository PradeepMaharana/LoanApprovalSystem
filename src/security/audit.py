"""Audit logging for compliance and monitoring."""

from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditLog:
    """Audit log entry for sensitive operations."""

    def __init__(
        self,
        user_id: str,
        action: str,
        resource: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error: Optional[str] = None,
    ):
        self.timestamp = datetime.utcnow()
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.resource_id = resource_id
        self.details = details or {}
        self.status = status
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "details": self.details,
            "status": self.status,
            "error": self.error,
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())


# In-memory audit log (in production, write to database/file)
AUDIT_LOGS = []


def audit_log(entry: AuditLog) -> None:
    """
    Log an audit entry.

    Args:
        entry: AuditLog entry to log
    """
    AUDIT_LOGS.append(entry)

    status_emoji = "✅" if entry.status == "success" else "❌"
    log_msg = (
        f"{status_emoji} AUDIT: {entry.user_id} {entry.action} "
        f"{entry.resource}/{entry.resource_id}"
    )

    if entry.status == "success":
        logger.info(log_msg)
    else:
        logger.warning(f"{log_msg} - Error: {entry.error}")


def log_sensitive_operation(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str,
    changes: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a sensitive operation.

    Args:
        user_id: User performing operation
        action: Action type (CREATE, UPDATE, DELETE, APPROVE, REJECT)
        resource: Resource type (applicant, application, etc.)
        resource_id: ID of affected resource
        changes: Dictionary of what changed
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details={"changes": changes} if changes else {},
        status="success",
    )
    audit_log(entry)


def log_failed_operation(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str,
    error: str,
) -> None:
    """Log a failed operation."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        status="failed",
        error=error,
    )
    audit_log(entry)


def log_authentication_attempt(
    user_id: str, success: bool, ip_address: Optional[str] = None
) -> None:
    """Log authentication attempt."""
    action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource="authentication",
        resource_id=user_id,
        details={"ip_address": ip_address},
        status="success" if success else "failed",
    )
    audit_log(entry)


def log_permission_denied(
    user_id: str, resource: str, action: str, resource_id: str
) -> None:
    """Log permission denied incident."""
    entry = AuditLog(
        user_id=user_id,
        action=f"{action}_DENIED",
        resource=resource,
        resource_id=resource_id,
        status="failed",
        error="Permission denied",
    )
    audit_log(entry)


def get_audit_logs(
    user_id: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
) -> list:
    """
    Retrieve audit logs with optional filters.

    Args:
        user_id: Filter by user
        resource: Filter by resource type
        action: Filter by action
        limit: Maximum number of results

    Returns:
        List of matching audit log entries
    """
    results = AUDIT_LOGS

    if user_id:
        results = [log for log in results if log.user_id == user_id]
    if resource:
        results = [log for log in results if log.resource == resource]
    if action:
        results = [log for log in results if log.action == action]

    return results[-limit:]


def export_audit_logs(filename: str) -> None:
    """Export audit logs to JSON file."""
    with open(filename, "w") as f:
        logs = [log.to_dict() for log in AUDIT_LOGS]
        json.dump(logs, f, indent=2, default=str)
    logger.info(f"✅ Audit logs exported to: {filename}")


def clear_audit_logs(days: int = 90) -> int:
    """
    Clear audit logs older than specified days.

    Args:
        days: Age threshold in days

    Returns:
        Number of logs deleted
    """
    cutoff = datetime.utcnow().timestamp() - (days * 86400)
    initial_count = len(AUDIT_LOGS)

    AUDIT_LOGS[:] = [
        log
        for log in AUDIT_LOGS
        if log.timestamp.timestamp() > cutoff
    ]

    deleted = initial_count - len(AUDIT_LOGS)
    logger.info(f"✅ Deleted {deleted} audit logs older than {days} days")
    return deleted
