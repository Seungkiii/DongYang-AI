from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI 설정
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-ada-002"
    gpt_model: str = "gpt-4"
    
    # 벡터 DB 설정
    vector_store_path: str = "vector_store"
    documents_path: str = "documents"
    
    # 문서 처리 설정
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # API 설정
    api_prefix: str = "/api"
    debug: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 