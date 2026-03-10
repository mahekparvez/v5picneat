from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import User, PointsHistory, Achievement
from app.core.config import get_settings
from typing import Dict, Optional

settings = get_settings()


class GamificationService:
    """Service for managing points, streaks, and achievements."""
    
    def calculate_resistance_points(
        self,
        calories: float,
        resisted_at: datetime
    ) -> Dict[str, any]:
        """
        Calculate points for resisting food.
        
        Bonuses:
        - High calorie food (>500 cal): +5 points
        - Late night resistance (after 10 PM): +3 points
        
        Returns:
            {
                "base_points": 10,
                "bonus_points": 8,
                "total_points": 18,
                "bonus_reasons": ["high_calorie", "late_night"]
            }
        """
        base_points = settings.RESISTANCE_BASE_POINTS
        bonus_points = 0
        bonus_reasons = []
        
        # High calorie bonus
        if calories >= settings.HIGH_CALORIE_THRESHOLD:
            bonus_points += settings.HIGH_CALORIE_BONUS
            bonus_reasons.append("high_calorie")
        
        # Late night bonus
        if resisted_at.hour >= settings.LATE_NIGHT_HOUR:
            bonus_points += settings.LATE_NIGHT_BONUS
            bonus_reasons.append("late_night")
        
        return {
            "base_points": base_points,
            "bonus_points": bonus_points,
            "total_points": base_points + bonus_points,
            "bonus_reasons": bonus_reasons
        }
    
    def award_points(
        self,
        db: Session,
        user_id: str,
        points: int,
        action_type: str,
        description: Optional[str] = None,
        related_log_id: Optional[str] = None,
        related_log_type: Optional[str] = None
    ) -> PointsHistory:
        """
        Award points to a user and update their total.
        
        Args:
            db: Database session
            user_id: User UUID
            points: Points to award
            action_type: Type of action (resistance, streak_bonus, achievement)
            description: Optional description
            related_log_id: Optional related log UUID
            related_log_type: Optional log type (food_log, resistance_log)
        
        Returns:
            Created PointsHistory record
        """
        # Create points history record
        points_record = PointsHistory(
            user_id=user_id,
            points=points,
            action_type=action_type,
            description=description,
            related_log_id=related_log_id,
            related_log_type=related_log_type
        )
        db.add(points_record)
        
        # Update user's total points
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.total_points += points
        
        db.commit()
        db.refresh(points_record)
        
        return points_record
    
    def update_streak(
        self,
        db: Session,
        user_id: str,
        activity_date: datetime
    ) -> Dict[str, any]:
        """
        Update user's streak based on new activity.
        
        Rules:
        - Activity today = maintain/increment streak
        - Missed yesterday = reset streak
        - Streak bonuses at milestones (7, 30, 100 days)
        
        Returns:
            {
                "current_streak": 5,
                "longest_streak": 12,
                "streak_bonus_awarded": 0,
                "milestone_reached": None
            }
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        today = activity_date.date()
        last_activity = user.last_activity_date.date() if user.last_activity_date else None
        
        streak_bonus_awarded = 0
        milestone_reached = None
        
        if last_activity is None:
            # First activity ever
            user.current_streak = 1
            user.last_activity_date = activity_date
        
        elif last_activity == today:
            # Already logged today, no streak change
            pass
        
        elif last_activity == today - timedelta(days=1):
            # Consecutive day - increment streak
            user.current_streak += 1
            user.last_activity_date = activity_date
            
            # Check for milestone bonuses
            if user.current_streak == 7:
                streak_bonus_awarded = 50
                milestone_reached = "7_days"
            elif user.current_streak == 30:
                streak_bonus_awarded = 200
                milestone_reached = "30_days"
            elif user.current_streak == 100:
                streak_bonus_awarded = 1000
                milestone_reached = "100_days"
            
            # Award bonus if milestone reached
            if streak_bonus_awarded > 0:
                self.award_points(
                    db, user_id, streak_bonus_awarded,
                    "streak_bonus",
                    f"{milestone_reached} streak milestone"
                )
        
        else:
            # Missed a day - reset streak
            user.current_streak = 1
            user.last_activity_date = activity_date
        
        # Update longest streak
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
        
        db.commit()
        db.refresh(user)
        
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "streak_bonus_awarded": streak_bonus_awarded,
            "milestone_reached": milestone_reached
        }
    
    def check_achievements(
        self,
        db: Session,
        user_id: str,
        action_type: str
    ) -> list[Achievement]:
        """
        Check if user unlocked any new achievements.
        
        Achievement types:
        - First resistance
        - 10, 50, 100 resistances
        - 30 days of consistent logging
        - Specific calorie milestones saved
        
        Returns:
            List of newly unlocked achievements
        """
        from sqlalchemy import func
        from app.models.models import ResistanceLog, FoodLog
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        new_achievements = []
        
        # Get existing achievements
        existing = db.query(Achievement).filter(
            Achievement.user_id == user_id
        ).all()
        existing_types = {a.achievement_type for a in existing}
        
        # Resistance-based achievements
        if action_type == "resistance":
            resistance_count = db.query(func.count(ResistanceLog.id)).filter(
                ResistanceLog.user_id == user_id
            ).scalar()
            
            achievements_to_check = [
                ("first_resistance", 1, "First Resistance", 25),
                ("10_resistances", 10, "Discipline Warrior", 50),
                ("50_resistances", 50, "Master of Willpower", 100),
                ("100_resistances", 100, "Resistance Legend", 250),
            ]
            
            for ach_type, threshold, title, points in achievements_to_check:
                if resistance_count >= threshold and ach_type not in existing_types:
                    achievement = Achievement(
                        user_id=user_id,
                        achievement_type=ach_type,
                        title=title,
                        description=f"Resisted {threshold} foods",
                        points_awarded=points
                    )
                    db.add(achievement)
                    new_achievements.append(achievement)
                    
                    # Award points
                    self.award_points(
                        db, user_id, points,
                        "achievement",
                        f"Unlocked: {title}"
                    )
        
        # Logging streak achievements
        if user.current_streak >= 30 and "consistent_logger" not in existing_types:
            achievement = Achievement(
                user_id=user_id,
                achievement_type="consistent_logger",
                title="Consistency Champion",
                description="Maintained a 30-day streak",
                points_awarded=150
            )
            db.add(achievement)
            new_achievements.append(achievement)
            
            self.award_points(
                db, user_id, 150,
                "achievement",
                "Unlocked: Consistency Champion"
            )
        
        db.commit()
        
        return new_achievements
    
    def get_user_stats(self, db: Session, user_id: str) -> Dict[str, any]:
        """
        Get comprehensive gamification stats for a user.
        
        Returns:
            {
                "total_points": 1250,
                "current_streak": 7,
                "longest_streak": 15,
                "total_resistances": 42,
                "total_calories_resisted": 12500,
                "achievements": [...],
                "points_breakdown": {...}
            }
        """
        from sqlalchemy import func
        from app.models.models import ResistanceLog
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get resistance stats
        resistance_stats = db.query(
            func.count(ResistanceLog.id).label("count"),
            func.sum(ResistanceLog.estimated_calories).label("total_calories")
        ).filter(ResistanceLog.user_id == user_id).first()
        
        # Get achievements
        achievements = db.query(Achievement).filter(
            Achievement.user_id == user_id
        ).order_by(Achievement.unlocked_at.desc()).all()
        
        # Get points breakdown
        points_breakdown = db.query(
            PointsHistory.action_type,
            func.sum(PointsHistory.points).label("total")
        ).filter(
            PointsHistory.user_id == user_id
        ).group_by(PointsHistory.action_type).all()
        
        return {
            "total_points": user.total_points,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "total_resistances": resistance_stats.count or 0,
            "total_calories_resisted": resistance_stats.total_calories or 0,
            "achievements": [
                {
                    "title": a.title,
                    "description": a.description,
                    "points": a.points_awarded,
                    "unlocked_at": a.unlocked_at.isoformat()
                }
                for a in achievements
            ],
            "points_breakdown": {
                action_type: total for action_type, total in points_breakdown
            }
        }


# Singleton instance
_gamification_instance = None


def get_gamification() -> GamificationService:
    """Get singleton gamification service instance."""
    global _gamification_instance
    if _gamification_instance is None:
        _gamification_instance = GamificationService()
    return _gamification_instance
