from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Gamification
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    
    # Preferences
    daily_calorie_goal = Column(Integer, default=2000)
    timezone = Column(String(50), default="UTC")
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    resistance_logs = relationship("ResistanceLog", back_populates="user", cascade="all, delete-orphan")
    points_history = relationship("PointsHistory", back_populates="user", cascade="all, delete-orphan")


class FoodLog(Base):
    """Food consumption log."""
    __tablename__ = "food_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Image
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Food identification
    food_name = Column(String(255), nullable=False)
    food_fdc_id = Column(Integer, nullable=True)  # USDA FDC ID
    
    # Nutrition (per serving)
    calories = Column(Float, nullable=False)
    protein = Column(Float, default=0)  # grams
    carbs = Column(Float, default=0)    # grams
    fat = Column(Float, default=0)      # grams
    fiber = Column(Float, default=0)    # grams
    
    # Serving info
    portion_size = Column(Float, nullable=True)  # grams
    serving_description = Column(String(255), nullable=True)  # "1 medium banana"
    
    # ML metadata
    confidence_score = Column(Float, nullable=False)
    model_version = Column(String(50), default="v1.0")
    alternative_predictions = Column(Text, nullable=True)  # JSON string of top-5
    
    # Context
    meal_type = Column(String(50), nullable=True)  # breakfast, lunch, dinner, snack
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="food_logs")


class ResistanceLog(Base):
    """Log of foods successfully resisted."""
    __tablename__ = "resistance_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Image
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Food identification
    food_name = Column(String(255), nullable=False)
    food_fdc_id = Column(Integer, nullable=True)
    
    # Estimated nutrition (what they DIDN'T eat)
    estimated_calories = Column(Float, nullable=False)
    estimated_protein = Column(Float, default=0)
    estimated_carbs = Column(Float, default=0)
    estimated_fat = Column(Float, default=0)
    
    # Points
    points_earned = Column(Integer, default=10)
    bonus_reason = Column(String(255), nullable=True)  # "high_calorie", "late_night"
    
    # ML metadata
    confidence_score = Column(Float, nullable=False)
    model_version = Column(String(50), default="v1.0")
    
    # Context
    notes = Column(Text, nullable=True)
    resisted_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resistance_logs")


class PointsHistory(Base):
    """Track all points earned by users."""
    __tablename__ = "points_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    points = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)  # resistance, streak_bonus, achievement
    description = Column(String(500), nullable=True)
    
    # Reference to related log (optional)
    related_log_id = Column(UUID(as_uuid=True), nullable=True)
    related_log_type = Column(String(50), nullable=True)  # food_log, resistance_log
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="points_history")


class FDCCache(Base):
    """Cache USDA FDC API responses."""
    __tablename__ = "fdc_cache"
    
    fdc_id = Column(Integer, primary_key=True)
    food_name = Column(String(255), nullable=False)
    
    # Nutrition per 100g
    calories = Column(Float, nullable=False)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    fiber = Column(Float, default=0)
    
    # Serving info
    serving_size = Column(Float, nullable=True)
    serving_unit = Column(String(50), nullable=True)
    
    # Raw data
    raw_data = Column(Text, nullable=True)  # JSON string of full FDC response
    
    cached_at = Column(DateTime, server_default=func.now())
    data_type = Column(String(50), default="SR Legacy")  # FDC data source type


class Achievement(Base):
    """User achievements."""
    __tablename__ = "achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    achievement_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    points_awarded = Column(Integer, default=0)
    
    unlocked_at = Column(DateTime, server_default=func.now())
