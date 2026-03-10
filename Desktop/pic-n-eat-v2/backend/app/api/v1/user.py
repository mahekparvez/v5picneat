"""
User Management API Routes  
ULTIMATE VERSION - Works with new verify_token
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.database import User
from app.schemas.schemas import UserResponse, UserUpdate
from app.services.auth import verify_token
from app.services.gamification import gamification_service

router = APIRouter(prefix="/user")

def get_current_user_inline(authorization: Optional[str], db: Session) -> User:
    """Inline auth helper"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception
    
    token = authorization.replace("Bearer ", "")
    
    # Verify token - now returns None instead of raising
    token_data = verify_token(token)
    if not token_data:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise credentials_exception
    
    return user

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    current_user = get_current_user_inline(authorization, db)
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    current_user = get_current_user_inline(authorization, db)
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.daily_calorie_goal is not None:
        current_user.daily_calorie_goal = user_update.daily_calorie_goal
    
    if user_update.weekly_resistance_goal is not None:
        current_user.weekly_resistance_goal = user_update.weekly_resistance_goal
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/achievements")
async def get_achievements(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get user's achievements and progress"""
    current_user = get_current_user_inline(authorization, db)
    achievements = gamification_service.get_achievement_status(db, current_user)
    return achievements