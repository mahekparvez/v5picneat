from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from PIL import Image
from typing import List, Optional
from datetime import datetime, timedelta
import io
import json

from app.db.base import get_db
from app.models.models import User, FoodLog
from app.api.routes.auth import get_current_user
from app.services.ml_service import get_classifier
from app.services.usda_service import USDAService
from app.services.storage_service import get_storage
from pydantic import BaseModel

router = APIRouter(prefix="/food", tags=["food_logging"])


# Pydantic models
class FoodLogResponse(BaseModel):
    id: str
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    portion_size: Optional[float]
    serving_description: Optional[str]
    confidence_score: float
    meal_type: Optional[str]
    notes: Optional[str]
    image_url: str
    thumbnail_url: Optional[str]
    logged_at: datetime
    
    class Config:
        from_attributes = True


class FoodStatsResponse(BaseModel):
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int
    avg_confidence: float


@router.post("/log", response_model=FoodLogResponse)
async def log_food(
    image: UploadFile = File(...),
    meal_type: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a food item by uploading an image.
    
    Process:
    1. Upload image to S3
    2. Run ML inference to identify food
    3. Lookup nutrition data from USDA FDC
    4. Calculate portion-adjusted nutrition
    5. Save to database
    
    Returns:
        Complete food log with nutrition data
    """
    # Validate image
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
        
        # Validate and upload image
        storage.validate_image(pil_image)
        original_url, thumbnail_url = storage.upload_food_image(
            pil_image,
            user_id=str(current_user.id),
            log_type="food"
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
        
        # Create food log
        food_log = FoodLog(
            user_id=current_user.id,
            image_url=original_url,
            thumbnail_url=thumbnail_url,
            food_name=fdc_data["food_name"],
            food_fdc_id=fdc_id,
            calories=nutrition["calories"],
            protein=nutrition["protein"],
            carbs=nutrition["carbs"],
            fat=nutrition["fat"],
            fiber=nutrition["fiber"],
            portion_size=portion_grams,
            serving_description=f"{portion_grams}g",
            confidence_score=top_prediction["confidence"],
            model_version="v1.0",
            alternative_predictions=json.dumps(ml_result["predictions"][:5]),
            meal_type=meal_type,
            notes=notes
        )
        
        db.add(food_log)
        db.commit()
        db.refresh(food_log)
        
        await usda_service.close()
        
        return food_log
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing food: {str(e)}")


@router.get("/logs", response_model=List[FoodLogResponse])
async def get_food_logs(
    skip: int = 0,
    limit: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meal_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's food logs with optional filters.
    
    Query params:
    - skip: Number of records to skip (pagination)
    - limit: Max records to return (max 100)
    - start_date: Filter by date range start
    - end_date: Filter by date range end
    - meal_type: Filter by meal type (breakfast, lunch, dinner, snack)
    """
    query = db.query(FoodLog).filter(FoodLog.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        query = query.filter(FoodLog.logged_at >= start_date)
    if end_date:
        query = query.filter(FoodLog.logged_at <= end_date)
    if meal_type:
        query = query.filter(FoodLog.meal_type == meal_type)
    
    # Order by most recent
    query = query.order_by(FoodLog.logged_at.desc())
    
    # Pagination
    logs = query.offset(skip).limit(min(limit, 100)).all()
    
    return logs


@router.get("/logs/stats", response_model=FoodStatsResponse)
async def get_food_stats(
    period: str = "today",  # today, week, month, all
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated nutrition statistics.
    
    Periods:
    - today: Last 24 hours
    - week: Last 7 days
    - month: Last 30 days
    - all: All time
    """
    query = db.query(FoodLog).filter(FoodLog.user_id == current_user.id)
    
    # Filter by period
    now = datetime.utcnow()
    if period == "today":
        start_time = now - timedelta(days=1)
        query = query.filter(FoodLog.logged_at >= start_time)
    elif period == "week":
        start_time = now - timedelta(days=7)
        query = query.filter(FoodLog.logged_at >= start_time)
    elif period == "month":
        start_time = now - timedelta(days=30)
        query = query.filter(FoodLog.logged_at >= start_time)
    
    # Aggregate stats
    stats = query.with_entities(
        func.sum(FoodLog.calories).label("total_calories"),
        func.sum(FoodLog.protein).label("total_protein"),
        func.sum(FoodLog.carbs).label("total_carbs"),
        func.sum(FoodLog.fat).label("total_fat"),
        func.count(FoodLog.id).label("meal_count"),
        func.avg(FoodLog.confidence_score).label("avg_confidence")
    ).first()
    
    return FoodStatsResponse(
        total_calories=stats.total_calories or 0,
        total_protein=stats.total_protein or 0,
        total_carbs=stats.total_carbs or 0,
        total_fat=stats.total_fat or 0,
        meal_count=stats.meal_count or 0,
        avg_confidence=round(stats.avg_confidence or 0, 3)
    )


@router.delete("/logs/{log_id}")
async def delete_food_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a food log."""
    food_log = db.query(FoodLog).filter(
        and_(
            FoodLog.id == log_id,
            FoodLog.user_id == current_user.id
        )
    ).first()
    
    if not food_log:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    # Delete from storage
    storage = get_storage()
    # Extract S3 key from URL (implementation depends on URL structure)
    # storage.delete_image(s3_key)
    
    db.delete(food_log)
    db.commit()
    
    return {"message": "Food log deleted successfully"}


@router.get("/logs/{log_id}", response_model=FoodLogResponse)
async def get_food_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific food log by ID."""
    food_log = db.query(FoodLog).filter(
        and_(
            FoodLog.id == log_id,
            FoodLog.user_id == current_user.id
        )
    ).first()
    
    if not food_log:
        raise HTTPException(status_code=404, detail="Food log not found")
    
    return food_log
