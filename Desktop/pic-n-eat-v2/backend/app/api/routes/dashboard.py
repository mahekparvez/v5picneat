from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Dict

from app.db.base import get_db
from app.models.models import User, FoodLog, ResistanceLog, Achievement
from app.api.routes.auth import get_current_user
from app.services.gamification_service import get_gamification

router = APIRouter(prefix="/user", tags=["user_dashboard"])


class DashboardResponse(BaseModel):
    # User info
    email: str
    full_name: str | None
    daily_calorie_goal: int
    
    # Gamification
    total_points: int
    current_streak: int
    longest_streak: int
    
    # Today's stats
    today_calories: float
    today_foods_logged: int
    today_resistances: int
    today_points_earned: int
    
    # Week stats
    week_calories: float
    week_avg_daily_calories: float
    week_foods_logged: int
    week_resistances: int
    week_calories_resisted: float
    
    # Top foods
    top_foods_this_week: List[Dict]
    
    # Recent achievements
    recent_achievements: List[Dict]
    
    # Streaks and milestones
    next_streak_milestone: Dict | None
    points_to_next_achievement: int


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete user dashboard with all stats.
    
    This is your home screen data - everything in one request!
    """
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    # Today's food stats
    today_food = db.query(
        func.sum(FoodLog.calories).label("calories"),
        func.count(FoodLog.id).label("count")
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= today_start
    ).first()
    
    # Today's resistance stats
    today_resistance = db.query(
        func.count(ResistanceLog.id).label("count"),
        func.sum(ResistanceLog.points_earned).label("points")
    ).filter(
        ResistanceLog.user_id == current_user.id,
        ResistanceLog.resisted_at >= today_start
    ).first()
    
    # Week food stats
    week_food = db.query(
        func.sum(FoodLog.calories).label("calories"),
        func.count(FoodLog.id).label("count")
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= week_start
    ).first()
    
    # Week resistance stats
    week_resistance = db.query(
        func.count(ResistanceLog.id).label("count"),
        func.sum(ResistanceLog.estimated_calories).label("calories")
    ).filter(
        ResistanceLog.user_id == current_user.id,
        ResistanceLog.resisted_at >= week_start
    ).first()
    
    # Top foods this week
    top_foods = db.query(
        FoodLog.food_name,
        func.count(FoodLog.id).label("count"),
        func.sum(FoodLog.calories).label("total_calories")
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= week_start
    ).group_by(FoodLog.food_name).order_by(
        func.count(FoodLog.id).desc()
    ).limit(5).all()
    
    # Recent achievements
    achievements = db.query(Achievement).filter(
        Achievement.user_id == current_user.id
    ).order_by(Achievement.unlocked_at.desc()).limit(3).all()
    
    # Next streak milestone
    current_streak = current_user.current_streak
    milestones = [7, 30, 100]
    next_milestone = None
    for milestone in milestones:
        if current_streak < milestone:
            next_milestone = {
                "days": milestone,
                "days_remaining": milestone - current_streak,
                "reward_points": 50 if milestone == 7 else (200 if milestone == 30 else 1000)
            }
            break
    
    return DashboardResponse(
        # User info
        email=current_user.email,
        full_name=current_user.full_name,
        daily_calorie_goal=current_user.daily_calorie_goal,
        
        # Gamification
        total_points=current_user.total_points,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        
        # Today's stats
        today_calories=today_food.calories or 0,
        today_foods_logged=today_food.count or 0,
        today_resistances=today_resistance.count or 0,
        today_points_earned=today_resistance.points or 0,
        
        # Week stats
        week_calories=week_food.calories or 0,
        week_avg_daily_calories=(week_food.calories or 0) / 7,
        week_foods_logged=week_food.count or 0,
        week_resistances=week_resistance.count or 0,
        week_calories_resisted=week_resistance.calories or 0,
        
        # Top foods
        top_foods_this_week=[
            {
                "name": food.food_name,
                "count": food.count,
                "total_calories": food.total_calories
            }
            for food in top_foods
        ],
        
        # Achievements
        recent_achievements=[
            {
                "title": a.title,
                "description": a.description,
                "points": a.points_awarded,
                "unlocked_at": a.unlocked_at.isoformat()
            }
            for a in achievements
        ],
        
        # Milestones
        next_streak_milestone=next_milestone,
        points_to_next_achievement=100  # Placeholder
    )


@router.get("/points")
async def get_points_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed points breakdown."""
    gamification = get_gamification()
    return gamification.get_user_stats(db, str(current_user.id))


@router.get("/streaks")
async def get_streak_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed streak information.
    
    Returns current streak, longest streak, and milestone progress.
    """
    current_streak = current_user.current_streak
    
    milestones = [
        {"days": 7, "reward": 50, "title": "Week Warrior"},
        {"days": 30, "reward": 200, "title": "Monthly Master"},
        {"days": 100, "reward": 1000, "title": "Century Champion"}
    ]
    
    next_milestone = None
    completed_milestones = []
    
    for milestone in milestones:
        if current_streak >= milestone["days"]:
            completed_milestones.append(milestone)
        elif next_milestone is None:
            next_milestone = {
                **milestone,
                "days_remaining": milestone["days"] - current_streak,
                "progress": (current_streak / milestone["days"]) * 100
            }
    
    return {
        "current_streak": current_streak,
        "longest_streak": current_user.longest_streak,
        "last_activity": current_user.last_activity_date.isoformat() if current_user.last_activity_date else None,
        "next_milestone": next_milestone,
        "completed_milestones": completed_milestones
    }
