import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BizFlow AI - LeadRadar"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Storage
    DB_PATH: str = os.environ.get(
        "BIZFLOW_DB_PATH", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bizflow.db")
    )
    
    # Telegram Notifications
    TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.environ.get("TELEGRAM_CHAT_ID", "")
    TELEGRAM_ENABLED: bool = bool(int(os.environ.get("TELEGRAM_ENABLED", "0")))
    
    # Scanning interval in seconds (default: 60 seconds)
    SCAN_INTERVAL: int = int(os.environ.get("SCAN_INTERVAL", "60"))
    MIN_INTENT_SCORE: int = int(os.environ.get("MIN_INTENT_SCORE", "60"))
    
    # Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", "8000"))

    class Config:
        case_sensitive = True

settings = Settings()
