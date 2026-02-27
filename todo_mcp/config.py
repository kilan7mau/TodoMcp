import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Lấy thư mục gốc của dự án (thư mục chứa folder todo_mcp)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(ROOT_DIR, ".env")

class Settings(BaseSettings):
    # Cấu hình mặc định
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "todo_db"
    COLLECTION_NAME: str = "tasks"
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
