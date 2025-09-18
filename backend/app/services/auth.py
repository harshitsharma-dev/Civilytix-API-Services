from fastapi import Header, HTTPException, Depends
from typing import Optional, Dict, Any
import uuid

from app.core.config import settings


class AuthService:
    """Service for handling authentication and authorization with GCS storage."""
    
    def __init__(self):
        self.users_cache = None
        self.last_cache_update = None
    
    def _get_users_data(self):
        """Get users data from GCS bucket with caching."""
        from app.services.storage import storage_service
        
        # Ensure storage service is initialized
        if not hasattr(storage_service, 'client') or storage_service.client is None:
            storage_service.initialize()
        
        # Simple caching to avoid frequent GCS calls
        if self.users_cache is None:
            self.users_cache = storage_service.get_users_data()
            if not self.users_cache:
                print("Warning: No users data found in storage, using empty dataset")
                self.users_cache = {"users": {}, "api_keys": {}}
        
        return self.users_cache
    
    def _save_users_data(self, users_data):
        """Save updated users data to GCS bucket."""
        from app.services.storage import storage_service
        
        success = storage_service.save_users_data(users_data)
        if success:
            self.users_cache = users_data  # Update cache
        return success
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            Dict: User data or None if not found
        """
        users_data = self._get_users_data()
        
        for user_id, user_info in users_data.get("users", {}).items():
            if user_info.get("email") == email:
                return user_info
        
        return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Get user by API key.
        
        Args:
            api_key: User's API key
            
        Returns:
            Dict: User data or None if not found
        """
        users_data = self._get_users_data()
        
        # Get user_id from api_keys mapping
        user_id = users_data.get("api_keys", {}).get(api_key)
        if not user_id:
            return None
        
        # Get user data
        return users_data.get("users", {}).get(user_id)
    
    def upgrade_user_to_premium(self, user_id: str) -> bool:
        """
        Upgrade user to premium status and save to GCS.
        
        Args:
            user_id: User's ID to upgrade
            
        Returns:
            bool: True if successful, False otherwise
        """
        users_data = self._get_users_data()
        
        if user_id not in users_data.get("users", {}):
            print(f"User {user_id} not found")
            return False
        
        # Update user to premium
        users_data["users"][user_id]["subscription_status"] = "premium"
        from datetime import datetime
        users_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        # Save back to GCS
        success = self._save_users_data(users_data)
        if success:
            print(f"Successfully upgraded user {user_id} to premium")
        else:
            print(f"Failed to save premium upgrade for user {user_id}")
        
        return success
    
    @staticmethod
    def verify_api_key(x_api_key: str = Header(..., description="API key for authentication")) -> str:
        """
        Dependency function to verify the API key provided in the X-API-Key header.
        
        Args:
            x_api_key: API key from the request header
            
        Returns:
            str: The validated API key
            
        Raises:
            HTTPException: If the API key is invalid
        """
        # Create instance to check against GCS user data
        auth_service_instance = AuthService()
        user = auth_service_instance.get_user_by_api_key(x_api_key)
        
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid API Key"
            )
        return x_api_key
    
    @staticmethod
    def get_current_user(api_key: str = Depends(verify_api_key)) -> Dict[str, Any]:
        """
        Get the current user based on the API key.
        
        Args:
            api_key: Validated API key
            
        Returns:
            Dict: User data from GCS storage
            
        Raises:
            HTTPException: If user is not found
        """
        auth_service_instance = AuthService()
        user = auth_service_instance.get_user_by_api_key(api_key)
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )
        return user
    
    @staticmethod
    def check_premium_status(user: Dict[str, Any]) -> bool:
        """
        Check if user has premium status.
        
        Args:
            user: User data from GCS storage
            
        Returns:
            bool: True if user has premium status, False otherwise
        """
        return user.get("subscription_status") == "premium"
    
    @staticmethod
    def require_premium(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """
        Dependency that requires user to have premium status.
        
        Args:
            user: Current user from get_current_user dependency
            
        Returns:
            Dict: User data if premium status is valid
            
        Raises:
            HTTPException: If user doesn't have premium (402 Payment Required)
        """
        if not AuthService.check_premium_status(user):
            raise HTTPException(
                status_code=402,
                detail={
                    "status": "error",
                    "message": "Premium subscription required. Please upgrade to access this feature.",
                    "upgrade_required": True
                }
            )
        return user


# Create an instance for easy importing
auth_service = AuthService()