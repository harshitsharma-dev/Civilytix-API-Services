from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.schemas import RegionRequest, PathRequest, APIResponse
from app.services.auth import auth_service
from app.services.database import db_service
from app.services.geospatial import geo_service
from app.services.storage import storage_service
from app.services.cost_tracker import cost_tracker

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/region", response_model=APIResponse)
async def get_data_region(
    request_data: RegionRequest, 
    user: Dict[str, Any] = Depends(auth_service.require_payment)
) -> APIResponse:
    """
    Retrieves geospatial data for a specified region based on user payment status.
    
    Args:
        request_data: Region request parameters
        user: Authenticated user with paid status
        
    Returns:
        APIResponse: Success response with download URL
    """
    try:
        # Generate unique request ID and metadata
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        endpoint = "/api/data/region"
        request_params = request_data.dict()
        
        # Validate center coordinates
        center_lat = request_data.center.get("lat")
        center_lon = request_data.center.get("lon")
        
        if center_lat is None or center_lon is None:
            raise HTTPException(
                status_code=400, 
                detail="Invalid center coordinates provided."
            )
        
        # Calculate real-time cost for this request
        user_tier = cost_tracker.get_user_tier(user.get("paymentStatus", "unpaid"))
        cost_calculation = cost_tracker.calculate_region_cost(
            user_tier=user_tier,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=request_data.radius_km,
            data_type=request_data.dataType
        )
        
        # Get geospatial data based on data type
        retrieved_data = geo_service.get_data_by_region(
            center_lat, center_lon, request_data.radius_km, request_data.dataType
        )
        
        # Save data to cloud storage
        if request_data.dataType == "potholes":
            result_url = storage_service.upload_geojson(
                retrieved_data, user["api_key"], request_id, 
                request_data.dataType, "region"
            )
        elif request_data.dataType == "uhi":
            # For UHI data, we would typically upload a TIFF file
            # For now, we'll upload the placeholder JSON data
            result_url = storage_service.upload_json_data(
                retrieved_data, 
                f"results/user_{user['api_key']}/{request_id}_uhi_region.json"
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid dataType specified. Must be 'potholes' or 'uhi'."
            )
        
        if not result_url:
            raise HTTPException(
                status_code=500, 
                detail="Error saving data to cloud storage."
            )
        
        # Log request in user history
        log_entry = {
            "requestId": request_id,
            "timestamp": timestamp,
            "endpoint": endpoint,
            "requestParams": request_params,
            "resultUrl": result_url
        }
        
        success = db_service.add_request_to_history(user["_id"], log_entry)
        if not success:
            print(f"Warning: Failed to log request {request_id} to user history")
        
        return APIResponse(
            status="success",
            message="Your data is ready for download.",
            requestId=request_id,
            downloadUrl=result_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_data_region: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while processing your request."
        )


@router.post("/path", response_model=APIResponse)
async def get_data_path(
    request_data: PathRequest,
    user: Dict[str, Any] = Depends(auth_service.require_payment)
) -> APIResponse:
    """
    Retrieves geospatial data for a specified path based on user payment status.
    
    Args:
        request_data: Path request parameters
        user: Authenticated user with paid status
        
    Returns:
        APIResponse: Success response with download URL
    """
    try:
        # Generate unique request ID and metadata
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        endpoint = "/api/data/path"
        request_params = request_data.dict()
        
        # Validate coordinates
        start_lat = request_data.start_coords.get("lat")
        start_lon = request_data.start_coords.get("lon")
        end_lat = request_data.end_coords.get("lat")
        end_lon = request_data.end_coords.get("lon")
        
        if None in [start_lat, start_lon, end_lat, end_lon]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid start or end coordinates provided."
            )
        
        # Get geospatial data based on data type
        retrieved_data = geo_service.get_data_by_path(
            start_lat, start_lon, end_lat, end_lon, 
            request_data.buffer_meters, request_data.dataType
        )
        
        # Save data to cloud storage
        if request_data.dataType == "potholes":
            result_url = storage_service.upload_geojson(
                retrieved_data, user["api_key"], request_id, 
                request_data.dataType, "path"
            )
        elif request_data.dataType == "uhi":
            # For UHI data, we would typically upload a TIFF file
            # For now, we'll upload the placeholder JSON data
            result_url = storage_service.upload_json_data(
                retrieved_data, 
                f"results/user_{user['api_key']}/{request_id}_uhi_path.json"
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid dataType specified. Must be 'potholes' or 'uhi'."
            )
        
        if not result_url:
            raise HTTPException(
                status_code=500, 
                detail="Error saving data to cloud storage."
            )
        
        # Log request in user history
        log_entry = {
            "requestId": request_id,
            "timestamp": timestamp,
            "endpoint": endpoint,
            "requestParams": request_params,
            "resultUrl": result_url
        }
        
        success = db_service.add_request_to_history(user["_id"], log_entry)
        if not success:
            print(f"Warning: Failed to log request {request_id} to user history")
        
        return APIResponse(
            status="success",
            message="Your data is ready for download.",
            requestId=request_id,
            downloadUrl=result_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_data_path: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while processing your request."
        )


@router.post("/estimate-cost/region")
async def estimate_region_cost(
    request_data: RegionRequest, 
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> Dict[str, Any]:
    """
    Estimate the cost for a region-based data request without processing.
    
    Args:
        request_data: Region request parameters
        user: Authenticated user
        
    Returns:
        Dict: Cost estimation details
    """
    try:
        # Validate center coordinates
        center_lat = request_data.center.get("lat")
        center_lon = request_data.center.get("lon")
        
        if center_lat is None or center_lon is None:
            raise HTTPException(
                status_code=400, 
                detail="Invalid center coordinates provided."
            )
        
        # Calculate cost estimation
        user_tier = cost_tracker.get_user_tier(user.get("paymentStatus", "unpaid"))
        cost_calculation = cost_tracker.calculate_region_cost(
            user_tier=user_tier,
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=request_data.radius_km,
            data_type=request_data.dataType
        )
        
        # Calculate area for additional info
        area_km2 = 3.14159 * (request_data.radius_km ** 2)
        estimated_size_mb = cost_tracker.estimate_data_size(
            request_data.dataType, area_km2=area_km2
        )
        
        return {
            "requestType": "region",
            "userTier": user_tier.value,
            "costBreakdown": cost_calculation.to_dict(),
            "estimatedDataSizeMb": round(estimated_size_mb, 2),
            "coverageAreaKm2": round(area_km2, 2),
            "dataType": request_data.dataType,
            "message": f"Estimated cost: ${cost_calculation.total_cost:.4f} USD"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error estimating region cost: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while estimating cost."
        )


@router.post("/estimate-cost/path")
async def estimate_path_cost(
    request_data: PathRequest, 
    user: Dict[str, Any] = Depends(auth_service.get_current_user)
) -> Dict[str, Any]:
    """
    Estimate the cost for a path-based data request without processing.
    
    Args:
        request_data: Path request parameters
        user: Authenticated user
        
    Returns:
        Dict: Cost estimation details
    """
    try:
        # Validate coordinates
        start_lat = request_data.start_coords.get("lat")
        start_lon = request_data.start_coords.get("lon")
        end_lat = request_data.end_coords.get("lat")
        end_lon = request_data.end_coords.get("lon")
        
        if any(coord is None for coord in [start_lat, start_lon, end_lat, end_lon]):
            raise HTTPException(
                status_code=400, 
                detail="Invalid coordinates provided."
            )
        
        # Calculate cost estimation
        user_tier = cost_tracker.get_user_tier(user.get("paymentStatus", "unpaid"))
        cost_calculation = cost_tracker.calculate_path_cost(
            user_tier=user_tier,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            buffer_meters=request_data.buffer_meters,
            data_type=request_data.dataType
        )
        
        # Calculate path length for additional info
        from math import radians, cos, sin, asin, sqrt
        lat1, lon1, lat2, lon2 = map(radians, [start_lat, start_lon, end_lat, end_lon])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        path_length_km = 2 * asin(sqrt(a)) * 6371
        
        estimated_size_mb = cost_tracker.estimate_data_size(
            request_data.dataType, path_length_km=path_length_km
        )
        
        return {
            "requestType": "path",
            "userTier": user_tier.value,
            "costBreakdown": cost_calculation.to_dict(),
            "estimatedDataSizeMb": round(estimated_size_mb, 2),
            "pathLengthKm": round(path_length_km, 2),
            "bufferWidthM": request_data.buffer_meters,
            "dataType": request_data.dataType,
            "message": f"Estimated cost: ${cost_calculation.total_cost:.4f} USD"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error estimating path cost: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while estimating cost."
        )