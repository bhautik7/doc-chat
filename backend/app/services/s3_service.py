import boto3
import uuid
from app.utils.config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

def upload_file_to_s3(file_bytes: bytes, filename: str, user_id: int) -> str:
    file_extension = filename.rsplit(".", 1)[-1]
    s3_key = f"users/{user_id}/documents/{uuid.uuid4()}.{file_extension}"
    s3_client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=s3_key,
        Body=file_bytes,
    )
    return s3_key

def delete_file_from_s3(s3_key: str) -> None:
    s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)

def get_file_from_s3(s3_key: str) -> bytes:
    response = s3_client.get_object(Bucket=settings.s3_bucket_name, Key=s3_key)
    return response["Body"].read()