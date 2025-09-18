from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class SimpleLogin(BaseModel):
    """Simple login request model."""
    email: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com"
            }
        }
    }


class UserProfile(BaseModel):
    """User profile response model."""
    user_id: str
    email: str
    full_name: str
    subscription_status: str  # "free", "premium"
    created_at: str
    api_key: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123456",
                "email": "user@example.com", 
                "full_name": "John Doe",
                "subscription_status": "premium",
                "created_at": "2024-01-01T00:00:00Z",
                "api_key": "premium_user_key_001"
            }
        }
    }


class PaymentRequest(BaseModel):
    """Payment processing request model."""
    user_id: str
    plan_type: str  # "monthly", "yearly"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123456",
                "plan_type": "monthly"
            }
        }
    }


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
    """Simple user model for GCS storage."""
    user_id: str
    email: str
    full_name: str
    subscription_status: str  # "free", "premium"
    created_at: str
    api_key: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user_123456",
                "email": "user@example.com",
                "full_name": "John Doe",
                "subscription_status": "premium",
                "created_at": "2024-01-01T00:00:00Z",
                "api_key": "user3_paid_token"
            }
        }
    }


class APIResponse(BaseModel):
    """Standard API response model."""
    status: str
    message: str
    requestId: Optional[str] = None
    downloadUrl: Optional[str] = None
    data: Optional[Dict] = None  # Direct data payload


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