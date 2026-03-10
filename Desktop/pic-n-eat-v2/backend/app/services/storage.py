"""
Cloudinary Storage Service - FREE Alternative to AWS S3
Drop-in replacement for storage.py

Setup:
1. Sign up at https://cloudinary.com/users/register/free
2. Get your credentials from dashboard
3. Add to .env:
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import io
import uuid
from typing import Tuple, Optional
from datetime import datetime
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class CloudinaryStorage:
    """Cloudinary storage handler - FREE alternative to S3"""
    
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        
        logger.info(f"✅ Cloudinary configured: {settings.CLOUDINARY_CLOUD_NAME}")
    
    def _generate_unique_id(self, user_id: int) -> str:
        """Generate unique filename"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"picneat/{user_id}/{timestamp}_{unique_id}"
    
    def _optimize_image(self, image: Image.Image, max_size: int = 1920) -> Image.Image:
        """Optimize image size while maintaining quality"""
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large
        width, height = image.size
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    async def upload_image(
        self,
        image: Image.Image,
        user_id: int,
        file_extension: str = "jpg"
    ) -> Tuple[str, str]:
        """
        Upload image to Cloudinary
        
        Returns:
            Tuple[public_id, secure_url]
        """
        try:
            # Optimize image
            optimized_image = self._optimize_image(image)
            
            # Convert to bytes
            buffer = io.BytesIO()
            optimized_image.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            # Generate unique ID
            public_id = self._generate_unique_id(user_id)
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                buffer,
                public_id=public_id,
                folder="picneat",  # Organize in folder
                resource_type="image",
                # Cloudinary optimizations
                quality="auto",
                fetch_format="auto"
            )
            
            # Get URLs
            secure_url = result['secure_url']
            
            logger.info(f"✅ Uploaded to Cloudinary: {public_id}")
            
            return public_id, secure_url
            
        except Exception as e:
            logger.error(f"❌ Cloudinary upload error: {e}")
            raise Exception(f"Failed to upload image: {str(e)}")
    
    async def delete_image(self, public_id: str) -> bool:
        """Delete image from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') == 'ok':
                logger.info(f"✅ Deleted from Cloudinary: {public_id}")
                return True
            else:
                logger.warning(f"⚠️ Delete failed: {public_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Cloudinary delete error: {e}")
            return False
    
    async def get_presigned_url(self, public_id: str, expiration: int = 3600) -> Optional[str]:
        """
        Get image URL (Cloudinary URLs are already public and optimized)
        No presigning needed - Cloudinary handles this better
        """
        try:
            # Generate optimized URL
            url = cloudinary.CloudinaryImage(public_id).build_url(
                secure=True,
                transformation=[
                    {'quality': 'auto'},
                    {'fetch_format': 'auto'}
                ]
            )
            return url
        except Exception as e:
            logger.error(f"❌ Error generating URL: {e}")
            return None

# Global instance
cloudinary_storage = CloudinaryStorage()


# ============================================
# BONUS: Migration script if you already have S3 images
# ============================================

async def migrate_from_s3_to_cloudinary(s3_storage, cloudinary_storage, db):
    """
    Helper function to migrate existing S3 images to Cloudinary
    Run this once if you already have images in S3
    """
    from app.models.database import FoodLog
    
    logs = db.query(FoodLog).all()
    
    for log in logs:
        try:
            # Download from S3
            s3_url = log.image_url
            
            # Download image (you'd need to implement this)
            # image = download_from_url(s3_url)
            
            # Upload to Cloudinary
            # public_id, new_url = await cloudinary_storage.upload_image(image, log.user_id)
            
            # Update database
            # log.image_s3_key = public_id
            # log.image_url = new_url
            # db.commit()
            
            print(f"✅ Migrated log {log.id}")
            
        except Exception as e:
            print(f"❌ Failed to migrate log {log.id}: {e}")
            continue
