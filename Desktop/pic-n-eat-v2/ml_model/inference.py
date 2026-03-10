"""
Food Recognition Inference Module
Optimized for production use with ONNX runtime
"""

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple
import onnxruntime as ort
import cv2

class FoodRecognitionInference:
    """
    Production-ready inference class for food recognition
    """
    
    def __init__(
        self,
        model_path: str,
        use_onnx: bool = True,
        device: str = "cpu"
    ):
        self.device = device
        self.use_onnx = use_onnx
        
        # Load class mapping
        checkpoint = torch.load(model_path, map_location=device)
        self.class_to_idx = checkpoint['class_to_idx']
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
        
        if use_onnx:
            # Use ONNX for faster inference
            onnx_path = str(Path(model_path).parent / "model.onnx")
            if Path(onnx_path).exists():
                self.session = ort.InferenceSession(
                    onnx_path,
                    providers=['CPUExecutionProvider']
                )
                self.input_name = self.session.get_inputs()[0].name
                print(f"✅ Loaded ONNX model from {onnx_path}")
            else:
                print(f"⚠️ ONNX model not found, falling back to PyTorch")
                self.use_onnx = False
        
        if not use_onnx:
            # Load PyTorch model
            from train_model import FoodRecognitionModel
            self.model = FoodRecognitionModel(
                num_classes=len(self.class_to_idx),
                pretrained=False
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(device)
            self.model.eval()
            print(f"✅ Loaded PyTorch model")
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for inference"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms
        img_tensor = self.transform(image)
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
        
        if self.use_onnx:
            return img_tensor.numpy()
        else:
            return img_tensor.to(self.device)
    
    def estimate_portion_size(self, image: Image.Image) -> float:
        """
        Estimate portion size multiplier using image analysis
        Returns a multiplier for the standard serving (1.0 = standard portion)
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect food region using edge detection and contours
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 1.0  # Default to standard portion
        
        # Find largest contour (assumed to be the food)
        largest_contour = max(contours, key=cv2.contourArea)
        food_area = cv2.contourArea(largest_contour)
        
        # Calculate percentage of image covered by food
        total_area = img_array.shape[0] * img_array.shape[1]
        coverage_ratio = food_area / total_area
        
        # Estimate portion multiplier based on coverage
        # Typical food photo covers 30-50% of frame
        if coverage_ratio < 0.2:
            multiplier = 0.5  # Small portion
        elif coverage_ratio < 0.35:
            multiplier = 0.8
        elif coverage_ratio < 0.55:
            multiplier = 1.0  # Standard portion
        elif coverage_ratio < 0.70:
            multiplier = 1.3
        else:
            multiplier = 1.6  # Large portion
        
        return multiplier
    
    @torch.no_grad()
    def predict(
        self,
        image: Image.Image,
        top_k: int = 3,
        estimate_portion: bool = True
    ) -> Dict:
        """
        Predict food category and get nutritional estimates
        
        Returns:
            {
                'category': str,
                'confidence': float,
                'top_predictions': List[Tuple[str, float]],
                'portion_multiplier': float
            }
        """
        # Preprocess
        img_input = self.preprocess_image(image)
        
        # Inference
        if self.use_onnx:
            outputs = self.session.run(None, {self.input_name: img_input})[0]
            outputs = torch.from_numpy(outputs)
        else:
            outputs = self.model(img_input)
        
        # Get probabilities
        probabilities = F.softmax(outputs, dim=1)[0]
        
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(self.idx_to_class)))
        
        top_predictions = [
            (self.idx_to_class[idx.item()], prob.item())
            for idx, prob in zip(top_indices, top_probs)
        ]
        
        # Estimate portion size
        portion_multiplier = 1.0
        if estimate_portion:
            portion_multiplier = self.estimate_portion_size(image)
        
        return {
            'category': top_predictions[0][0],
            'confidence': top_predictions[0][1],
            'top_predictions': top_predictions,
            'portion_multiplier': round(portion_multiplier, 2)
        }
    
    def batch_predict(self, images: List[Image.Image]) -> List[Dict]:
        """Predict multiple images"""
        results = []
        for image in images:
            result = self.predict(image)
            results.append(result)
        return results

def export_to_onnx(model_path: str, output_path: str = None):
    """
    Export PyTorch model to ONNX for faster inference
    """
    from train_model import FoodRecognitionModel
    
    # Load model
    checkpoint = torch.load(model_path, map_location='cpu')
    num_classes = len(checkpoint['class_to_idx'])
    
    model = FoodRecognitionModel(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Dummy input
    dummy_input = torch.randn(1, 3, 384, 384)
    
    # Export
    if output_path is None:
        output_path = str(Path(model_path).parent / "model.onnx")
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print(f"✅ Exported ONNX model to {output_path}")
    
    # Verify ONNX model
    import onnx
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print("✅ ONNX model verified successfully")

if __name__ == "__main__":
    # Example: Export model to ONNX
    # export_to_onnx("checkpoints/best_model.pth")
    
    # Example: Run inference
    model_path = "checkpoints/best_model.pth"
    if Path(model_path).exists():
        predictor = FoodRecognitionInference(model_path, use_onnx=False)
        
        # Test with sample image
        test_image = Image.new('RGB', (384, 384), color='red')
        result = predictor.predict(test_image)
        print("\n🍕 Prediction result:")
        print(json.dumps(result, indent=2))
