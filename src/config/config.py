from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""

    # API Settings
    API_TITLE: str = "Loan Approval System API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Professional REST API for loan application processing"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_LEVEL: str = "info"

    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Business Rules
    MIN_AGE: int = 18
    MAX_AGE: int = 100
    MIN_CREDIT_SCORE: int = 300
    MAX_CREDIT_SCORE: int = 850
    MIN_LOAN_AMOUNT: float = 1000
    MAX_LOAN_AMOUNT: float = 10000000
    MIN_TENURE_MONTHS: int = 3
    MAX_TENURE_MONTHS: int = 360
    TENURE_MULTIPLE: int = 3

    # Risk Thresholds
    VERY_LOW_RISK_THRESHOLD: float = 75
    LOW_RISK_THRESHOLD: float = 60
    MODERATE_RISK_THRESHOLD: float = 40
    HIGH_RISK_THRESHOLD: float = 20

    # Processing Time
    PROCESSING_TIME_DAYS: int = 3
    PROCESSING_TIME_HOURS: int = 2

    # Database (for future use)
    DATABASE_URL: Optional[str] = None
    USE_SQLITE: bool = False
    SQLITE_DB_PATH: str = "loan_approvals.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
