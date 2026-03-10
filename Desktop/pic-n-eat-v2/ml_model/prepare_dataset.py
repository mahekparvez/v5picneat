"""
WWEIA Dataset Downloader and Preprocessor
Downloads food images and nutritional data from USDA datasets
"""

import os
import requests
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
from tqdm import tqdm
import time

class WWEIADatasetProcessor:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.images_dir = self.data_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # USDA FDC API endpoint
        self.fdc_api_base = "https://api.nal.usda.gov/fdc/v1"
        self.api_key = os.getenv("USDA_FDC_API_KEY", "DEMO_KEY")
        
    def download_wweia_metadata(self):
        """
        Download WWEIA food category data
        Note: The actual image dataset needs to be downloaded manually from
        https://agdatacommons.nal.usda.gov/articles/dataset/What_We_Eat_In_America_WWEIA_Database/24660126
        """
        print("📥 WWEIA Dataset Download Instructions:")
        print("=" * 60)
        print("1. Visit: https://agdatacommons.nal.usda.gov/articles/dataset/What_We_Eat_In_America_WWEIA_Database/24660126")
        print("2. Download the food category files")
        print("3. Place them in:", self.data_dir / "raw")
        print("=" * 60)
        
        # Create raw data directory
        (self.data_dir / "raw").mkdir(exist_ok=True)
        
    def fetch_food_details_from_fdc(self, food_name: str) -> Dict:
        """
        Fetch nutritional information from USDA FDC API
        """
        url = f"{self.fdc_api_base}/foods/search"
        params = {
            "query": food_name,
            "api_key": self.api_key,
            "pageSize": 1,
            "dataType": ["Survey (FNDDS)"]  # Focus on survey foods for WWEIA
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("foods") and len(data["foods"]) > 0:
                food = data["foods"][0]
                
                # Extract key nutrients
                nutrients = {}
                for nutrient in food.get("foodNutrients", []):
                    nutrient_name = nutrient.get("nutrientName", "")
                    value = nutrient.get("value", 0)
                    
                    if "Energy" in nutrient_name and "kcal" in nutrient_name:
                        nutrients["calories"] = value
                    elif "Protein" in nutrient_name:
                        nutrients["protein"] = value
                    elif "Carbohydrate" in nutrient_name:
                        nutrients["carbs"] = value
                    elif "Total lipid" in nutrient_name or "Fat" in nutrient_name:
                        nutrients["fat"] = value
                    elif "Fiber" in nutrient_name:
                        nutrients["fiber"] = value
                    elif "Sugars" in nutrient_name:
                        nutrients["sugar"] = value
                        
                return {
                    "fdc_id": food.get("fdcId"),
                    "description": food.get("description"),
                    "nutrients": nutrients,
                    "serving_size": food.get("servingSize", 100),
                    "serving_unit": food.get("servingSizeUnit", "g")
                }
        except Exception as e:
            print(f"Error fetching {food_name}: {e}")
            return None
        
        time.sleep(0.1)  # Rate limiting
        return None
    
    def create_food_database(self, food_categories: List[str]) -> pd.DataFrame:
        """
        Create a comprehensive food database with nutritional info
        """
        food_data = []
        
        print("🔍 Fetching nutritional data from USDA FDC...")
        for category in tqdm(food_categories):
            food_info = self.fetch_food_details_from_fdc(category)
            if food_info:
                food_data.append({
                    "category": category,
                    "fdc_id": food_info["fdc_id"],
                    "description": food_info["description"],
                    **food_info["nutrients"],
                    "serving_size": food_info["serving_size"],
                    "serving_unit": food_info["serving_unit"]
                })
        
        df = pd.DataFrame(food_data)
        
        # Save to CSV
        output_path = self.data_dir / "food_nutrition_database.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ Saved nutrition database to {output_path}")
        
        return df
    
    def prepare_training_data(self, images_path: str = None):
        """
        Prepare dataset for model training
        Expects images organized in folders by category
        """
        if images_path:
            images_path = Path(images_path)
        else:
            images_path = self.images_dir
            
        # Create train/val/test splits
        from sklearn.model_selection import train_test_split
        
        image_data = []
        for category_dir in images_path.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                for img_path in category_dir.glob("*.jpg"):
                    image_data.append({
                        "image_path": str(img_path),
                        "category": category
                    })
        
        df = pd.DataFrame(image_data)
        
        # 70-15-15 split
        train_df, temp_df = train_test_split(df, test_size=0.3, stratify=df['category'], random_state=42)
        val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['category'], random_state=42)
        
        # Save splits
        train_df.to_csv(self.data_dir / "train.csv", index=False)
        val_df.to_csv(self.data_dir / "val.csv", index=False)
        test_df.to_csv(self.data_dir / "test.csv", index=False)
        
        print(f"📊 Dataset prepared:")
        print(f"  Train: {len(train_df)} images")
        print(f"  Val: {len(val_df)} images")
        print(f"  Test: {len(test_df)} images")
        print(f"  Categories: {df['category'].nunique()}")
        
        return train_df, val_df, test_df

# Example usage for common food categories
COMMON_FOOD_CATEGORIES = [
    "Pizza", "Burger", "Salad", "Pasta", "Rice", "Chicken", "Fish", "Steak",
    "Sandwich", "Soup", "Sushi", "Tacos", "Burrito", "Noodles", "Bread",
    "Eggs", "Yogurt", "Fruit salad", "Vegetables", "French fries", "Ice cream",
    "Cake", "Cookies", "Donut", "Muffin", "Pancakes", "Waffles", "Cereal",
    "Oatmeal", "Smoothie", "Coffee", "Tea", "Juice", "Soda", "Water",
    "Apple", "Banana", "Orange", "Grapes", "Strawberries", "Blueberries",
    "Avocado", "Tomato", "Broccoli", "Carrot", "Spinach", "Potato",
    "Cheese", "Milk", "Butter", "Chocolate"
]

if __name__ == "__main__":
    processor = WWEIADatasetProcessor()
    
    # Step 1: Show download instructions
    processor.download_wweia_metadata()
    
    # Step 2: Create nutrition database
    nutrition_df = processor.create_food_database(COMMON_FOOD_CATEGORIES)
    print(nutrition_df.head())
    
    # Step 3: Prepare training data (after you've organized images)
    # processor.prepare_training_data("path/to/your/organized/images")
