"""
Pydantic Schemas for API Request/Response
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============== User Schemas ==============

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    daily_calorie_goal: Optional[int] = Field(None, ge=500, le=5000)
    weekly_resistance_goal: Optional[int] = Field(None, ge=0, le=100)

class UserResponse(UserBase):
    id: int
    is_active: bool
    total_points: int
    current_streak: int
    longest_streak: int
    daily_calorie_goal: Optional[int]
    weekly_resistance_goal: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============== Auth Schemas ==============

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# ============== Food Log Schemas ==============

class LogTypeEnum(str, Enum):
    EATEN = "eaten"
    RESISTED = "resisted"

class FoodPrediction(BaseModel):
    """Food recognition prediction"""
    category: str
    confidence: float
    portion_multiplier: float

class NutritionInfo(BaseModel):
    """Nutritional information"""
    calories: Optional[float]
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    fiber: Optional[float]
    sugar: Optional[float]
    fdc_id: Optional[int]

class FoodLogCreate(BaseModel):
    """Create food log - used internally after image upload"""
    food_category: str
    confidence_score: float
    portion_multiplier: float = 1.0
    log_type: LogTypeEnum
    notes: Optional[str] = None
    
    # Nutrition data from USDA
    calories_per_100g: Optional[float]
    protein_per_100g: Optional[float]
    carbs_per_100g: Optional[float]
    fat_per_100g: Optional[float]
    fiber_per_100g: Optional[float]
    sugar_per_100g: Optional[float]
    fdc_id: Optional[int]

class FoodLogResponse(BaseModel):
    """Food log response"""
    id: int
    user_id: int
    image_url: str
    
    # Recognition
    food_category: str
    confidence_score: float
    portion_multiplier: float
    
    # Nutrition (estimated for actual portion)
    estimated_calories: Optional[float]
    estimated_protein: Optional[float]
    estimated_carbs: Optional[float]
    estimated_fat: Optional[float]
    
    # Type and points
    log_type: LogTypeEnum
    points_earned: int
    
    # Optional
    notes: Optional[str]
    
    # Timestamps
    logged_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageUploadResponse(BaseModel):
    """Response after image upload and processing"""
    log_id: int
    prediction: FoodPrediction
    nutrition: NutritionInfo
    points_earned: int
    message: str

# ============== Stats Schemas ==============

class DailySummary(BaseModel):
    """Daily nutrition summary"""
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meals_logged: int
    resistances_logged: int
    points_earned: int
    calorie_goal: Optional[int]
    goal_percentage: Optional[float]

class WeeklySummary(BaseModel):
    """Weekly summary"""
    week_start: str
    week_end: str
    total_calories: float
    total_resistances: int
    total_points: int
    daily_summaries: List[DailySummary]
    resistance_goal: int
    resistance_goal_met: bool

class UserStats(BaseModel):
    """User statistics"""
    total_points: int
    current_streak: int
    longest_streak: int
    total_meals_logged: int
    total_resistances: int
    average_daily_calories: Optional[float]
    most_common_foods: List[tuple[str, int]]  # (food_name, count)
    
# ============== Leaderboard Schemas ==============

class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    username: str
    total_points: int
    current_streak: int
    resistances_this_week: int

class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    entries: List[LeaderboardEntry]
    user_rank: Optional[int]
    total_users: int
