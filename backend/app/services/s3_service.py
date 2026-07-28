import logging
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.utils.config import settings
from app.utils.exceptions import NotFoundError, StorageError

logger = logging.getLogger(__name__)

MISSING_OBJECT_CODES = {"NoSuchKey", "404", "NotFound"}

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

def _error_code(error: ClientError) -> str:
    return str(error.response.get("Error", {}).get("Code", ""))

def upload_file_to_s3(file_bytes: bytes, filename: str, user_id: int) -> str:
    file_extension = filename.rsplit(".", 1)[-1]
    s3_key = f"users/{user_id}/documents/{uuid.uuid4()}.{file_extension}"
    try:
        s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=file_bytes,
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to upload %s to s3://%s/%s", filename, settings.s3_bucket_name, s3_key)
        raise StorageError("Failed to store the uploaded file") from exc
    return s3_key

def delete_file_from_s3(s3_key: str) -> None:
    try:
        s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
    except ClientError as exc:
        if _error_code(exc) in MISSING_OBJECT_CODES:
            logger.warning("Object %s was already missing from storage", s3_key)
            return
        logger.exception("Failed to delete %s from storage", s3_key)
        raise StorageError("Failed to delete the stored file") from exc
    except BotoCoreError as exc:
        logger.exception("Failed to delete %s from storage", s3_key)
        raise StorageError("Failed to delete the stored file") from exc

def get_file_from_s3(s3_key: str) -> bytes:
    try:
        response = s3_client.get_object(Bucket=settings.s3_bucket_name, Key=s3_key)
        return response["Body"].read()
    except ClientError as exc:
        if _error_code(exc) in MISSING_OBJECT_CODES:
            logger.error("Object %s is missing from storage", s3_key)
            raise NotFoundError("The stored file is no longer available") from exc
        logger.exception("Failed to read %s from storage", s3_key)
        raise StorageError("Failed to read the stored file") from exc
    except BotoCoreError as exc:
        logger.exception("Failed to read %s from storage", s3_key)
        raise StorageError("Failed to read the stored file") from exc
