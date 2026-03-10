"""
USDA Food Data Central API Service
Fetches nutritional information from USDA FDC database
"""

import httpx
from typing import Optional, Dict
import logging
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.core.config import get_settings
from app.models.database import NutritionCache

logger = logging.getLogger(__name__)
settings = get_settings()

class USDAFDCService:
    """USDA Food Data Central API client"""
    
    def __init__(self):
        self.api_key = settings.USDA_FDC_API_KEY
        self.base_url = settings.FDC_API_BASE_URL
        self.timeout = 10.0
    
    async def search_food(self, query: str) -> Optional[Dict]:
        """
        Search for food in USDA database
        
        Returns nutrition data per 100g
        """
        url = f"{self.base_url}/foods/search"
        params = {
            "query": query,
            "api_key": self.api_key,
            "pageSize": 1,
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("foods") or len(data["foods"]) == 0:
                    logger.warning(f"No results found for query: {query}")
                    return None
                
                food = data["foods"][0]
                return self._parse_nutrition_data(food)
                
        except httpx.TimeoutException:
            logger.error(f"Timeout while searching for: {query}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while searching USDA FDC: {e}")
            return None
        except Exception as e:
            logger.error(f"Error searching USDA FDC: {e}")
            return None
    
    def _parse_nutrition_data(self, food_data: Dict) -> Dict:
        """Parse nutrition data from USDA response"""
        nutrients = {}
        
        # Map USDA nutrient names to our schema
        nutrient_mapping = {
            "Energy": "calories",
            "Protein": "protein",
            "Carbohydrate, by difference": "carbs",
            "Total lipid (fat)": "fat",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugar"
        }
        
        # Extract nutrients
        for nutrient in food_data.get("foodNutrients", []):
            nutrient_name = nutrient.get("nutrientName", "")
            value = nutrient.get("value", 0)
            unit = nutrient.get("unitName", "")
            
            # Handle Energy (calories)
            if "Energy" in nutrient_name:
                if "kcal" in unit.lower() or "kcal" in nutrient_name.lower():
                    nutrients["calories"] = value
                continue
            
            # Handle other nutrients
            for usda_name, our_name in nutrient_mapping.items():
                if usda_name in nutrient_name:
                    nutrients[our_name] = value
                    break
        
        return {
            "fdc_id": food_data.get("fdcId"),
            "description": food_data.get("description"),
            "calories": nutrients.get("calories", 0),
            "protein": nutrients.get("protein", 0),
            "carbs": nutrients.get("carbs", 0),
            "fat": nutrients.get("fat", 0),
            "fiber": nutrients.get("fiber", 0),
            "sugar": nutrients.get("sugar", 0),
            "raw_data": json.dumps(food_data)
        }
    
    async def get_nutrition_cached(self, db: Session, food_name: str) -> Optional[Dict]:
        """
        Get nutrition data with caching
        First checks local cache, then USDA API if not found
        """
        # Check cache first
        cached = db.query(NutritionCache).filter(
            NutritionCache.food_name == food_name.lower()
        ).first()
        
        if cached:
            # Update cache metadata
            cached.last_accessed = datetime.utcnow()
            cached.access_count += 1
            db.commit()
            
            logger.info(f"Nutrition data found in cache for: {food_name}")
            return {
                "fdc_id": cached.fdc_id,
                "calories": cached.calories,
                "protein": cached.protein,
                "carbs": cached.carbs,
                "fat": cached.fat,
                "fiber": cached.fiber,
                "sugar": cached.sugar
            }
        
        # Not in cache, fetch from API
        logger.info(f"Fetching nutrition data from USDA for: {food_name}")
        nutrition_data = await self.search_food(food_name)
        
        if nutrition_data:
            # Save to cache
            cache_entry = NutritionCache(
                food_name=food_name.lower(),
                fdc_id=nutrition_data["fdc_id"],
                calories=nutrition_data["calories"],
                protein=nutrition_data["protein"],
                carbs=nutrition_data["carbs"],
                fat=nutrition_data["fat"],
                fiber=nutrition_data["fiber"],
                sugar=nutrition_data["sugar"],
                raw_response=nutrition_data.get("raw_data")
            )
            db.add(cache_entry)
            db.commit()
            
            logger.info(f"Cached nutrition data for: {food_name}")
            
            # Remove raw_data before returning
            nutrition_data.pop("raw_data", None)
            nutrition_data.pop("description", None)
            
            return nutrition_data
        
        return None
    
    def calculate_portion_nutrition(
        self,
        nutrition_per_100g: Dict,
        portion_multiplier: float,
        serving_size_g: float = 150.0  # Default serving size
    ) -> Dict:
        """
        Calculate nutrition for actual portion size
        
        Args:
            nutrition_per_100g: Nutrition data per 100g
            portion_multiplier: Multiplier from image analysis (e.g., 1.5 for 1.5x normal portion)
            serving_size_g: Base serving size in grams (default 150g)
        
        Returns:
            Estimated nutrition for the portion
        """
        actual_grams = serving_size_g * portion_multiplier
        multiplier = actual_grams / 100.0
        
        return {
            "estimated_calories": round(nutrition_per_100g.get("calories", 0) * multiplier, 1),
            "estimated_protein": round(nutrition_per_100g.get("protein", 0) * multiplier, 1),
            "estimated_carbs": round(nutrition_per_100g.get("carbs", 0) * multiplier, 1),
            "estimated_fat": round(nutrition_per_100g.get("fat", 0) * multiplier, 1),
            "portion_grams": round(actual_grams, 1)
        }

# Global instance
usda_service = USDAFDCService()
