"""Plant tracking commands package."""

from pathlib import Path

from dotenv import load_dotenv

# Load .env before the database module reads DATABASE_URL at import time
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from . import database  # noqa: F401, E402
