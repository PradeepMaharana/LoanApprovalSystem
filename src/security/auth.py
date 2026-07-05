"""JWT Authentication and authorization management."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import hashlib
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security Configuration (should be in .env)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenPayload:
    """JWT token payload structure."""

    def __init__(
        self,
        sub: str,
        user_id: str,
        role: str = "user",
        scopes: list = None,
        exp: datetime = None,
    ):
        self.sub = sub
        self.user_id = user_id
        self.role = role
        self.scopes = scopes or ["read", "write"]
        self.exp = exp or (datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))


def create_token(
    user_id: str,
    role: str = "user",
    scopes: Optional[list] = None,
    expires_days: Optional[int] = None,
) -> str:
    """
    Create a JWT token for the given user.

    Args:
        user_id: Unique user identifier
        role: User role (user, admin, analyst)
        scopes: List of permission scopes
        expires_days: Token expiration in days (default: 1)

    Returns:
        JWT token string
    """
    if expires_days is None:
        expires_days = ACCESS_TOKEN_EXPIRE_DAYS

    expire = datetime.utcnow() + timedelta(days=expires_days)
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "role": role,
        "scopes": scopes or ["read", "write"],
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"✅ Token created for user: {user_id} (role: {role})")
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"✅ Token verified for user: {payload.get('user_id')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"❌ Invalid token: {str(e)}")
        return None


def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    Get current user from token.

    Args:
        token: JWT token string

    Returns:
        User information or None if invalid
    """
    payload = verify_token(token)
    if not payload:
        return None

    return {
        "user_id": payload.get("user_id"),
        "role": payload.get("role"),
        "scopes": payload.get("scopes", []),
    }


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password
        hashed: Hashed password

    Returns:
        True if passwords match
    """
    return hash_password(password) == hashed


def require_auth(func):
    """
    Decorator to require authentication on a function.
    Expects 'token' parameter in kwargs.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs.get("token")
        if not token:
            logger.error("❌ No authentication token provided")
            raise ValueError("Authentication token required")

        user = get_current_user(token)
        if not user:
            logger.error("❌ Invalid or expired token")
            raise ValueError("Invalid or expired token")

        kwargs["current_user"] = user
        return func(*args, **kwargs)

    return wrapper
