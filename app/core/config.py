from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Crown Mega Store API"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str
    BACKEND_URL: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    BUSINESS_EMAIL: str
    
    # SendGrid (alternative email service)
    SENDGRID_API_KEY: str
    EMAIL_PROVIDER: str = "resend"  # "smtp", "sendgrid", or "resend"
    FROM_EMAIL: str = "crownmegastore@gmail.com"
    
    # Resend
    RESEND_API_KEY: str = ""
    
    # Business
    BUSINESS_WHATSAPP: str
    BUSINESS_PHONE: str
    
    
    class Config:
        env_file = '.env'
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()