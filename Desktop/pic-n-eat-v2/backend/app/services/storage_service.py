import boto3
from botocore.exceptions import ClientError
from PIL import Image
import io
from typing import Tuple, Optional
from datetime import datetime
import uuid
from app.core.config import get_settings

settings = get_settings()


class StorageService:
    """
    Service for uploading and managing images in S3/CloudFlare R2.
    """
    
    def __init__(self):
        # Initialize S3 client (works with CloudFlare R2 too)
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def upload_food_image(
        self, 
        image: Image.Image, 
        user_id: str,
        log_type: str = "food"  # "food" or "resistance"
    ) -> Tuple[str, str]:
        """
        Upload food image and create thumbnail.
        
        Args:
            image: PIL Image object
            user_id: User UUID
            log_type: Type of log (food or resistance)
        
        Returns:
            Tuple of (original_url, thumbnail_url)
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        image_id = str(uuid.uuid4())[:8]
        
        # Generate S3 keys
        original_key = f"{log_type}-logs/{user_id}/{timestamp}_{image_id}.jpg"
        thumbnail_key = f"thumbnails/{log_type}/{user_id}/{timestamp}_{image_id}_thumb.jpg"
        
        # Upload original
        original_url = self._upload_image(image, original_key, quality=95)
        
        # Create and upload thumbnail
        thumbnail = self._create_thumbnail(image, settings.THUMBNAIL_SIZE)
        thumbnail_url = self._upload_image(thumbnail, thumbnail_key, quality=85)
        
        return original_url, thumbnail_url
    
    def _upload_image(
        self, 
        image: Image.Image, 
        s3_key: str, 
        quality: int = 95
    ) -> str:
        """
        Upload a PIL Image to S3.
        
        Returns:
            Public URL of uploaded image
        """
        # Convert image to bytes
        buffer = io.BytesIO()
        
        # Strip EXIF data for privacy
        image_without_exif = self._strip_exif(image)
        image_without_exif.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=buffer,
                ContentType='image/jpeg',
                CacheControl='max-age=31536000',  # 1 year
            )
            
            # Generate URL
            if settings.S3_ENDPOINT_URL:
                # CloudFlare R2 or custom endpoint
                url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{s3_key}"
            else:
                # Standard S3
                url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}"
            
            return url
        
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise
    
    def _create_thumbnail(
        self, 
        image: Image.Image, 
        size: Tuple[int, int]
    ) -> Image.Image:
        """
        Create a thumbnail maintaining aspect ratio.
        """
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def _strip_exif(self, image: Image.Image) -> Image.Image:
        """
        Remove EXIF data from image for privacy.
        GPS coordinates, camera info, etc. are removed.
        """
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        return image_without_exif
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for private access.
        
        Args:
            s3_key: S3 object key
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            raise
    
    def delete_image(self, s3_key: str) -> bool:
        """
        Delete an image from S3.
        
        Args:
            s3_key: S3 object key
        
        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
    
    def validate_image(self, image: Image.Image) -> bool:
        """
        Validate image meets requirements.
        
        Checks:
        - Format is allowed (JPEG, PNG, WebP)
        - Size is under limit
        - Image is not corrupted
        """
        # Check format
        if image.format not in ['JPEG', 'PNG', 'WEBP']:
            raise ValueError(f"Invalid image format: {image.format}")
        
        # Check size
        buffer = io.BytesIO()
        image.save(buffer, format=image.format)
        size_mb = len(buffer.getvalue()) / (1024 * 1024)
        
        if size_mb > settings.MAX_IMAGE_SIZE_MB:
            raise ValueError(f"Image too large: {size_mb:.1f}MB (max {settings.MAX_IMAGE_SIZE_MB}MB)")
        
        return True


# Singleton instance
_storage_instance = None


def get_storage() -> StorageService:
    """Get singleton storage service instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService()
    return _storage_instance


# Usage example:
"""
from PIL import Image
from app.services.storage_service import get_storage

storage = get_storage()

# Upload food log image
image = Image.open("food.jpg")
storage.validate_image(image)
original_url, thumbnail_url = storage.upload_food_image(
    image, 
    user_id="user-123",
    log_type="food"
)

print(f"Original: {original_url}")
print(f"Thumbnail: {thumbnail_url}")

# Generate presigned URL (for private images)
presigned = storage.generate_presigned_url("food-logs/user-123/image.jpg")
"""
