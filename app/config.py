from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:8000"

    # SQL Server
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_HOST: str = "localhost"
    DB_PORT: int = 1433
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mssql+aioodbc://@{self.DB_HOST}/{self.DB_NAME}"
            f"?driver={self.DB_DRIVER.replace(' ', '+')}"
            f"&Trusted_Connection=yes"
            f"&TrustServerCertificate=yes"
        )

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 1440     # 24h - Customer
    JWT_STAFF_EXPIRE_MINUTES: int = 480       # 8h  - Staff/Admin
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    # Storage Local
    UPLOAD_DIR: str = "static/uploads"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str

    class Config:
        env_file = ".env"

settings = Settings()
