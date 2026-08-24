"""Pytest configuration for CLI unit tests.

Commands-package unit tests exercise the Markdown code paths. Blank out
DATABASE_URL (unless the operator explicitly exported one) so that
importing the commands package does not load a live database connection
from the repo-root .env via load_dotenv (which never overrides an
already-set value).
"""
import os

os.environ.setdefault("DATABASE_URL", "")
