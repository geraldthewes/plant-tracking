import os
from pathlib import Path

from dotenv import load_dotenv
from typing import Optional

load_dotenv(Path(__file__).resolve().parents[4] / ".env")


class Settings:
    """Application settings."""

    def __init__(self):
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.reload: bool = os.getenv("RELOAD", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "info")


settings = Settings()
