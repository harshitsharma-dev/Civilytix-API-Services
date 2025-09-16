from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class RegionRequest(BaseModel):
    """Request model for region-based data retrieval."""
    center: Dict[str, float]  # {"lat": float, "lon": float}
    radius_km: float
    dataType: str  # "potholes" or "uhi"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "center": {"lat": 12.9141, "lon": 79.1325},
                "radius_km": 5.0,
                "dataType": "potholes"
            }
        }
    }


class PathRequest(BaseModel):
    """Request model for path-based data retrieval."""
    start_coords: Dict[str, float]  # {"lat": float, "lon": float}
    end_coords: Dict[str, float]    # {"lat": float, "lon": float}
    buffer_meters: float
    dataType: str  # "potholes" or "uhi"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "start_coords": {"lat": 12.9141, "lon": 79.1325},
                "end_coords": {"lat": 12.9200, "lon": 79.1400},
                "buffer_meters": 100.0,
                "dataType": "potholes"
            }
        }
    }


class RequestHistoryEntry(BaseModel):
    """Model for request history entry."""
    requestId: str
    timestamp: datetime
    endpoint: str
    requestParams: Dict
    resultUrl: str


class User(BaseModel):
    """User model for database operations."""
    email: str
    paymentStatus: str  # "paid" or "unpaid"
    api_key: Optional[str] = None
    requestHistory: List[RequestHistoryEntry] = []
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "paymentStatus": "paid",
                "api_key": "user3_paid_token",
                "requestHistory": []
            }
        }
    }


class APIResponse(BaseModel):
    """Standard API response model."""
    status: str
    message: str
    requestId: Optional[str] = None
    downloadUrl: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = "error"
    message: str


class HistoryResponse(BaseModel):
    """Response model for user history."""
    history: List[RequestHistoryEntry]


class DownloadResponse(BaseModel):
    """Response model for download URL."""
    requestId: str
    downloadUrl: str