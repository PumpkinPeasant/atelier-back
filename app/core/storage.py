"""S3-совместимое хранилище файлов (MinIO локально, облако в проде).

boto3 синхронный, поэтому вызовы оборачиваются в run_in_threadpool на стороне
эндпоинтов, чтобы не блокировать event loop.
"""

from functools import lru_cache

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings


@lru_cache
def get_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def upload_bytes(key: str, data: bytes, content_type: str) -> None:
    get_client().put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )


def delete_object(key: str) -> None:
    get_client().delete_object(Bucket=settings.s3_bucket, Key=key)


def public_url(key: str) -> str:
    return f"{settings.s3_public_base}/{key}"


def ensure_bucket() -> None:
    """Создаёт бакет, если его нет (для локальной разработки)."""
    client = get_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        client.create_bucket(Bucket=settings.s3_bucket)
