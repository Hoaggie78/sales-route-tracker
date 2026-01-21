from pydantic_settings import BaseSettings
from typing import Optional
from datetime import datetime


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Microsoft Graph API
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_TENANT_ID: str = "common"
    MICROSOFT_REDIRECT_URI: str
    MICROSOFT_AUTHORITY: str = "https://login.microsoftonline.com/common"
    MICROSOFT_SCOPES: list = ["Files.ReadWrite.All", "User.Read", "offline_access"]
    
    # OneDrive
    ONEDRIVE_FILE_PATH: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 1 week
    
    # CORS and Frontend
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
with open("debug_startup.log", "a") as f:
    f.write(f"\n--- {datetime.now()} ---\n")
    f.write(f"DEBUG: Loaded SECRET_KEY starting with: {settings.SECRET_KEY[:8]}\n")
    f.write(f"DEBUG: Using ALGORITHM: {settings.ALGORITHM}\n")
    f.write(f"DEBUG: FRONTEND_URL: {settings.FRONTEND_URL}\n")
print(f"DEBUG: Loaded SECRET_KEY starting with: {settings.SECRET_KEY[:8]}")
print(f"DEBUG: Using ALGORITHM: {settings.ALGORITHM}")
print(f"DEBUG: FRONTEND_URL: {settings.FRONTEND_URL}")
