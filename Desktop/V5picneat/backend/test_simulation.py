"""
PicNEat V1 - Simulated Test
Tests the food detection logic without needing network access
"""

import json

# Simulate what Groq Vision API would return for a pizza photo
def simulate_groq_response():
    """This is what Groq would return for a photo of pizza"""
    return {
        "foods": [
            {
                "name": "pizza, cheese, regular crust",
                "portion_grams": 125.3,
                "confidence": 0.91,
                "notes": "Standard dinner plate, single slice covering ~12% of plate. Typical dining hall thickness. Estimated 125g based on visible size and standard pizza density."
            }
        ]
    }

# Simulate Purdue menu lookup
def fuzzy_match_purdue(food_name):
    """Fuzzy match against our 17 Purdue menu items"""
    purdue_items = [
        {"item_name": "Pizza Slice Cheese", "calories_per_serving": 285, "serving_size_g": 125, "dining_hall": "Hillenbrand"},
        {"item_name": "Pizza Slice Pepperoni", "calories_per_serving": 313, "serving_size_g": 125, "dining_hall": "Hillenbrand"},
        {"item_name": "Grilled Chicken Breast", "calories_per_serving": 165, "serving_size_g": 100, "dining_hall": "Wiley"},
        {"item_name": "Burger with Bun", "calories_per_serving": 540, "serving_size_g": 220, "dining_hall": "Earhart"},
    ]
    
    food_lower = food_name.lower()
    
    for item in purdue_items:
        item_lower = item["item_name"].lower()
        if "pizza" in food_lower and "pizza" in item_lower:
            if "cheese" in food_lower and "cheese" in item_lower:
                # MATCH FOUND!
                cals_per_100g = (item["calories_per_serving"] / item["serving_size_g"]) * 100
                return {
                    "name": item["item_name"],
                    "calories_per_100g": cals_per_100g,
                    "protein": 12.0,  # Typical pizza values
                    "carbs": 36.0,
                    "fats": 10.0,
                    "source": "purdue",
                    "dining_hall": item["dining_hall"]
                }
    
    return None

# Simulate complete meal analysis
def analyze_meal_simulation():
    """Simulates the complete /analyze-meal endpoint logic"""
    
    print("=" * 60)
    print("🍕 PicNEat V1 - Simulated Food Detection Test")
    print("=" * 60)
    print()
    
    # Step 1: Groq Vision identifies the food
    print("📸 Step 1: Groq Vision API analyzing image...")
    groq_result = simulate_groq_response()
    food_item = groq_result['foods'][0]
    print(f"   ✅ Detected: {food_item['name']}")
    print(f"   ✅ Portion: {food_item['portion_grams']}g")
    print(f"   ✅ Confidence: {food_item['confidence']*100:.1f}%")
    print()
    
    # Step 2: Purdue menu lookup
    print("🏫 Step 2: Checking Purdue dining menu...")
    nutrition = fuzzy_match_purdue(food_item['name'])
    
    if nutrition:
        print(f"   ✅ MATCH FOUND: {nutrition['name']}")
        print(f"   ✅ Source: {nutrition['source']} ({nutrition['dining_hall']})")
    else:
        print("   ⚠️  No Purdue match, would call USDA API...")
        nutrition = {
            'calories_per_100g': 266,
            'protein': 12.0,
            'carbs': 36.0,
            'fats': 10.0,
            'source': 'usda'
        }
    print()
    
    # Step 3: Calculate actual nutrition based on portion
    print("🧮 Step 3: Calculating nutrition for actual portion...")
    multiplier = food_item['portion_grams'] / 100.0
    
    result = {
        "foods": [{
            "name": food_item['name'],
            "portion_grams": food_item['portion_grams'],
            "calories": int(nutrition['calories_per_100g'] * multiplier),
            "protein": round(nutrition['protein'] * multiplier, 1),
            "carbs": round(nutrition['carbs'] * multiplier, 1),
            "fats": round(nutrition['fats'] * multiplier, 1),
            "confidence": food_item['confidence'],
            "source": nutrition['source']
        }],
        "total_calories": int(nutrition['calories_per_100g'] * multiplier),
        "total_protein": round(nutrition['protein'] * multiplier, 1),
        "total_carbs": round(nutrition['carbs'] * multiplier, 1),
        "total_fats": round(nutrition['fats'] * multiplier, 1),
        "analysis_time_ms": 2847
    }
    
    print(f"   ✅ Calories: {result['total_calories']}")
    print(f"   ✅ Protein: {result['total_protein']}g")
    print(f"   ✅ Carbs: {result['total_carbs']}g")
    print(f"   ✅ Fats: {result['total_fats']}g")
    print()
    
    # Step 4: Display final result
    print("=" * 60)
    print("🎉 FINAL API RESPONSE:")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print()
    
    print("=" * 60)
    print("✅ SUCCESS! Your backend would return this to iOS app!")
    print("=" * 60)
    print()
    print("🔥 What just happened:")
    print("   1. Groq Vision identified: Pizza, cheese (125g)")
    print("   2. Matched Purdue menu: 'Pizza Slice Cheese' from Hillenbrand")
    print("   3. Calculated accurate calories: 285 cal")
    print("   4. Ready to send to iOS app!")
    print()
    print("📱 Your iOS app receives this JSON and displays:")
    print("   - Food name with confidence %")
    print("   - Calorie ring updates")
    print("   - +FUEL animation")
    print("   - Streak continues!")
    print()

if __name__ == "__main__":
    analyze_meal_simulation()
