"""Role-Based Access Control (RBAC) management."""

from typing import Dict, List, Optional
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Role permission matrix
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": ["read", "write", "delete", "audit", "manage_users"],
    "analyst": ["read", "write", "audit"],
    "user": ["read", "write"],
    "viewer": ["read"],
    "guest": [],
}

# Resource-role access matrix
RESOURCE_PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
    "applicants": {
        "read": ["admin", "analyst", "user"],
        "write": ["admin", "analyst"],
        "delete": ["admin"],
    },
    "applications": {
        "read": ["admin", "analyst", "user"],
        "write": ["admin", "analyst", "user"],
        "delete": ["admin"],
    },
    "audit_logs": {
        "read": ["admin", "analyst"],
        "write": ["system"],
        "delete": ["admin"],
    },
    "users": {
        "read": ["admin"],
        "write": ["admin"],
        "delete": ["admin"],
    },
    "analytics": {
        "read": ["admin", "analyst"],
        "write": ["admin"],
        "delete": ["admin"],
    },
}


def check_permission(user_role: str, resource: str, action: str) -> bool:
    """
    Check if user role has permission for resource action.

    Args:
        user_role: User's role (admin, analyst, user, viewer, guest)
        resource: Resource name (applicants, applications, etc.)
        action: Action type (read, write, delete)

    Returns:
        True if permission granted
    """
    if resource not in RESOURCE_PERMISSIONS:
        logger.warning(f"⚠️ Unknown resource: {resource}")
        return False

    if action not in RESOURCE_PERMISSIONS[resource]:
        logger.warning(f"⚠️ Unknown action: {action} for resource: {resource}")
        return False

    allowed_roles = RESOURCE_PERMISSIONS[resource][action]
    has_permission = user_role in allowed_roles

    if has_permission:
        logger.debug(f"✅ Permission granted: {user_role} {action} {resource}")
    else:
        logger.warning(
            f"❌ Permission denied: {user_role} {action} {resource}"
        )

    return has_permission


def check_scope(user_scopes: List[str], required_scope: str) -> bool:
    """
    Check if user has required scope.

    Args:
        user_scopes: List of user scopes
        required_scope: Required scope (read, write, delete, audit, manage_users)

    Returns:
        True if user has scope
    """
    has_scope = required_scope in user_scopes
    if not has_scope:
        logger.warning(f"❌ Scope missing: user lacks '{required_scope}' scope")
    return has_scope


def require_role(required_roles: List[str]):
    """
    Decorator to require specific role for function.
    Expects 'current_user' dict in kwargs.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                logger.error("❌ No user context found")
                raise ValueError("User context required")

            user_role = current_user.get("role", "guest")
            if user_role not in required_roles:
                logger.error(f"❌ Insufficient role: {user_role}")
                raise PermissionError(
                    f"Required role(s): {', '.join(required_roles)}"
                )

            logger.debug(f"✅ Role check passed: {user_role}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_scope(required_scope: str):
    """
    Decorator to require specific scope for function.
    Expects 'current_user' dict in kwargs.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                logger.error("❌ No user context found")
                raise ValueError("User context required")

            user_scopes = current_user.get("scopes", [])
            if not check_scope(user_scopes, required_scope):
                raise PermissionError(f"Required scope: {required_scope}")

            logger.debug(f"✅ Scope check passed: {required_scope}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def add_role(role: str, permissions: List[str]) -> None:
    """Add a new role with permissions."""
    ROLE_PERMISSIONS[role] = permissions
    logger.info(f"✅ Role added: {role} with permissions: {permissions}")


def grant_permission(
    role: str, resource: str, action: str
) -> None:
    """Grant permission for role on resource action."""
    if resource not in RESOURCE_PERMISSIONS:
        RESOURCE_PERMISSIONS[resource] = {}
    if action not in RESOURCE_PERMISSIONS[resource]:
        RESOURCE_PERMISSIONS[resource][action] = []

    if role not in RESOURCE_PERMISSIONS[resource][action]:
        RESOURCE_PERMISSIONS[resource][action].append(role)
        logger.info(f"✅ Permission granted: {role} → {action} {resource}")


def revoke_permission(role: str, resource: str, action: str) -> None:
    """Revoke permission for role on resource action."""
    if (
        resource in RESOURCE_PERMISSIONS
        and action in RESOURCE_PERMISSIONS[resource]
    ):
        if role in RESOURCE_PERMISSIONS[resource][action]:
            RESOURCE_PERMISSIONS[resource][action].remove(role)
            logger.info(f"✅ Permission revoked: {role} → {action} {resource}")
