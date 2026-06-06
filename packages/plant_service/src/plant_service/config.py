"""Service configuration"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def get_database_url() -> str:
    """Get database URL from environment"""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is required")
    return url


def get_s3_bucket() -> str:
    """Get S3 bucket name from environment"""
    return os.environ.get("S3_BUCKET", "plant-tracking-media")


def get_s3_region() -> str:
    """Get S3 region from environment"""
    return os.environ.get("S3_REGION", "us-east-1")


def get_s3_access_key_id() -> str | None:
    """Get S3 access key ID from environment"""
    return os.environ.get("S3_ACCESS_KEY_ID")


def get_s3_secret_access_key() -> str | None:
    """Get S3 secret access key from environment"""
    return os.environ.get("S3_SECRET_ACCESS_KEY")


def get_s3_endpoint_url() -> str | None:
    """Get S3 endpoint URL from environment (for local testing with localstack etc.)"""
    return os.environ.get("S3_ENDPOINT_URL")
