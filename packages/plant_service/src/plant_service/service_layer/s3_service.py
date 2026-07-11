"""
S3 service wrapper for media attachment storage
"""
from __future__ import annotations

import logging
from typing import Protocol

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ReadableBytes(Protocol):
    """Minimal read-only binary stream protocol for boto3 upload_fileobj."""

    def read(self, size: int = -1) -> bytes: ...


class S3Service:
    """Service for handling S3 operations for media attachments."""

    def __init__(
        self,
        endpoint_url: str | None,
        access_key_id: str | None,
        secret_access_key: str | None,
        region_name: str,
        bucket: str,
        force_path_style: bool = False,
    ) -> None:
        client_config = None
        if force_path_style:
            client_config = Config(s3={"addressing_style": "path"})
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
            config=client_config,
        )
        self.bucket = bucket

    @classmethod
    def from_config(cls) -> S3Service:
        """Create an S3 service from environment configuration."""
        from plant_service import config

        return cls(
            endpoint_url=config.get_s3_endpoint_url(),
            access_key_id=config.get_s3_access_key_id(),
            secret_access_key=config.get_s3_secret_access_key(),
            region_name=config.get_s3_region(),
            bucket=config.get_s3_bucket(),
            force_path_style=config.get_s3_force_path_style(),
        )

    def upload_file(self, file_path: str, s3_key: str) -> bool:
        """Upload a file to S3."""
        try:
            self.client.upload_file(file_path, self.bucket, s3_key)
            return True
        except ClientError as e:
            logger.error("Error uploading file to S3: %s", e)
            return False

    def upload_fileobj(self, fileobj: ReadableBytes, s3_key: str) -> bool:
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
