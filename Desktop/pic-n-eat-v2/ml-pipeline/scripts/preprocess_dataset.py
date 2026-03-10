"""
Dataset Preprocessing Script for WWEIA Food Images

This script:
1. Downloads WWEIA dataset if not present
2. Maps WWEIA food codes to USDA FDC IDs
3. Organizes images into train/val/test splits
4. Creates class labels and metadata
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import requests


class WWEIAPreprocessor:
    def __init__(self, raw_data_dir: str = "data/raw", output_dir: str = "data/processed"):
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create split directories
        for split in ["train", "val", "test"]:
            (self.output_dir / split).mkdir(exist_ok=True)
    
    def load_food_codes(self) -> pd.DataFrame:
        """Load WWEIA food codes and metadata."""
        food_codes_path = self.raw_data_dir / "food_codes.csv"
        
        if not food_codes_path.exists():
            raise FileNotFoundError(
                f"Food codes file not found at {food_codes_path}. "
                "Please download the WWEIA dataset first."
            )
        
        df = pd.read_csv(food_codes_path)
        print(f"✓ Loaded {len(df)} food codes")
        return df
    
    def map_to_fdc(self, food_codes: pd.DataFrame) -> Dict[int, int]:
        """
        Map WWEIA food codes to USDA FDC IDs.
        
        This mapping allows us to link our ML predictions to
        accurate nutrition data from the FDC database.
        """
        # Load or create mapping
        mapping_path = self.output_dir / "fdc_mapping.json"
        
        if mapping_path.exists():
            with open(mapping_path) as f:
                mapping = json.load(f)
            print(f"✓ Loaded existing FDC mapping: {len(mapping)} entries")
            return {int(k): v for k, v in mapping.items()}
        
        # Create new mapping by searching FDC API
        print("Creating FDC mapping (this may take a while)...")
        mapping = {}
        
        for _, row in tqdm(food_codes.iterrows(), total=len(food_codes)):
            wweia_code = row['food_code']
            food_name = row['food_description']
            
            # Search FDC API for matching food
            fdc_id = self._search_fdc(food_name)
            if fdc_id:
                mapping[wweia_code] = fdc_id
        
        # Save mapping
        with open(mapping_path, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"✓ Created FDC mapping: {len(mapping)} entries")
        return mapping
    
    def _search_fdc(self, food_name: str) -> int:
        """Search USDA FDC API for food."""
        # You need to add your USDA API key here
        api_key = os.getenv("USDA_API_KEY")
        if not api_key:
            print("Warning: USDA_API_KEY not set. Skipping FDC mapping.")
            return None
        
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "api_key": api_key,
            "query": food_name,
            "dataType": "SR Legacy",
            "pageSize": 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            foods = data.get("foods", [])
            if foods:
                return foods[0]["fdcId"]
        except Exception as e:
            print(f"Error searching FDC for '{food_name}': {e}")
        
        return None
    
    def organize_images(self, food_codes: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Organize food images into class directories.
        
        Returns:
            Dictionary mapping class names to image paths
        """
        print("Organizing images by food class...")
        
        images_dir = self.raw_data_dir / "food_images"
        class_images = {}
        
        # Find all food images
        for food_dir in images_dir.iterdir():
            if not food_dir.is_dir():
                continue
            
            for img_path in food_dir.glob("*.jpg"):
                # Extract food code from filename
                # Assuming format: food_code_001.jpg
                food_code = int(img_path.stem.split('_')[0])
                
                # Get food name from codes
                food_row = food_codes[food_codes['food_code'] == food_code]
                if len(food_row) == 0:
                    continue
                
                food_name = food_row.iloc[0]['food_description']
                
                # Clean food name for use as class label
                class_name = self._clean_class_name(food_name)
                
                if class_name not in class_images:
                    class_images[class_name] = []
                
                class_images[class_name].append(str(img_path))
        
        print(f"✓ Found {len(class_images)} food classes")
        print(f"✓ Total images: {sum(len(imgs) for imgs in class_images.values())}")
        
        return class_images
    
    def _clean_class_name(self, food_name: str) -> str:
        """Clean food name to create valid class label."""
        # Convert to lowercase, replace spaces with underscores
        clean = food_name.lower().strip()
        clean = clean.replace(" ", "_")
        clean = clean.replace(",", "")
        clean = clean.replace("(", "").replace(")", "")
        return clean
    
    def create_splits(
        self, 
        class_images: Dict[str, List[str]], 
        train_ratio: float = 0.8, 
        val_ratio: float = 0.1
    ):
        """
        Create train/val/test splits and copy images.
        
        Args:
            class_images: Dictionary of class names to image paths
            train_ratio: Proportion for training (default 0.8)
            val_ratio: Proportion for validation (default 0.1)
                       Test will be 1 - train_ratio - val_ratio
        """
        print("Creating train/val/test splits...")
        
        class_names = []
        
        for class_name, image_paths in tqdm(class_images.items()):
            if len(image_paths) < 10:  # Skip classes with too few images
                continue
            
            class_names.append(class_name)
            
            # Split into train/temp
            train_imgs, temp_imgs = train_test_split(
                image_paths, 
                train_size=train_ratio, 
                random_state=42
            )
            
            # Split temp into val/test
            val_imgs, test_imgs = train_test_split(
                temp_imgs,
                train_size=val_ratio / (1 - train_ratio),
                random_state=42
            )
            
            # Copy images to respective directories
            for split, images in [("train", train_imgs), ("val", val_imgs), ("test", test_imgs)]:
                class_dir = self.output_dir / split / class_name
                class_dir.mkdir(exist_ok=True)
                
                for img_path in images:
                    img_name = Path(img_path).name
                    shutil.copy(img_path, class_dir / img_name)
        
        # Save class names
        with open(self.output_dir / "class_names.json", 'w') as f:
            json.dump(sorted(class_names), f, indent=2)
        
        print(f"✓ Created splits with {len(class_names)} classes")
        print(f"  - Train: {self._count_images(self.output_dir / 'train')} images")
        print(f"  - Val: {self._count_images(self.output_dir / 'val')} images")
        print(f"  - Test: {self._count_images(self.output_dir / 'test')} images")
    
    def _count_images(self, directory: Path) -> int:
        """Count total images in directory."""
        return len(list(directory.rglob("*.jpg")))
    
    def create_metadata(self):
        """Create metadata file with dataset statistics."""
        metadata = {
            "num_classes": len(list((self.output_dir / "train").iterdir())),
            "train_images": self._count_images(self.output_dir / "train"),
            "val_images": self._count_images(self.output_dir / "val"),
            "test_images": self._count_images(self.output_dir / "test"),
            "image_size": 224,
            "normalization": {
                "mean": [0.485, 0.456, 0.406],
                "std": [0.229, 0.224, 0.225]
            }
        }
        
        with open(self.output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Created metadata file")
    
    def run(self):
        """Run complete preprocessing pipeline."""
        print("=" * 60)
        print("WWEIA Dataset Preprocessing")
        print("=" * 60)
        
        # Step 1: Load food codes
        food_codes = self.load_food_codes()
        
        # Step 2: Map to FDC IDs
        fdc_mapping = self.map_to_fdc(food_codes)
        
        # Step 3: Organize images
        class_images = self.organize_images(food_codes)
        
        # Step 4: Create splits
        self.create_splits(class_images)
        
        # Step 5: Create metadata
        self.create_metadata()
        
        print("\n" + "=" * 60)
        print("✅ Preprocessing complete!")
        print("=" * 60)
        print(f"\nProcessed data saved to: {self.output_dir}")
        print("\nNext steps:")
        print("  1. Review class_names.json")
        print("  2. Start training: python scripts/train.py")


if __name__ == "__main__":
    preprocessor = WWEIAPreprocessor()
    preprocessor.run()
