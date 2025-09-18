from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

from app.models.schemas import HistoryResponse, DownloadResponse, SimpleLogin, UserProfile, PaymentRequest, APIResponse
from app.services.auth import auth_service, AuthService
from app.services.database import db_service

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/login", response_model=UserProfile)
async def login_user(login_data: SimpleLogin) -> UserProfile:
    """
    Simple login endpoint that returns user profile if found.
    
    Args:
        login_data: Login request with email
        
    Returns:
        UserProfile: User's profile information
    """
    try:
        user = auth_service.get_user_by_email(login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found. Please check your email address."
            )
        
        # Return user profile with API key
        return UserProfile(
            user_id=user["user_id"],
            email=user["email"],
            full_name=user["full_name"],
            subscription_status=user["subscription_status"],
            created_at=user["created_at"],
            api_key=user.get("api_key")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during login."
        )


@router.post("/upgrade", response_model=APIResponse)
async def upgrade_to_premium(
    payment_data: PaymentRequest,
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> APIResponse:
    """
    Upgrade user to premium subscription.
    
    Args:
        payment_data: Payment request with plan details
        user: Current authenticated user
        
    Returns:
        APIResponse: Success response with upgrade confirmation
    """
    try:
        # Verify user is upgrading themselves or is authorized
        if user["user_id"] != payment_data.user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only upgrade your own account."
            )
        
        # Check if user is already premium
        if user["subscription_status"] == "premium":
            return APIResponse(
                status="success",
                message="User is already premium subscriber.",
                data={
                    "user_id": user["user_id"],
                    "subscription_status": "premium",
                    "plan_type": payment_data.plan_type
                }
            )
        
        # Process upgrade
        auth_svc = AuthService()
        success = auth_svc.upgrade_user_to_premium(user["user_id"])
        
        if success:
            return APIResponse(
                status="success",
                message=f"Successfully upgraded to premium ({payment_data.plan_type} plan)!",
                data={
                    "user_id": user["user_id"],
                    "subscription_status": "premium",
                    "plan_type": payment_data.plan_type,
                    "upgraded_at": datetime.utcnow().isoformat() + "Z"
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to process premium upgrade. Please try again."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during upgrade: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during upgrade."
        )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> UserProfile:
    """
    Get current user's profile information.
    
    Args:
        user: Current authenticated user
        
    Returns:
        UserProfile: User's profile information
    """
    try:
        return UserProfile(
            user_id=user["user_id"],
            email=user["email"],
            full_name=user["full_name"],
            subscription_status=user["subscription_status"],
            created_at=user["created_at"]
        )
        
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving profile."
        )


@router.get("/history", response_model=HistoryResponse)
async def get_user_history(
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> HistoryResponse:
    """
    Retrieves the request history for the authenticated user.
    
    Args:
        user: Authenticated user
        
    Returns:
        HistoryResponse: User's request history
    """
    try:
        # Get user's request history from database
        history = user.get("requestHistory", [])
        
        # Format timestamps to ISO 8601 string for JSON serialization
        formatted_history = []
        for entry in history:
            formatted_entry = entry.copy()
            if isinstance(formatted_entry.get("timestamp"), datetime):
                formatted_entry["timestamp"] = formatted_entry["timestamp"].isoformat() + 'Z'
            formatted_history.append(formatted_entry)
        
        return HistoryResponse(history=formatted_history)
        
    except Exception as e:
        print(f"Error retrieving user history: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while retrieving user history."
        )


@router.get("/history/{request_id}", response_model=DownloadResponse)
async def get_specific_previous_output(
    request_id: str,
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> DownloadResponse:
    """
    Retrieves the download URL for a specific previous request.
    
    Args:
        request_id: ID of the specific request
        user: Authenticated user
        
    Returns:
        DownloadResponse: Request ID and download URL
    """
    try:
        # Search user's request history for the specific request
        request_history = user.get("requestHistory", [])
        specific_request = None
        
        for entry in request_history:
            if entry.get("requestId") == request_id:
                specific_request = entry
                break
        
        if not specific_request:
            raise HTTPException(
                status_code=404, 
                detail="Request ID not found in user history."
            )
        
        return DownloadResponse(
            requestId=request_id,
            downloadUrl=specific_request.get("resultUrl")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving specific request: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while retrieving request details."
        )



@router.post("/process-payment", response_model=APIResponse)


@router.get("/stats")
async def get_user_stats(
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> Dict[str, Any]:
    """
    Get user usage statistics.
    
    Args:
        user: Authenticated user
        
    Returns:
        Dict: User statistics
    """
    try:
        request_history = user.get("requestHistory", [])
        
        # Calculate basic statistics
        total_requests = len(request_history)
        
        # Count requests by endpoint
        endpoint_counts = {}
        data_type_counts = {}
        
        for entry in request_history:
            endpoint = entry.get("endpoint", "unknown")
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
            
            # Extract data type from request parameters
            request_params = entry.get("requestParams", {})
            data_type = request_params.get("dataType", "unknown")
            data_type_counts[data_type] = data_type_counts.get(data_type, 0) + 1
        
        # Get most recent request date
        most_recent_request = None
        if request_history:
            latest_entry = max(request_history, key=lambda x: x.get("timestamp", datetime.min))
            most_recent_request = latest_entry.get("timestamp")
            if isinstance(most_recent_request, datetime):
                most_recent_request = most_recent_request.isoformat() + 'Z'
        
        stats = {
            "totalRequests": total_requests,
            "endpointUsage": endpoint_counts,
            "dataTypeUsage": data_type_counts,
            "mostRecentRequest": most_recent_request,
            "paymentStatus": user.get("paymentStatus")
        }
        
        return stats
        
    except Exception as e:
        print(f"Error calculating user stats: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while calculating user statistics."
        )