import torch
import torchvision.transforms as transforms
from PIL import Image
from typing import Dict, List, Tuple
import json
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


class FoodClassifier:
    """
    Food classification model inference service.
    Uses custom-trained model on WWEIA dataset.
    """
    
    def __init__(self, model_path: str = None):
        self.device = torch.device(
            settings.MODEL_DEVICE if torch.cuda.is_available() else "cpu"
        )
        self.model_path = model_path or settings.MODEL_PATH
        self.model = None
        self.class_names = []
        self.transforms = self._get_transforms()
        
        # Load model on initialization
        self.load_model()
    
    def load_model(self):
        """Load trained model and class names."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please train the model first using ml-pipeline/"
            )
        
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Load model architecture
        from torchvision import models
        
        # Using EfficientNet-B3 as base (better than MobileNetV2)
        self.model = models.efficientnet_b3(pretrained=False)
        num_classes = checkpoint.get("num_classes", 1000)
        
        # Modify classifier head
        in_features = self.model.classifier[1].in_features
        self.model.classifier = torch.nn.Sequential(
            torch.nn.Dropout(p=0.3),
            torch.nn.Linear(in_features, num_classes)
        )
        
        # Load weights
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()
        
        # Load class names (food labels)
        self.class_names = checkpoint.get("class_names", [])
        
        print(f"✓ Model loaded: {num_classes} classes")
        print(f"✓ Device: {self.device}")
    
    def _get_transforms(self):
        """Get image preprocessing transforms."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet stats
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    @torch.no_grad()
    def predict(
        self, 
        image: Image.Image, 
        top_k: int = 5
    ) -> List[Dict[str, any]]:
        """
        Predict food class from image.
        
        Args:
            image: PIL Image object
            top_k: Return top K predictions
        
        Returns:
            List of predictions with class name, confidence, and FDC search term
            [
                {
                    "food_name": "banana",
                    "confidence": 0.95,
                    "class_id": 42,
                    "search_term": "banana raw"
                },
                ...
            ]
        """
        # Preprocess
        image_tensor = self.transforms(image).unsqueeze(0).to(self.device)
        
        # Inference
        outputs = self.model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        # Get top K predictions
        top_probs, top_indices = torch.topk(probabilities, top_k)
        
        predictions = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            class_id = idx.item()
            confidence = prob.item()
            
            if class_id < len(self.class_names):
                food_name = self.class_names[class_id]
                
                predictions.append({
                    "food_name": food_name,
                    "confidence": round(confidence, 3),
                    "class_id": class_id,
                    "search_term": self._get_search_term(food_name)
                })
        
        return predictions
    
    def _get_search_term(self, food_name: str) -> str:
        """
        Convert model class name to USDA search term.
        
        Model might output: "banana_ripe"
        USDA search needs: "banana raw"
        """
        # Simple processing - can be enhanced with mapping dict
        term = food_name.replace("_", " ").lower()
        
        # Add "raw" for common foods if not specified
        cooking_terms = ["cooked", "fried", "baked", "grilled", "raw"]
        if not any(term in term for term in cooking_terms):
            # Default to raw for fruits/vegetables
            if any(word in term for word in ["apple", "banana", "orange", "carrot"]):
                term += " raw"
        
        return term
    
    def estimate_portion_size(self, image: Image.Image) -> float:
        """
        Estimate portion size in grams from image.
        
        This is a simplified version. For production, you'd want:
        - Depth estimation
        - Reference object detection (coin, hand, plate)
        - Known object size database
        
        Returns:
            Estimated weight in grams
        """
        # Placeholder implementation
        # TODO: Implement proper portion estimation
        
        # Default portions (very rough estimates)
        DEFAULT_PORTIONS = {
            "banana": 118,      # 1 medium banana
            "apple": 182,       # 1 medium apple
            "chicken_breast": 170,  # 6 oz
            "rice": 158,        # 1 cup cooked
            "bread": 28,        # 1 slice
        }
        
        # For now, return average portion
        return 150.0  # 150g as default
    
    def predict_with_portion(
        self, 
        image: Image.Image
    ) -> Dict[str, any]:
        """
        Complete inference pipeline: classification + portion estimation.
        
        Returns:
            {
                "predictions": [...],  # Top 5 predictions
                "top_prediction": {...},  # Most confident
                "portion_grams": 150.0,
                "needs_manual_review": False
            }
        """
        predictions = self.predict(image, top_k=5)
        portion_grams = self.estimate_portion_size(image)
        
        top_prediction = predictions[0]
        confidence_threshold = settings.CONFIDENCE_THRESHOLD
        
        return {
            "predictions": predictions,
            "top_prediction": top_prediction,
            "portion_grams": portion_grams,
            "needs_manual_review": top_prediction["confidence"] < confidence_threshold
        }


# Singleton instance
_classifier_instance = None


def get_classifier() -> FoodClassifier:
    """Get singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = FoodClassifier()
    return _classifier_instance


# Usage example:
"""
from PIL import Image
from app.services.ml_service import get_classifier

classifier = get_classifier()

# Load image
image = Image.open("food.jpg")

# Get predictions
result = classifier.predict_with_portion(image)

print(f"Food: {result['top_prediction']['food_name']}")
print(f"Confidence: {result['top_prediction']['confidence']:.2%}")
print(f"Portion: {result['portion_grams']}g")

# All predictions
for pred in result['predictions']:
    print(f"  - {pred['food_name']}: {pred['confidence']:.2%}")
"""
