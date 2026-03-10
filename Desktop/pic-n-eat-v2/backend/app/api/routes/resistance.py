from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from PIL import Image
from typing import List, Optional
from datetime import datetime, timedelta
import io
import json

from app.db.base import get_db
from app.models.models import User, ResistanceLog
from app.api.routes.auth import get_current_user
from app.services.ml_service import get_classifier
from app.services.usda_service import USDAService
from app.services.storage_service import get_storage
from app.services.gamification_service import get_gamification
from pydantic import BaseModel

router = APIRouter(prefix="/resistance", tags=["resistance_tracking"])


# Pydantic models
class ResistanceLogResponse(BaseModel):
    id: str
    food_name: str
    estimated_calories: float
    estimated_protein: float
    estimated_carbs: float
    estimated_fat: float
    points_earned: int
    bonus_reason: Optional[str]
    confidence_score: float
    notes: Optional[str]
    image_url: str
    thumbnail_url: Optional[str]
    resisted_at: datetime
    
    class Config:
        from_attributes = True


class ResistanceStatsResponse(BaseModel):
    total_resistances: int
    total_calories_resisted: float
    total_points_earned: int
    current_streak: int
    longest_streak: int
    avg_resistance_value: float


class ResistanceLeaderboardEntry(BaseModel):
    user_id: str
    full_name: Optional[str]
    total_points: int
    total_resistances: int
    current_streak: int


@router.post("/log", response_model=ResistanceLogResponse)
async def log_resistance(
    image: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a food you successfully resisted eating! 💪
    
    Process:
    1. Upload image to S3
    2. Identify food with ML
    3. Get nutrition from USDA FDC
    4. Calculate points (base + bonuses)
    5. Update streak
    6. Check for achievements
    
    Bonuses:
    - High calorie food (>500 cal): +5 points
    - Late night resistance (after 10 PM): +3 points
    
    Returns:
        Resistance log with points earned and bonuses
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Load image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Get services
        storage = get_storage()
        classifier = get_classifier()
        usda_service = USDAService()
        gamification = get_gamification()
        
        # Validate and upload image
        storage.validate_image(pil_image)
        original_url, thumbnail_url = storage.upload_food_image(
            pil_image,
            user_id=str(current_user.id),
            log_type="resistance"
        )
        
        # Run ML inference
        ml_result = classifier.predict_with_portion(pil_image)
        top_prediction = ml_result["top_prediction"]
        portion_grams = ml_result["portion_grams"]
        
        # Search USDA database
        search_results = await usda_service.search_food(
            query=top_prediction["search_term"],
            page_size=1
        )
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail=f"No nutrition data found for {top_prediction['food_name']}"
            )
        
        fdc_id = search_results[0]["fdc_id"]
        
        # Get detailed nutrition
        fdc_data = await usda_service.get_food_details(fdc_id, db)
        if not fdc_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch nutrition data"
            )
        
        # Calculate portion-adjusted nutrition
        nutrition = usda_service.calculate_nutrition_for_portion(
            fdc_data,
            portion_grams
        )
        
        # Calculate points
        resisted_at = datetime.utcnow()
        points_data = gamification.calculate_resistance_points(
            calories=nutrition["calories"],
            resisted_at=resisted_at
        )
        
        # Create resistance log
        resistance_log = ResistanceLog(
            user_id=current_user.id,
            image_url=original_url,
            thumbnail_url=thumbnail_url,
            food_name=fdc_data["food_name"],
            food_fdc_id=fdc_id,
            estimated_calories=nutrition["calories"],
            estimated_protein=nutrition["protein"],
            estimated_carbs=nutrition["carbs"],
            estimated_fat=nutrition["fat"],
            points_earned=points_data["total_points"],
            bonus_reason=", ".join(points_data["bonus_reasons"]) if points_data["bonus_reasons"] else None,
            confidence_score=top_prediction["confidence"],
            model_version="v1.0",
            notes=notes,
            resisted_at=resisted_at
        )
        
        db.add(resistance_log)
        db.commit()
        db.refresh(resistance_log)
        
        # Award points
        gamification.award_points(
            db,
            user_id=str(current_user.id),
            points=points_data["total_points"],
            action_type="resistance",
            description=f"Resisted {fdc_data['food_name']} ({nutrition['calories']:.0f} cal)",
            related_log_id=str(resistance_log.id),
            related_log_type="resistance_log"
        )
        
        # Update streak
        streak_result = gamification.update_streak(
            db,
            user_id=str(current_user.id),
            activity_date=resisted_at
        )
        
        # Check achievements
        new_achievements = gamification.check_achievements(
            db,
            user_id=str(current_user.id),
            action_type="resistance"
        )
        
        await usda_service.close()
        
        # Add streak/achievement info to response
        response_data = {
            **resistance_log.__dict__,
            "streak_updated": streak_result,
            "new_achievements": [
                {"title": a.title, "points": a.points_awarded}
                for a in new_achievements
            ] if new_achievements else []
        }
        
        return resistance_log
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging resistance: {str(e)}")


@router.get("/logs", response_model=List[ResistanceLogResponse])
async def get_resistance_logs(
    skip: int = 0,
    limit: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's resistance logs.
    
    Shows your history of discipline! 🏆
    """
    query = db.query(ResistanceLog).filter(ResistanceLog.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        query = query.filter(ResistanceLog.resisted_at >= start_date)
    if end_date:
        query = query.filter(ResistanceLog.resisted_at <= end_date)
    
    # Order by most recent
    query = query.order_by(ResistanceLog.resisted_at.desc())
    
    # Pagination
    logs = query.offset(skip).limit(min(limit, 100)).all()
    
    return logs


@router.get("/stats", response_model=ResistanceStatsResponse)
async def get_resistance_stats(
    period: str = "all",  # today, week, month, all
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get resistance statistics.
    
    See how much you've resisted! 💪
    """
    query = db.query(ResistanceLog).filter(ResistanceLog.user_id == current_user.id)
    
    # Filter by period
    now = datetime.utcnow()
    if period == "today":
        start_time = now - timedelta(days=1)
        query = query.filter(ResistanceLog.resisted_at >= start_time)
    elif period == "week":
        start_time = now - timedelta(days=7)
        query = query.filter(ResistanceLog.resisted_at >= start_time)
    elif period == "month":
        start_time = now - timedelta(days=30)
        query = query.filter(ResistanceLog.resisted_at >= start_time)
    
    # Aggregate stats
    stats = query.with_entities(
        func.count(ResistanceLog.id).label("total_resistances"),
        func.sum(ResistanceLog.estimated_calories).label("total_calories"),
        func.sum(ResistanceLog.points_earned).label("total_points"),
        func.avg(ResistanceLog.estimated_calories).label("avg_calories")
    ).first()
    
    return ResistanceStatsResponse(
        total_resistances=stats.total_resistances or 0,
        total_calories_resisted=stats.total_calories or 0,
        total_points_earned=stats.total_points or 0,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        avg_resistance_value=round(stats.avg_calories or 0, 1)
    )


@router.get("/leaderboard", response_model=List[ResistanceLeaderboardEntry])
async def get_leaderboard(
    period: str = "week",  # week, month, all
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get resistance leaderboard.
    
    See who's the most disciplined! 🏆
    
    Rankings based on total points earned from resistances.
    """
    # This is a simplified version - you might want to add time-based filtering
    users = db.query(User).order_by(User.total_points.desc()).limit(limit).all()
    
    leaderboard = []
    for user in users:
        resistance_count = db.query(func.count(ResistanceLog.id)).filter(
            ResistanceLog.user_id == user.id
        ).scalar()
        
        leaderboard.append(
            ResistanceLeaderboardEntry(
                user_id=str(user.id),
                full_name=user.full_name or "Anonymous",
                total_points=user.total_points,
                total_resistances=resistance_count,
                current_streak=user.current_streak
            )
        )
    
    return leaderboard


@router.delete("/logs/{log_id}")
async def delete_resistance_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resistance log."""
    resistance_log = db.query(ResistanceLog).filter(
        and_(
            ResistanceLog.id == log_id,
            ResistanceLog.user_id == current_user.id
        )
    ).first()
    
    if not resistance_log:
        raise HTTPException(status_code=404, detail="Resistance log not found")
    
    # Note: You might want to deduct points when deleting
    # For now, we'll just delete the log
    
    db.delete(resistance_log)
    db.commit()
    
    return {"message": "Resistance log deleted successfully"}


@router.get("/logs/{log_id}", response_model=ResistanceLogResponse)
async def get_resistance_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resistance log by ID."""
    resistance_log = db.query(ResistanceLog).filter(
        and_(
            ResistanceLog.id == log_id,
            ResistanceLog.user_id == current_user.id
        )
    ).first()
    
    if not resistance_log:
        raise HTTPException(status_code=404, detail="Resistance log not found")
    
    return resistance_log
