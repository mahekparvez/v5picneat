"""
Core Configuration for Pic N Eat Backend
Updated with Cloudinary support (FREE alternative to AWS S3)
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
from functools import lru_cache
import secrets

class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Pic N Eat API"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"  # Alias used by app.main and routes
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/picneat",
        description="PostgreSQL connection string"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if v and v.startswith("postgres://"):
            # Convert postgres:// to postgresql:// for SQLAlchemy
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    # ========================================
    # Image Storage Options
    # ========================================
    
    # OPTION 1: Cloudinary (RECOMMENDED - FREE & EASY!)
    # Sign up at https://cloudinary.com/users/register/free
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # OPTION 2: AWS S3 (Original option)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "picneat-images"
    S3_UPLOAD_PREFIX: str = "uploads"
    
    # OPTION 3: Supabase Storage
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Which storage to use (auto-detect based on available credentials)
    @property
    def storage_backend(self) -> str:
        """Automatically detect which storage backend to use"""
        if self.CLOUDINARY_CLOUD_NAME and self.CLOUDINARY_API_KEY:
            return "cloudinary"
        elif self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY:
            return "s3"
        elif self.SUPABASE_URL and self.SUPABASE_KEY:
            return "supabase"
        else:
            return "local"  # Fallback to local storage for development
    
    # ========================================
    # USDA Food Data Central API
    # ========================================
    USDA_FDC_API_KEY: str = Field(
        default="DEMO_KEY",
        description="Get your key from https://fdc.nal.usda.gov/api-key-signup.html"
    )
    FDC_API_BASE_URL: str = "https://api.nal.usda.gov/fdc/v1"
    
    # ML Model
    MODEL_PATH: str = "./models/best_model.pth"
    USE_ONNX: bool = True
    MODEL_DEVICE: str = "cpu"  # "cuda" or "cpu"
    
    # Points System
    POINTS_PER_MEAL_LOGGED: int = 10
    POINTS_PER_RESISTANCE: int = 25  # Higher reward for discipline!
    RESISTANCE_STREAK_MULTIPLIER: float = 1.5  # Bonus for consecutive resistances
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: set[str] = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    }
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# JWT Settings
JWT_SECRET_KEY = get_settings().SECRET_KEY
JWT_ALGORITHM = get_settings().ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
