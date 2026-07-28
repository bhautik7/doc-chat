from pydantic_settings import BaseSettings
from typing import List, Optional
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
    cors_allow_origins: str = "http://localhost:5173"
    enable_api_docs: bool = False
    max_upload_size_mb: int = 20

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    class Config:
        env_file=".env"

settings=Settings()