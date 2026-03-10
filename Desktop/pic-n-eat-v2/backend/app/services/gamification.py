"""
Gamification Service
Handles points, streaks, and achievements for Pic N Eat
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Tuple
import logging

from app.models.database import User, FoodLog, LogType
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class GamificationService:
    """Service for managing points and gamification features"""
    
    @staticmethod
    def calculate_points(
        log_type: LogType,
        current_streak: int = 0,
        confidence_score: float = 1.0
    ) -> int:
        """
        Calculate points earned for a food log
        
        Args:
            log_type: Type of log (eaten or resisted)
            current_streak: Current resistance streak
            confidence_score: ML model confidence (0-1)
        
        Returns:
            Points earned
        """
        if log_type == LogType.EATEN:
            # Base points for logging a meal
            points = settings.POINTS_PER_MEAL_LOGGED
            
            # Bonus for high confidence
            if confidence_score > 0.9:
                points += 2
        else:  # RESISTED
            # Higher base points for resistance
            points = settings.POINTS_PER_RESISTANCE
            
            # Streak bonus
            if current_streak > 0:
                streak_bonus = int(
                    points * (settings.RESISTANCE_STREAK_MULTIPLIER - 1) *
                    min(current_streak / 7, 1.0)  # Max bonus at 7-day streak
                )
                points += streak_bonus
        
        return points
    
    @staticmethod
    def update_streak(db: Session, user: User, log_type: LogType) -> Tuple[int, bool]:
        """
        Update user's resistance streak
        
        Returns:
            Tuple[current_streak, is_new_record]
        """
        if log_type != LogType.RESISTED:
            return user.current_streak, False
        
        # Get last resistance log
        last_resistance = db.query(FoodLog).filter(
            FoodLog.user_id == user.id,
            FoodLog.log_type == LogType.RESISTED
        ).order_by(FoodLog.logged_at.desc()).first()
        
        if not last_resistance:
            # First resistance ever
            user.current_streak = 1
        else:
            # Check if within 48 hours
            time_diff = datetime.utcnow() - last_resistance.logged_at
            if time_diff <= timedelta(hours=48):
                user.current_streak += 1
            else:
                # Streak broken
                user.current_streak = 1
        
        # Check if new record
        is_new_record = False
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
            is_new_record = True
            logger.info(f"🎉 New streak record for user {user.id}: {user.current_streak} days!")
        
        db.commit()
        
        return user.current_streak, is_new_record
    
    @staticmethod
    def check_and_reset_streak(db: Session, user: User) -> bool:
        """
        Check if streak should be reset (called periodically)
        Returns True if streak was reset
        """
        if user.current_streak == 0:
            return False
        
        # Get last resistance log
        last_resistance = db.query(FoodLog).filter(
            FoodLog.user_id == user.id,
            FoodLog.log_type == LogType.RESISTED
        ).order_by(FoodLog.logged_at.desc()).first()
        
        if not last_resistance:
            return False
        
        # Reset if more than 48 hours since last resistance
        time_diff = datetime.utcnow() - last_resistance.logged_at
        if time_diff > timedelta(hours=48):
            logger.info(f"Resetting streak for user {user.id} (last resistance: {time_diff.days} days ago)")
            user.current_streak = 0
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_weekly_resistance_count(db: Session, user_id: int) -> int:
        """Get number of resistances this week"""
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        count = db.query(func.count(FoodLog.id)).filter(
            FoodLog.user_id == user_id,
            FoodLog.log_type == LogType.RESISTED,
            FoodLog.logged_at >= week_start
        ).scalar()
        
        return count or 0
    
    @staticmethod
    def get_achievement_status(db: Session, user: User) -> dict:
        """
        Get user's achievement status
        
        Returns various achievements and progress
        """
        # Total stats
        total_meals = db.query(func.count(FoodLog.id)).filter(
            FoodLog.user_id == user.id,
            FoodLog.log_type == LogType.EATEN
        ).scalar() or 0
        
        total_resistances = db.query(func.count(FoodLog.id)).filter(
            FoodLog.user_id == user.id,
            FoodLog.log_type == LogType.RESISTED
        ).scalar() or 0
        
        # Weekly goal progress
        weekly_resistances = GamificationService.get_weekly_resistance_count(db, user.id)
        weekly_goal_met = weekly_resistances >= user.weekly_resistance_goal
        
        # Achievement milestones
        achievements = []
        
        if total_resistances >= 1:
            achievements.append("🎯 First Resistance")
        if total_resistances >= 10:
            achievements.append("💪 Discipline Apprentice (10 resistances)")
        if total_resistances >= 50:
            achievements.append("🔥 Willpower Warrior (50 resistances)")
        if total_resistances >= 100:
            achievements.append("👑 Self-Control Master (100 resistances)")
        
        if user.longest_streak >= 3:
            achievements.append("⚡ 3-Day Streak")
        if user.longest_streak >= 7:
            achievements.append("🌟 Week Warrior")
        if user.longest_streak >= 30:
            achievements.append("💎 Month Master")
        
        if total_meals >= 100:
            achievements.append("📊 Nutrition Tracker (100 meals logged)")
        
        return {
            "total_meals": total_meals,
            "total_resistances": total_resistances,
            "weekly_resistances": weekly_resistances,
            "weekly_goal": user.weekly_resistance_goal,
            "weekly_goal_met": weekly_goal_met,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "total_points": user.total_points,
            "achievements": achievements
        }

# Global instance
gamification_service = GamificationService()
