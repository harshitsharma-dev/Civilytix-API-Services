import json
from typing import Optional, Dict, Any
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

from app.core.config import settings


class CloudStorageService:
    """Service for handling Google Cloud Storage operations."""
    
    def __init__(self):
        self.client: Optional[storage.Client] = None
        self.bucket = None
        
    def initialize(self) -> bool:
        """
        Initialize Google Cloud Storage client and bucket.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize client with project ID if provided
            if settings.GCS_PROJECT_ID:
                self.client = storage.Client(project=settings.GCS_PROJECT_ID)
            else:
                # Use default credentials from environment
                self.client = storage.Client()
            
            self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
            print(f"Successfully initialized GCS client for bucket: {settings.GCS_BUCKET_NAME}")
            return True
        except Exception as e:
            print(f"Error initializing Google Cloud Storage: {e}")
            return False
    
    def upload_json_data(self, data: Dict[str, Any], destination_path: str, 
                        content_type: str = 'application/json') -> Optional[str]:
        """
        Upload JSON data to Google Cloud Storage.
        
        Args:
            data: Data to upload as JSON
            destination_path: Path in the bucket where file will be stored
            content_type: MIME type of the content
            
        Returns:
            str: Public URL to the uploaded file, None if failed
        """
        try:
            if not self.client or not self.bucket:
                if not self.initialize():
                    return None
            
            blob = self.bucket.blob(destination_path)
            
            # Convert data to JSON string and upload
            json_data = json.dumps(data)
            blob.upload_from_string(json_data, content_type=content_type)
            
            # Generate public URL
            public_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{destination_path}"
            
            print(f"Successfully uploaded data to GCS: {public_url}")
            return public_url
            
        except GoogleCloudError as e:
            print(f"Google Cloud Storage error: {e}")
            return None
        except Exception as e:
            print(f"Error uploading to GCS: {e}")
            return None
    
    def upload_file(self, file_path: str, destination_path: str, 
                   content_type: str = 'application/octet-stream') -> Optional[str]:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            file_path: Local path to the file to upload
            destination_path: Path in the bucket where file will be stored
            content_type: MIME type of the content
            
        Returns:
            str: Public URL to the uploaded file, None if failed
        """
        try:
            if not self.client or not self.bucket:
                if not self.initialize():
                    return None
            
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(file_path, content_type=content_type)
            
            # Generate public URL
            public_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{destination_path}"
            
            print(f"Successfully uploaded file to GCS: {public_url}")
            return public_url
            
        except GoogleCloudError as e:
            print(f"Google Cloud Storage error: {e}")
            return None
        except Exception as e:
            print(f"Error uploading file to GCS: {e}")
            return None
    
    def generate_signed_url(self, blob_name: str, expiration_hours: int = 24) -> Optional[str]:
        """
        Generate a signed URL for private access to a blob.
        
        Args:
            blob_name: Name of the blob in the bucket
            expiration_hours: Hours until the URL expires
            
        Returns:
            str: Signed URL, None if failed
        """
        try:
            if not self.client or not self.bucket:
                if not self.initialize():
                    return None
            
            blob = self.bucket.blob(blob_name)
            
            from datetime import datetime, timedelta
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            signed_url = blob.generate_signed_url(expiration=expiration)
            return signed_url
            
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from the bucket.
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.client or not self.bucket:
                if not self.initialize():
                    return False
            
            blob = self.bucket.blob(blob_name)
            blob.delete()
            
            print(f"Successfully deleted blob: {blob_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting blob: {e}")
            return False
    
    def list_blobs(self, prefix: Optional[str] = None) -> list:
        """
        List blobs in the bucket.
        
        Args:
            prefix: Optional prefix to filter blobs
            
        Returns:
            list: List of blob names
        """
        try:
            if not self.client or not self.bucket:
                if not self.initialize():
                    return []
            
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            print(f"Error listing blobs: {e}")
            return []
    
    def upload_geojson(self, geojson_data: Dict[str, Any], user_api_key: str, 
                      request_id: str, data_type: str, query_type: str) -> Optional[str]:
        """
        Upload GeoJSON data with standardized naming convention.
        
        Args:
            geojson_data: GeoJSON data to upload
            user_api_key: User's API key for folder organization
            request_id: Unique request ID
            data_type: Type of data (potholes, uhi)
            query_type: Type of query (region, path)
            
        Returns:
            str: Public URL to uploaded file, None if failed
        """
        destination_path = f"results/user_{user_api_key}/{request_id}_{data_type}_{query_type}.geojson"
        return self.upload_json_data(geojson_data, destination_path, 'application/geojson')
    
    def upload_tiff(self, file_path: str, user_api_key: str, 
                   request_id: str, data_type: str, query_type: str) -> Optional[str]:
        """
        Upload TIFF data with standardized naming convention.
        
        Args:
            file_path: Local path to TIFF file
            user_api_key: User's API key for folder organization
            request_id: Unique request ID
            data_type: Type of data (potholes, uhi)
            query_type: Type of query (region, path)
            
        Returns:
            str: Public URL to uploaded file, None if failed
        """
        destination_path = f"results/user_{user_api_key}/{request_id}_{data_type}_{query_type}.tif"
        return self.upload_file(file_path, destination_path, 'image/tiff')


# Global cloud storage service instance
storage_service = CloudStorageService()