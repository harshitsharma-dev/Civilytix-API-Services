from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class CostTier(str, Enum):
    """User tier for cost calculations"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class CostCalculation(BaseModel):
    """Cost calculation details"""
    base_cost: float
    data_volume_cost: float
    processing_cost: float
    total_cost: float
    credits_used: float
    tier: CostTier


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


class UsageInstanceResponse(BaseModel):
    """Response model for usage instance"""
    request_id: str
    timestamp: datetime
    endpoint: str
    method: str
    user_id: Optional[str]
    user_tier: CostTier
    request_params: Dict[str, Any]
    response_status: int
    processing_time_ms: float
    data_volume_mb: float
    cost_calculation: CostCalculation
    ip_address: Optional[str]


class UsageMetricsResponse(BaseModel):
    """Response model for usage metrics"""
    total_requests: int
    total_cost: float
    average_response_time: float
    error_rate: float
    requests_by_tier: Dict[str, int]
    cost_by_tier: Dict[str, float]


class EndpointUsageResponse(BaseModel):
    """Response model for endpoint usage statistics"""
    endpoint: str
    request_count: int
    total_cost: float
    average_response_time: float
    error_count: int
    last_accessed: Optional[datetime]