"""
Test script for PicNEat V1 API
Download a sample food image and test the /analyze-meal endpoint
"""

import requests
import json

# Test the API
API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_analyze_meal(image_path: str):
    """Test meal analysis with an image"""
    print(f"📸 Testing /analyze-meal with {image_path}...")
    
    with open(image_path, 'rb') as f:
        files = {'file': ('food.jpg', f, 'image/jpeg')}
        response = requests.post(f"{API_URL}/analyze-meal", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Analysis Results:")
        print(f"Total Calories: {result['total_calories']}")
        print(f"Analysis Time: {result['analysis_time_ms']}ms")
        print(f"\nDetected Foods:")
        for food in result['foods']:
            print(f"  - {food['name']}")
            print(f"    Portion: {food['portion_grams']}g")
            print(f"    Calories: {food['calories']}")
            print(f"    Protein: {food['protein']}g | Carbs: {food['carbs']}g | Fats: {food['fats']}g")
            print(f"    Confidence: {food['confidence']*100:.1f}%")
            print(f"    Source: {food['source']}")
            print()
    else:
        print(f"❌ ERROR: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("PicNEat V1 API Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Analyze meal (you'll need to provide an image)
    print("To test /analyze-meal, run:")
    print("  python test_api.py /path/to/food-image.jpg")
    print()
    print("Or use curl:")
    print("  curl -X POST http://localhost:8000/analyze-meal \\")
    print("    -F 'file=@food.jpg'")
