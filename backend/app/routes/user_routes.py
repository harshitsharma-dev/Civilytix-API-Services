from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

from app.models.schemas import HistoryResponse, DownloadResponse
from app.services.auth import auth_service
from app.services.database import db_service

router = APIRouter(prefix="/user", tags=["user"])


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


@router.get("/profile")
async def get_user_profile(
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> Dict[str, Any]:
    """
    Get basic user profile information.
    
    Args:
        user: Authenticated user
        
    Returns:
        Dict: User profile data
    """
    try:
        # Return basic user info without sensitive data
        profile = {
            "email": user.get("email"),
            "paymentStatus": user.get("paymentStatus"),
            "requestCount": len(user.get("requestHistory", [])),
            "memberSince": user.get("created_at"),
        }
        
        return profile
        
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while retrieving user profile."
        )


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