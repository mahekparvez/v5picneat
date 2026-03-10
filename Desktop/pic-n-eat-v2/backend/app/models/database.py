"""
Database Models for Pic N Eat
"""

from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class LogType(str, enum.Enum):
    """Type of food log"""
    EATEN = "eaten"
    RESISTED = "resisted"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Profile
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Gamification
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)  # Consecutive resistances
    longest_streak = Column(Integer, default=0)
    
    # Goals
    daily_calorie_goal = Column(Integer, nullable=True)
    weekly_resistance_goal = Column(Integer, default=7)  # Goal: resist 1 temptation per day
    
    # Relationships
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"

class FoodLog(Base):
    """Food log model - tracks both eaten and resisted foods"""
    __tablename__ = "food_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Image
    image_url = Column(String, nullable=False)
    image_s3_key = Column(String, nullable=False)
    
    # Food Recognition
    food_category = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    portion_multiplier = Column(Float, default=1.0)
    
    # Nutrition (per 100g from USDA FDC)
    calories_per_100g = Column(Float, nullable=True)
    protein_per_100g = Column(Float, nullable=True)
    carbs_per_100g = Column(Float, nullable=True)
    fat_per_100g = Column(Float, nullable=True)
    fiber_per_100g = Column(Float, nullable=True)
    sugar_per_100g = Column(Float, nullable=True)
    
    # Actual estimated values (adjusted for portion)
    estimated_calories = Column(Float, nullable=True)
    estimated_protein = Column(Float, nullable=True)
    estimated_carbs = Column(Float, nullable=True)
    estimated_fat = Column(Float, nullable=True)
    
    # Log type
    log_type = Column(Enum(LogType), nullable=False, default=LogType.EATEN)
    
    # Points awarded for this log
    points_earned = Column(Integer, default=0)
    
    # Optional user notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # USDA FDC reference
    fdc_id = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="food_logs")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_logtype_date', 'user_id', 'log_type', 'logged_at'),
        Index('idx_user_date', 'user_id', 'logged_at'),
    )
    
    def __repr__(self):
        return f"<FoodLog {self.food_category} ({self.log_type})>"

class NutritionCache(Base):
    """Cache for USDA FDC API responses"""
    __tablename__ = "nutrition_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, unique=True, index=True, nullable=False)
    fdc_id = Column(Integer, nullable=False)
    
    # Nutritional values per 100g
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)
    
    # Raw API response
    raw_response = Column(Text, nullable=True)
    
    # Cache metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    access_count = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<NutritionCache {self.food_name}>"
