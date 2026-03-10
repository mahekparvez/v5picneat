import httpx
import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.models import FDCCache
from datetime import datetime, timedelta

settings = get_settings()


class USDAService:
    """Service for interacting with USDA FoodData Central API."""
    
    def __init__(self):
        self.api_key = settings.USDA_API_KEY
        self.base_url = settings.USDA_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_food(
        self, 
        query: str, 
        page_size: int = 5,
        data_type: str = "SR Legacy"  # Most reliable data source
    ) -> List[Dict]:
        """
        Search for food in USDA FDC database.
        
        Args:
            query: Search term (e.g., "banana", "chicken breast")
            page_size: Number of results to return
            data_type: FDC data type (SR Legacy, Foundation, Survey, etc.)
        
        Returns:
            List of food items with FDC IDs and basic info
        """
        url = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "dataType": data_type,
            "sortBy": "dataType.keyword",
            "sortOrder": "asc"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            foods = []
            for food in data.get("foods", []):
                foods.append({
                    "fdc_id": food.get("fdcId"),
                    "description": food.get("description"),
                    "data_type": food.get("dataType"),
                    "brand_owner": food.get("brandOwner"),
                })
            
            return foods
        
        except httpx.HTTPError as e:
            print(f"USDA API error: {e}")
            return []
    
    async def get_food_details(self, fdc_id: int, db: Session) -> Optional[Dict]:
        """
        Get detailed nutrition information for a specific food.
        First checks cache, then fetches from API if needed.
        
        Args:
            fdc_id: USDA FoodData Central ID
            db: Database session for cache lookup
        
        Returns:
            Nutrition data dictionary
        """
        # Check cache first (valid for 30 days)
        cached = db.query(FDCCache).filter(FDCCache.fdc_id == fdc_id).first()
        if cached and (datetime.now() - cached.cached_at).days < 30:
            return self._cache_to_dict(cached)
        
        # Fetch from API
        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Parse nutrition data
            nutrients = self._parse_nutrients(data.get("foodNutrients", []))
            
            food_data = {
                "fdc_id": fdc_id,
                "food_name": data.get("description", "Unknown"),
                "calories": nutrients.get("Energy", 0),
                "protein": nutrients.get("Protein", 0),
                "carbs": nutrients.get("Carbohydrate, by difference", 0),
                "fat": nutrients.get("Total lipid (fat)", 0),
                "fiber": nutrients.get("Fiber, total dietary", 0),
                "serving_size": data.get("servingSize"),
                "serving_unit": data.get("servingSizeUnit"),
                "raw_data": json.dumps(data),
                "data_type": data.get("dataType"),
            }
            
            # Update cache
            if cached:
                for key, value in food_data.items():
                    setattr(cached, key, value)
                cached.cached_at = datetime.now()
            else:
                cache_entry = FDCCache(**food_data)
                db.add(cache_entry)
            
            db.commit()
            
            return food_data
        
        except httpx.HTTPError as e:
            print(f"USDA API error for FDC {fdc_id}: {e}")
            return None
    
    def _parse_nutrients(self, food_nutrients: List[Dict]) -> Dict[str, float]:
        """
        Extract key nutrients from FDC nutrient list.
        
        FDC provides nutrients per 100g by default.
        """
        nutrients = {}
        
        for nutrient in food_nutrients:
            name = nutrient.get("nutrient", {}).get("name")
            value = nutrient.get("amount", 0)
            
            if name:
                nutrients[name] = value
        
        return nutrients
    
    def _cache_to_dict(self, cache_entry: FDCCache) -> Dict:
        """Convert cache entry to dictionary."""
        return {
            "fdc_id": cache_entry.fdc_id,
            "food_name": cache_entry.food_name,
            "calories": cache_entry.calories,
            "protein": cache_entry.protein,
            "carbs": cache_entry.carbs,
            "fat": cache_entry.fat,
            "fiber": cache_entry.fiber,
            "serving_size": cache_entry.serving_size,
            "serving_unit": cache_entry.serving_unit,
            "data_type": cache_entry.data_type,
        }
    
    def calculate_nutrition_for_portion(
        self, 
        fdc_data: Dict, 
        portion_grams: float
    ) -> Dict[str, float]:
        """
        Calculate nutrition values for a specific portion size.
        
        FDC provides values per 100g, so we scale based on actual portion.
        
        Args:
            fdc_data: Dictionary from get_food_details()
            portion_grams: Estimated portion size in grams
        
        Returns:
            Scaled nutrition values
        """
        scale_factor = portion_grams / 100  # FDC uses per 100g
        
        return {
            "calories": round(fdc_data["calories"] * scale_factor, 1),
            "protein": round(fdc_data["protein"] * scale_factor, 1),
            "carbs": round(fdc_data["carbs"] * scale_factor, 1),
            "fat": round(fdc_data["fat"] * scale_factor, 1),
            "fiber": round(fdc_data["fiber"] * scale_factor, 1),
        }
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Usage example:
"""
usda_service = USDAService()

# Search for foods
results = await usda_service.search_food("banana")
# [{"fdc_id": 173944, "description": "Bananas, raw", ...}]

# Get detailed nutrition
nutrition = await usda_service.get_food_details(173944, db)
# {"calories": 89, "protein": 1.09, "carbs": 22.84, ...}

# Calculate for specific portion
portion_nutrition = usda_service.calculate_nutrition_for_portion(
    nutrition, 
    portion_grams=118  # 1 medium banana
)
# {"calories": 105.0, "protein": 1.3, "carbs": 27.0, ...}
"""
