from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    anthropic_api_key: str
    openai_api_key: str | None = None
    
    # Stripe
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str | None = None
    stripe_price_id_basic: str  # $79/month plan
    
    # Database
    database_url: str = "sqlite:///./shopbot.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 1 week
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # AI Settings
    default_ai_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
