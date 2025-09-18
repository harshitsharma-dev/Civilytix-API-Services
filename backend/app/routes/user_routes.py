from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta

from app.models.schemas import HistoryResponse, DownloadResponse
from app.services.auth import auth_service
from app.services.database import db_service
from app.services.cost_tracker import cost_tracker

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


@router.get("/cost-summary")
async def get_cost_summary(
    user: Dict[str, Any] = Depends(auth_service.get_current_user),
    days: int = 30
) -> Dict[str, Any]:
    """
    Get cost summary for the specified period.
    
    Args:
        user: Authenticated user
        days: Number of days to look back (default: 30)
        
    Returns:
        Dict: Cost summary data
    """
    try:
        request_history = user.get("requestHistory", [])
        
        # Calculate usage summary
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        usage_summary = cost_tracker.get_usage_summary(
            request_history, start_date, end_date
        )
        
        # Get user tier info
        user_tier = cost_tracker.get_user_tier(user.get("paymentStatus", "unpaid"))
        
        # Calculate current month usage for limits check
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_requests = len([
            entry for entry in request_history
            if entry.get("timestamp") and 
            (isinstance(entry["timestamp"], datetime) and entry["timestamp"] >= current_month_start or
             isinstance(entry["timestamp"], str) and datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')) >= current_month_start)
        ])
        
        current_month_data_mb = sum([
            entry.get("dataSizeMb", 0) for entry in request_history
            if entry.get("timestamp") and 
            (isinstance(entry["timestamp"], datetime) and entry["timestamp"] >= current_month_start or
             isinstance(entry["timestamp"], str) and datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00')) >= current_month_start)
        ])
        
        # Check usage limits
        usage_limits = cost_tracker.check_usage_limits(
            user_tier, current_month_requests, current_month_data_mb
        )
        
        return {
            "userTier": user_tier.value,
            "summaryPeriod": f"Last {days} days",
            "usageSummary": usage_summary.to_dict(),
            "currentMonthUsage": usage_limits,
            "projectedMonthlyCost": round(usage_summary.total_cost * (30 / days), 2) if days > 0 else 0
        }
        
    except Exception as e:
        print(f"Error generating cost summary: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while generating cost summary."
        )


@router.get("/cost-breakdown/{request_id}")
async def get_request_cost_breakdown(
    request_id: str,
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed cost breakdown for a specific request.
    
    Args:
        request_id: ID of the specific request
        user: Authenticated user
        
    Returns:
        Dict: Detailed cost breakdown
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
        
        # Extract cost information
        cost_info = specific_request.get("cost", {})
        
        if not cost_info:
            # For older requests without cost info, estimate based on parameters
            params = specific_request.get("requestParams", {})
            user_tier = cost_tracker.get_user_tier(user.get("paymentStatus", "unpaid"))
            
            if "radius_km" in params:  # Region request
                cost_calculation = cost_tracker.calculate_region_cost(
                    user_tier=user_tier,
                    center_lat=params.get("center", {}).get("lat", 0),
                    center_lon=params.get("center", {}).get("lon", 0),
                    radius_km=params.get("radius_km", 1),
                    data_type=params.get("dataType", "potholes")
                )
            else:  # Path request
                cost_calculation = cost_tracker.calculate_path_cost(
                    user_tier=user_tier,
                    start_lat=params.get("start_coords", {}).get("lat", 0),
                    start_lon=params.get("start_coords", {}).get("lon", 0),
                    end_lat=params.get("end_coords", {}).get("lat", 0),
                    end_lon=params.get("end_coords", {}).get("lon", 0),
                    buffer_meters=params.get("buffer_meters", 100),
                    data_type=params.get("dataType", "potholes")
                )
            cost_info = cost_calculation.to_dict()
        
        return {
            "requestId": request_id,
            "timestamp": specific_request.get("timestamp"),
            "endpoint": specific_request.get("endpoint"),
            "dataType": specific_request.get("requestParams", {}).get("dataType"),
            "userTier": specific_request.get("userTier", "unknown"),
            "costBreakdown": cost_info,
            "dataSizeMb": specific_request.get("dataSizeMb", 0),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving cost breakdown: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while retrieving cost breakdown."
        )