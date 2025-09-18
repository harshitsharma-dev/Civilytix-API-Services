from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.schemas import RegionRequest, PathRequest, APIResponse
from app.services.auth import auth_service
from app.services.database import db_service
from app.services.geospatial import geo_service
from app.services.storage import storage_service

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/region", response_model=APIResponse)
async def get_data_region(
    request_data: RegionRequest, 
    user: Dict[str, Any] = Depends(auth_service.require_premium)
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
        
        # Get geospatial data based on data type
        retrieved_data = geo_service.get_data_by_region(
            center_lat, center_lon, request_data.radius_km, request_data.dataType
        )
        
        # Return data directly instead of saving to cloud storage
        return APIResponse(
            status="success",
            message="Geospatial data retrieved successfully.",
            requestId=request_id,
            data=retrieved_data  # Return data directly
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
    user: Dict[str, Any] = Depends(auth_service.require_premium)
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
        
        # Return data directly instead of saving to cloud storage
        return APIResponse(
            status="success",
            message="Geospatial data retrieved successfully.",
            requestId=request_id,
            data=retrieved_data  # Return data directly
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_data_path: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while processing your request."
        )