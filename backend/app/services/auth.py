from fastapi import Header, HTTPException, Depends
from typing import Optional, Dict, Any

from app.core.config import settings


class AuthService:
    """Service for handling authentication and authorization."""
    
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
        if x_api_key not in settings.VALID_API_KEYS:
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
            Dict: User data from database
            
        Raises:
            HTTPException: If user is not found
        """
        # Import here to avoid circular dependency
        from app.services.database import db_service
        
        user = db_service.get_user_by_api_key(api_key)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )
        return user
    
    @staticmethod
    def check_payment_status(user: Dict[str, Any]) -> bool:
        """
        Check if user has paid status.
        
        Args:
            user: User data from database
            
        Returns:
            bool: True if user has paid, False otherwise
        """
        return user.get("paymentStatus") == "paid"
    
    @staticmethod
    def require_payment(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """
        Dependency that requires user to have paid status.
        
        Args:
            user: Current user from get_current_user dependency
            
        Returns:
            Dict: User data if payment status is valid
            
        Raises:
            HTTPException: If user hasn't paid (402 Payment Required)
        """
        if not AuthService.check_payment_status(user):
            raise HTTPException(
                status_code=402,
                detail={
                    "status": "error",
                    "message": "Access denied. Please complete payment to use this feature."
                }
            )
        return user


# Create an instance for easy importing
auth_service = AuthService()