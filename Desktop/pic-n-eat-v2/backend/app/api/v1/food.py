"""
Food Logging API Routes
PRODUCTION-READY VERSION - Inline auth, uses Cloudinary
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from PIL import Image
import io
from typing import Optional

from app.core.database import get_db
from app.models.database import User, FoodLog, LogType
from app.schemas.schemas import (
    FoodLogResponse,
    ImageUploadResponse,
    LogTypeEnum,
    FoodPrediction,
    NutritionInfo
)
from app.services.auth import verify_token
from app.services.storage import cloudinary_storage
from app.services.ml_inference import food_recognition_service
from app.services.usda_fdc import usda_service
from app.services.gamification import gamification_service
from app.core.config import get_settings

router = APIRouter(prefix="/food")
settings = get_settings()

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
    token_data = verify_token(token, credentials_exception)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise credentials_exception
    
    return user

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_food_image(
    file: UploadFile = File(...),
    log_type: LogTypeEnum = Form(...),
    notes: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Upload food image and create log entry"""
    
    current_user = get_current_user_inline(authorization, db)
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit"
        )
    
    try:
        # Load image
        image = Image.open(io.BytesIO(contents))
        
        # Step 1: Run food recognition
        prediction = await food_recognition_service.predict_food(image)
        food_category = prediction['category']
        confidence = prediction['confidence']
        portion_multiplier = prediction['portion_multiplier']
        
        # Step 2: Fetch nutritional data
        nutrition_data = await usda_service.get_nutrition_cached(db, food_category)
        
        if not nutrition_data:
            nutrition_data = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'sugar': 0,
                'fdc_id': None
            }
        
        # Step 3: Calculate portion-adjusted nutrition
        portion_nutrition = usda_service.calculate_portion_nutrition(
            nutrition_data,
            portion_multiplier
        )
        
        # Step 4: Calculate points
        points_earned = gamification_service.calculate_points(
            log_type=LogType(log_type.value),
            current_streak=current_user.current_streak,
            confidence_score=confidence
        )
        
        # Step 5: Update user streak (if resistance)
        if log_type == LogTypeEnum.RESISTED:
            new_streak, is_record = gamification_service.update_streak(
                db, current_user, LogType.RESISTED
            )
        
        # Step 6: Upload image to Cloudinary
        s3_key, image_url = await cloudinary_storage.upload_image(
            image=image,
            user_id=current_user.id,
            file_extension="jpg"
        )
        
        # Step 7: Create food log entry
        food_log = FoodLog(
            user_id=current_user.id,
            image_url=image_url,
            image_s3_key=s3_key,
            food_category=food_category,
            confidence_score=confidence,
            portion_multiplier=portion_multiplier,
            log_type=LogType(log_type.value),
            calories_per_100g=nutrition_data.get('calories'),
            protein_per_100g=nutrition_data.get('protein'),
            carbs_per_100g=nutrition_data.get('carbs'),
            fat_per_100g=nutrition_data.get('fat'),
            fiber_per_100g=nutrition_data.get('fiber'),
            sugar_per_100g=nutrition_data.get('sugar'),
            fdc_id=nutrition_data.get('fdc_id'),
            estimated_calories=portion_nutrition.get('estimated_calories'),
            estimated_protein=portion_nutrition.get('estimated_protein'),
            estimated_carbs=portion_nutrition.get('estimated_carbs'),
            estimated_fat=portion_nutrition.get('estimated_fat'),
            points_earned=points_earned,
            notes=notes
        )
        
        db.add(food_log)
        current_user.total_points += points_earned
        db.commit()
        db.refresh(food_log)
        
        # Prepare response message
        if log_type == LogTypeEnum.RESISTED:
            message = f"💪 Great job resisting! +{points_earned} points. Current streak: {current_user.current_streak} days!"
        else:
            message = f"📝 Meal logged! +{points_earned} points. Estimated: {portion_nutrition.get('estimated_calories', 0):.0f} cal"
        
        return ImageUploadResponse(
            log_id=food_log.id,
            prediction=FoodPrediction(
                category=food_category,
                confidence=confidence,
                portion_multiplier=portion_multiplier
            ),
            nutrition=NutritionInfo(**nutrition_data),
            points_earned=points_earned,
            message=message
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    limit: int = 50,
    offset: int = 0,
    log_type: Optional[LogTypeEnum] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get user's food logs"""
    current_user = get_current_user_inline(authorization, db)
    
    query = db.query(FoodLog).filter(FoodLog.user_id == current_user.id)
    
    if log_type:
        query = query.filter(FoodLog.log_type == LogType(log_type.value))
    
    logs = query.order_by(FoodLog.logged_at.desc()).offset(offset).limit(limit).all()
    return logs

@router.get("/logs/{log_id}", response_model=FoodLogResponse)
async def get_food_log(
    log_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get specific food log"""
    current_user = get_current_user_inline(authorization, db)
    
    log = db.query(FoodLog).filter(
        FoodLog.id == log_id,
        FoodLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found"
        )
    
    return log

@router.delete("/logs/{log_id}")
async def delete_food_log(
    log_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Delete a food log"""
    current_user = get_current_user_inline(authorization, db)
    
    log = db.query(FoodLog).filter(
        FoodLog.id == log_id,
        FoodLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found"
        )
    
    # Delete image from Cloudinary
    await cloudinary_storage.delete_image(log.image_s3_key)
    
    # Deduct points
    current_user.total_points -= log.points_earned
    if current_user.total_points < 0:
        current_user.total_points = 0
    
    db.delete(log)
    db.commit()
    
    return {"message": "Food log deleted successfully"}
