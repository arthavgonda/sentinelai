from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Twitter/X API Credentials
    API_KEY_X: str = ""
    API_KEY_SECRET_X: str = ""
    
    # Telegram API Credentials
    API_ID_TELEGRAM: int = 0
    API_KEY_TELEGRAM: str = ""
    
    # GitHub API Token
    GITHUB_API_TOKEN: str = ""
    
    # Numverify API Key
    NUMVERIFY_API_KEY: str = ""
    
    # Etherscan API Key
    ETHERSCAN_API_KEY: str = ""
    
    # VirusTotal API Key
    VIRUSTOTAL_API_KEY: str = ""
    
    # NewsAPI Key
    NEWSAPI_KEY: str = ""
    
    # Google News API Key
    GOOGLE_NEWS_API_KEY: str = ""
    
    # Instagram RapidAPI Credentials
    INSTAGRAM_RAPIDAPI_HOST: str = "instagram120.p.rapidapi.com"
    INSTAGRAM_RAPIDAPI_KEY: str = ""
    
    # Hunter.io RapidAPI Credentials
    HUNTER_RAPIDAPI_HOST: str = "email-finder7.p.rapidapi.com"
    HUNTER_RAPIDAPI_KEY: str = ""
    
    # IPInfo Token
    IPINFO_TOKEN: str = ""
    
    # Reddit API Credentials
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "OSINT/1.0 by YourAppName"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./osint.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    API_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 50
    CACHE_TTL_SOCIAL: int = 3600
    CACHE_TTL_EMAIL: int = 86400
    CACHE_TTL_BLOCKCHAIN: int = 900
    CACHE_TTL_NEWS: int = 3600
    
    RATE_LIMIT_PER_MINUTE: int = 60
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60
    
    ENABLE_WEBSOCKET: bool = True
    WEBSOCKET_PORT: int = 8765
    
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

