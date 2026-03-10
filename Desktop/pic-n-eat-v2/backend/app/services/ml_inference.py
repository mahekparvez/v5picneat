"""
ML Inference Service
Integrates food recognition model with backend
"""

import sys
from pathlib import Path
from PIL import Image
from typing import Dict
import logging

# Add ML model path to system path
ml_model_path = Path(__file__).parent.parent.parent.parent / "ml_model"
sys.path.append(str(ml_model_path))

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class FoodRecognitionService:
    """Food recognition service wrapper"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load the ML model"""
        try:
            from inference import FoodRecognitionInference
            
            model_path = settings.MODEL_PATH
            if not Path(model_path).exists():
                logger.warning(f"Model not found at {model_path}. Inference will be disabled.")
                return
            
            self.model = FoodRecognitionInference(
                model_path=model_path,
                use_onnx=settings.USE_ONNX,
                device=settings.MODEL_DEVICE
            )
            self.model_loaded = True
            logger.info(f"✅ Food recognition model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Model loading failed. Using fallback mode.")
            self.model_loaded = False
    
    async def predict_food(self, image: Image.Image) -> Dict:
        """
        Predict food from image
        
        Returns:
            {
                'category': str,
                'confidence': float,
                'portion_multiplier': float,
                'top_predictions': List[Tuple[str, float]]
            }
        """
        if not self.model_loaded:
            # Fallback mode - return default values
            logger.warning("Model not loaded, using fallback prediction")
            return {
                'category': 'unknown',
                'confidence': 0.5,
                'portion_multiplier': 1.0,
                'top_predictions': [('unknown', 0.5)]
            }
        
        try:
            prediction = self.model.predict(
                image=image,
                top_k=3,
                estimate_portion=True
            )
            
            logger.info(f"Predicted: {prediction['category']} (confidence: {prediction['confidence']:.2f})")
            return prediction
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return {
                'category': 'unknown',
                'confidence': 0.5,
                'portion_multiplier': 1.0,
                'top_predictions': [('unknown', 0.5)]
            }
    
    async def batch_predict(self, images: list[Image.Image]) -> list[Dict]:
        """Predict multiple images"""
        if not self.model_loaded:
            return [await self.predict_food(img) for img in images]
        
        try:
            predictions = self.model.batch_predict(images)
            return predictions
        except Exception as e:
            logger.error(f"Error during batch prediction: {e}")
            return [await self.predict_food(img) for img in images]

# Global instance
food_recognition_service = FoodRecognitionService()
