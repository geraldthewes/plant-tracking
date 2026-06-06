"""
S3 service wrapper for media attachment storage
"""
from __future__ import annotations

import logging

import boto3
from botocore.exceptions import ClientError

from plant_service.config import (
    get_s3_access_key_id,
    get_s3_bucket,
    get_s3_endpoint_url,
    get_s3_region,
    get_s3_secret_access_key,
)

logger = logging.getLogger(__name__)


class S3Service:
    """Service for handling S3 operations for media attachments."""

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=get_s3_endpoint_url(),
            aws_access_key_id=get_s3_access_key_id(),
            aws_secret_access_key=get_s3_secret_access_key(),
            region_name=get_s3_region(),
        )
        self.bucket = get_s3_bucket()

    def upload_file(self, file_path: str, s3_key: str) -> bool:
        """Upload a file to S3."""
        try:
            self.client.upload_file(file_path, self.bucket, s3_key)
            return True
        except ClientError as e:
            logger.error("Error uploading file to S3: %s", e)
            return False

    def upload_fileobj(self, fileobj, s3_key: str) -> bool:
        """Upload a file-like object to S3."""
        try:
            self.client.upload_fileobj(fileobj, self.bucket, s3_key)
            return True
        except ClientError as e:
            logger.error("Error uploading fileobj to S3: %s", e)
            return False

    def download_file(self, s3_key: str, file_path: str) -> bool:
        """Download a file from S3."""
        try:
            self.client.download_file(self.bucket, s3_key, file_path)
            return True
        except ClientError as e:
            logger.error("Error downloading file from S3: %s", e)
            return False

    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            logger.error("Error deleting file from S3: %s", e)
            return False

    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> str | None:
        """Generate a presigned URL for S3 object."""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error("Error generating presigned URL: %s", e)
            return None
