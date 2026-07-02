"""Создать бакет в S3/MinIO, если его нет.

Использование:
    python -m scripts.init_bucket

Для локального docker-compose бакет уже создаётся сервисом minio-init —
этот скрипт нужен, если поднимаете MinIO/облако отдельно.
"""

from app.core import storage
from app.core.config import settings


def main() -> None:
    storage.ensure_bucket()
    print(f"Bucket ready: {settings.s3_bucket} @ {settings.s3_endpoint_url}")


if __name__ == "__main__":
    main()
