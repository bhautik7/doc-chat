from pydantic_settings import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    database_url:str
    openai_api_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    s3_bucket_name: str
    s3_endpoint_url: Optional[str] = None
    aws_access_key_id: str
    aws_secret_access_key: str

    class Config:
        env_file=".env"

settings=Settings()