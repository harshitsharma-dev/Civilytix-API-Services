# app/services/cost_tracker.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class CostTier(Enum):
    """Cost tiers for different user types"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class CostCalculation:
    """Represents the cost breakdown for an API request"""
    base_cost: float
    data_volume_cost: float
    processing_cost: float
    storage_cost: float
    total_cost: float
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseCost": self.base_cost,
            "dataVolumeCost": self.data_volume_cost,
            "processingCost": self.processing_cost,
            "storageCost": self.storage_cost,
            "totalCost": self.total_cost,
            "currency": self.currency
        }


@dataclass
class UsageSummary:
    """Summary of usage and costs for a time period"""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_cost: float
    cost_by_endpoint: Dict[str, float]
    cost_by_data_type: Dict[str, float]
    data_volume_gb: float
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "periodStart": self.period_start.isoformat(),
            "periodEnd": self.period_end.isoformat(),
            "totalRequests": self.total_requests,
            "totalCost": self.total_cost,
            "costByEndpoint": self.cost_by_endpoint,
            "costByDataType": self.cost_by_data_type,
            "dataVolumeGb": self.data_volume_gb,
            "currency": self.currency
        }


class CostTracker:
    """Service for calculating and tracking API usage costs"""
    
    def __init__(self):
        # Pricing configuration (per request)
        self.pricing = {
            CostTier.FREE: {
                "base_cost": 0.0,
                "data_volume_per_mb": 0.0,
                "processing_multiplier": 0.0,
                "storage_per_mb": 0.0,
                "max_requests_per_month": 100,
                "max_data_volume_mb": 50
            },
            CostTier.BASIC: {
                "base_cost": 0.05,  # $0.05 per request
                "data_volume_per_mb": 0.01,  # $0.01 per MB
                "processing_multiplier": 1.0,
                "storage_per_mb": 0.005,  # $0.005 per MB stored
                "max_requests_per_month": 1000,
                "max_data_volume_mb": 1000
            },
            CostTier.PREMIUM: {
                "base_cost": 0.03,  # $0.03 per request (volume discount)
                "data_volume_per_mb": 0.008,  # $0.008 per MB
                "processing_multiplier": 1.2,  # Premium processing
                "storage_per_mb": 0.003,  # $0.003 per MB stored
                "max_requests_per_month": 10000,
                "max_data_volume_mb": 10000
            },
            CostTier.ENTERPRISE: {
                "base_cost": 0.02,  # $0.02 per request (enterprise discount)
                "data_volume_per_mb": 0.005,  # $0.005 per MB
                "processing_multiplier": 1.5,  # Enterprise processing
                "storage_per_mb": 0.002,  # $0.002 per MB stored
                "max_requests_per_month": -1,  # Unlimited
                "max_data_volume_mb": -1  # Unlimited
            }
        }
        
        # Processing cost multipliers based on data type
        self.data_type_multipliers = {
            "potholes": 1.0,  # Base processing
            "uhi": 1.5,  # More complex processing for UHI data
            "combined": 2.0  # Combined data requests
        }
        
        # Regional cost multipliers
        self.region_multipliers = {
            "local": 1.0,  # Local/cached data
            "national": 1.2,  # National coverage
            "global": 1.5  # Global coverage
        }
    
    def get_user_tier(self, payment_status: str) -> CostTier:
        """Determine user's cost tier based on payment status"""
        tier_mapping = {
            "unpaid": CostTier.FREE,
            "basic": CostTier.BASIC,
            "paid": CostTier.PREMIUM,
            "premium": CostTier.PREMIUM,
            "enterprise": CostTier.ENTERPRISE
        }
        return tier_mapping.get(payment_status, CostTier.FREE)
    
    def estimate_data_size(self, data_type: str, area_km2: float = None, 
                          path_length_km: float = None) -> float:
        """Estimate data size in MB based on request parameters"""
        # Base data density estimates (MB per km²)
        density_estimates = {
            "potholes": 0.5,  # 0.5 MB per km² for pothole data
            "uhi": 2.0,  # 2.0 MB per km² for heat island data
            "combined": 3.0  # Combined data
        }
        
        density = density_estimates.get(data_type, 1.0)
        
        if area_km2:
            # For region requests
            return area_km2 * density
        elif path_length_km:
            # For path requests (assume 1km buffer width)
            return path_length_km * 2 * density  # 2km total width
        else:
            # Default estimate
            return 1.0
    
    def calculate_request_cost(self, 
                             user_tier: CostTier,
                             data_type: str,
                             estimated_size_mb: float,
                             region_type: str = "local",
                             priority: str = "normal") -> CostCalculation:
        """Calculate the cost for a specific API request"""
        
        pricing = self.pricing[user_tier]
        
        # Base cost per request
        base_cost = pricing["base_cost"]
        
        # Data volume cost
        data_volume_cost = estimated_size_mb * pricing["data_volume_per_mb"]
        
        # Processing cost (includes data type and region multipliers)
        processing_multiplier = (
            pricing["processing_multiplier"] * 
            self.data_type_multipliers.get(data_type, 1.0) *
            self.region_multipliers.get(region_type, 1.0)
        )
        
        # Priority processing surcharge
        priority_multiplier = 1.5 if priority == "high" else 1.0
        
        processing_cost = base_cost * processing_multiplier * priority_multiplier
        
        # Storage cost
        storage_cost = estimated_size_mb * pricing["storage_per_mb"]
        
        # Total cost
        total_cost = base_cost + data_volume_cost + processing_cost + storage_cost
        
        return CostCalculation(
            base_cost=round(base_cost, 4),
            data_volume_cost=round(data_volume_cost, 4),
            processing_cost=round(processing_cost, 4),
            storage_cost=round(storage_cost, 4),
            total_cost=round(total_cost, 4)
        )
    
    def calculate_region_cost(self, 
                            user_tier: CostTier,
                            center_lat: float,
                            center_lon: float,
                            radius_km: float,
                            data_type: str) -> CostCalculation:
        """Calculate cost for a region-based request"""
        
        # Calculate area
        area_km2 = 3.14159 * (radius_km ** 2)
        
        # Estimate data size
        estimated_size_mb = self.estimate_data_size(data_type, area_km2=area_km2)
        
        # Determine region type based on coordinates (simplified)
        region_type = "local" if abs(center_lat) < 30 else "global"
        
        return self.calculate_request_cost(
            user_tier, data_type, estimated_size_mb, region_type
        )
    
    def calculate_path_cost(self,
                           user_tier: CostTier,
                           start_lat: float,
                           start_lon: float,
                           end_lat: float,
                           end_lon: float,
                           buffer_meters: float,
                           data_type: str) -> CostCalculation:
        """Calculate cost for a path-based request"""
        
        # Calculate approximate path length using Haversine formula
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1, lat2, lon2 = map(radians, [start_lat, start_lon, end_lat, end_lon])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        path_length_km = 2 * asin(sqrt(a)) * 6371  # Earth radius in km
        
        # Estimate data size
        estimated_size_mb = self.estimate_data_size(data_type, path_length_km=path_length_km)
        
        # Determine region type
        region_type = "local" if abs(start_lat) < 30 and abs(end_lat) < 30 else "global"
        
        return self.calculate_request_cost(
            user_tier, data_type, estimated_size_mb, region_type
        )
    
    def get_usage_summary(self, 
                         user_history: List[Dict[str, Any]], 
                         start_date: datetime = None,
                         end_date: datetime = None) -> UsageSummary:
        """Calculate usage summary for a given period"""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Filter history by date range
        filtered_history = []
        for entry in user_history:
            entry_date = entry.get("timestamp")
            if isinstance(entry_date, str):
                entry_date = datetime.fromisoformat(entry_date.replace('Z', '+00:00'))
            elif isinstance(entry_date, datetime):
                pass
            else:
                continue
                
            if start_date <= entry_date <= end_date:
                filtered_history.append(entry)
        
        # Calculate totals
        total_requests = len(filtered_history)
        total_cost = sum(entry.get("cost", {}).get("totalCost", 0) for entry in filtered_history)
        
        # Cost by endpoint
        cost_by_endpoint = {}
        for entry in filtered_history:
            endpoint = entry.get("endpoint", "unknown")
            cost = entry.get("cost", {}).get("totalCost", 0)
            cost_by_endpoint[endpoint] = cost_by_endpoint.get(endpoint, 0) + cost
        
        # Cost by data type
        cost_by_data_type = {}
        for entry in filtered_history:
            params = entry.get("requestParams", {})
            data_type = params.get("dataType", "unknown")
            cost = entry.get("cost", {}).get("totalCost", 0)
            cost_by_data_type[data_type] = cost_by_data_type.get(data_type, 0) + cost
        
        # Estimate total data volume
        data_volume_gb = sum(entry.get("dataSizeMb", 1) for entry in filtered_history) / 1024
        
        return UsageSummary(
            period_start=start_date,
            period_end=end_date,
            total_requests=total_requests,
            total_cost=round(total_cost, 2),
            cost_by_endpoint=cost_by_endpoint,
            cost_by_data_type=cost_by_data_type,
            data_volume_gb=round(data_volume_gb, 3)
        )
    
    def check_usage_limits(self, 
                          user_tier: CostTier, 
                          current_month_requests: int,
                          current_month_data_mb: float) -> Dict[str, Any]:
        """Check if user has exceeded usage limits"""
        
        pricing = self.pricing[user_tier]
        max_requests = pricing["max_requests_per_month"]
        max_data_mb = pricing["max_data_volume_mb"]
        
        result = {
            "withinLimits": True,
            "requestsUsed": current_month_requests,
            "requestsLimit": max_requests,
            "dataUsedMb": current_month_data_mb,
            "dataLimitMb": max_data_mb,
            "warnings": []
        }
        
        if max_requests > 0 and current_month_requests >= max_requests:
            result["withinLimits"] = False
            result["warnings"].append("Monthly request limit exceeded")
        
        if max_data_mb > 0 and current_month_data_mb >= max_data_mb:
            result["withinLimits"] = False
            result["warnings"].append("Monthly data volume limit exceeded")
        
        # Warning thresholds (80% of limit)
        if max_requests > 0 and current_month_requests >= max_requests * 0.8:
            result["warnings"].append("Approaching monthly request limit")
        
        if max_data_mb > 0 and current_month_data_mb >= max_data_mb * 0.8:
            result["warnings"].append("Approaching monthly data volume limit")
        
        return result


# Global cost tracker instance
cost_tracker = CostTracker()