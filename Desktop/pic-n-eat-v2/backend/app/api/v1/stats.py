"""
Statistics and Analytics API Routes
FIXED VERSION - No Pydantic issues
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.models.database import User, FoodLog, LogType
from app.schemas.schemas import (
    DailySummary,
    WeeklySummary,
    UserStats,
    LeaderboardResponse,
    LeaderboardEntry
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/stats")

@router.get("/daily", response_model=DailySummary)
async def get_daily_summary(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily nutrition summary"""
    
    # Parse date
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.utcnow().date()
    else:
        target_date = datetime.utcnow().date()
    
    # Get logs for the day
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= start_of_day,
        FoodLog.logged_at <= end_of_day
    ).all()
    
    # Calculate totals
    total_calories = sum(log.estimated_calories or 0 for log in logs if log.log_type == LogType.EATEN)
    total_protein = sum(log.estimated_protein or 0 for log in logs if log.log_type == LogType.EATEN)
    total_carbs = sum(log.estimated_carbs or 0 for log in logs if log.log_type == LogType.EATEN)
    total_fat = sum(log.estimated_fat or 0 for log in logs if log.log_type == LogType.EATEN)
    
    meals_logged = sum(1 for log in logs if log.log_type == LogType.EATEN)
    resistances_logged = sum(1 for log in logs if log.log_type == LogType.RESISTED)
    points_earned = sum(log.points_earned for log in logs)
    
    # Calculate goal percentage
    goal_percentage = None
    if current_user.daily_calorie_goal:
        goal_percentage = (total_calories / current_user.daily_calorie_goal) * 100
    
    return DailySummary(
        date=target_date.isoformat(),
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        meals_logged=meals_logged,
        resistances_logged=resistances_logged,
        points_earned=points_earned,
        calorie_goal=current_user.daily_calorie_goal,
        goal_percentage=goal_percentage
    )

@router.get("/weekly", response_model=WeeklySummary)
async def get_weekly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly summary"""
    
    # Calculate week boundaries
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get daily summaries for each day
    daily_summaries = []
    total_calories = 0
    total_resistances = 0
    total_points = 0
    
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.isoformat()
        
        # Reuse daily summary logic
        start_of_day = datetime.combine(day, datetime.min.time())
        end_of_day = datetime.combine(day, datetime.max.time())
        
        logs = db.query(FoodLog).filter(
            FoodLog.user_id == current_user.id,
            FoodLog.logged_at >= start_of_day,
            FoodLog.logged_at <= end_of_day
        ).all()
        
        day_calories = sum(log.estimated_calories or 0 for log in logs if log.log_type == LogType.EATEN)
        day_resistances = sum(1 for log in logs if log.log_type == LogType.RESISTED)
        day_points = sum(log.points_earned for log in logs)
        
        daily_summaries.append(DailySummary(
            date=day_str,
            total_calories=day_calories,
            total_protein=sum(log.estimated_protein or 0 for log in logs if log.log_type == LogType.EATEN),
            total_carbs=sum(log.estimated_carbs or 0 for log in logs if log.log_type == LogType.EATEN),
            total_fat=sum(log.estimated_fat or 0 for log in logs if log.log_type == LogType.EATEN),
            meals_logged=sum(1 for log in logs if log.log_type == LogType.EATEN),
            resistances_logged=day_resistances,
            points_earned=day_points,
            calorie_goal=current_user.daily_calorie_goal,
            goal_percentage=(day_calories / current_user.daily_calorie_goal * 100) if current_user.daily_calorie_goal else None
        ))
        
        total_calories += day_calories
        total_resistances += day_resistances
        total_points += day_points
    
    return WeeklySummary(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        total_calories=total_calories,
        total_resistances=total_resistances,
        total_points=total_points,
        daily_summaries=daily_summaries,
        resistance_goal=current_user.weekly_resistance_goal,
        resistance_goal_met=total_resistances >= current_user.weekly_resistance_goal
    )

@router.get("/overview", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall user statistics"""
    
    # Total meals and resistances
    total_meals = db.query(func.count(FoodLog.id)).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.log_type == LogType.EATEN
    ).scalar() or 0
    
    total_resistances = db.query(func.count(FoodLog.id)).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.log_type == LogType.RESISTED
    ).scalar() or 0
    
    # Average daily calories (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.log_type == LogType.EATEN,
        FoodLog.logged_at >= thirty_days_ago
    ).all()
    
    if recent_logs:
        total_cal = sum(log.estimated_calories or 0 for log in recent_logs)
        days_with_logs = len(set(log.logged_at.date() for log in recent_logs))
        average_daily_calories = total_cal / max(days_with_logs, 1)
    else:
        average_daily_calories = None
    
    # Most common foods
    food_counts = db.query(
        FoodLog.food_category,
        func.count(FoodLog.id).label('count')
    ).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.log_type == LogType.EATEN
    ).group_by(FoodLog.food_category).order_by(desc('count')).limit(5).all()
    
    most_common_foods = [(food, count) for food, count in food_counts]
    
    return UserStats(
        total_points=current_user.total_points,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        total_meals_logged=total_meals,
        total_resistances=total_resistances,
        average_daily_calories=average_daily_calories,
        most_common_foods=most_common_foods
    )

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get global leaderboard"""
    
    # Get top users by points
    top_users = db.query(User).filter(
        User.is_active == True
    ).order_by(desc(User.total_points)).limit(limit).all()
    
    # Calculate weekly resistances for each user
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    
    leaderboard_entries = []
    user_rank = None
    
    for idx, user in enumerate(top_users, 1):
        weekly_resistances = db.query(func.count(FoodLog.id)).filter(
            FoodLog.user_id == user.id,
            FoodLog.log_type == LogType.RESISTED,
            FoodLog.logged_at >= week_start
        ).scalar() or 0
        
        leaderboard_entries.append(LeaderboardEntry(
            rank=idx,
            username=user.username,
            total_points=user.total_points,
            current_streak=user.current_streak,
            resistances_this_week=weekly_resistances
        ))
        
        if user.id == current_user.id:
            user_rank = idx
    
    # If current user not in top, calculate their rank
    if user_rank is None:
        higher_ranked = db.query(func.count(User.id)).filter(
            User.total_points > current_user.total_points,
            User.is_active == True
        ).scalar()
        user_rank = higher_ranked + 1
    
    total_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    return LeaderboardResponse(
        entries=leaderboard_entries,
        user_rank=user_rank,
        total_users=total_users
    )
