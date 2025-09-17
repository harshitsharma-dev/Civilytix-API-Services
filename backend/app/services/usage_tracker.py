# app/services/usage_tracker.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json
from collections import defaultdict, deque
import threading
import time

from .cost_tracker import CostTracker, CostTier, CostCalculation


@dataclass
class APIUsageInstance:
    """Represents a single API request usage instance"""
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
    ip_address: str
    user_agent: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestId": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "endpoint": self.endpoint,
            "method": self.method,
            "userId": self.user_id,
            "userTier": self.user_tier.value,
            "requestParams": self.request_params,
            "responseStatus": self.response_status,
            "processingTimeMs": self.processing_time_ms,
            "dataVolumeMb": self.data_volume_mb,
            "costCalculation": self.cost_calculation.to_dict(),
            "ipAddress": self.ip_address,
            "userAgent": self.user_agent
        }


@dataclass
class UsageMetrics:
    """Real-time usage metrics"""
    total_requests: int
    requests_per_minute: float
    average_response_time: float
    total_cost: float
    cost_per_hour: float
    most_used_endpoints: List[Dict[str, Any]]
    user_tier_distribution: Dict[str, int]
    error_rate: float
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalRequests": self.total_requests,
            "requestsPerMinute": self.requests_per_minute,
            "averageResponseTime": self.average_response_time,
            "totalCost": self.total_cost,
            "costPerHour": self.cost_per_hour,
            "mostUsedEndpoints": self.most_used_endpoints,
            "userTierDistribution": self.user_tier_distribution,
            "errorRate": self.error_rate,
            "lastUpdated": self.last_updated.isoformat()
        }


class UsageTracker:
    """Service for tracking API usage instances and generating real-time metrics"""
    
    def __init__(self, max_instances: int = 10000):
        self.max_instances = max_instances
        self.usage_instances: deque = deque(maxlen=max_instances)
        self.cost_tracker = CostTracker()
        self.lock = threading.Lock()
        
        # Real-time metrics tracking
        self.metrics_cache = None
        self.last_metrics_update = None
        self.metrics_cache_duration = 10  # seconds
        
        # Performance tracking
        self.endpoint_stats = defaultdict(list)
        self.user_tier_stats = defaultdict(int)
        self.error_counts = defaultdict(int)
        
    def track_request(self, 
                     endpoint: str,
                     method: str,
                     user_tier: CostTier,
                     request_params: Dict[str, Any],
                     response_status: int,
                     processing_time_ms: float,
                     data_volume_mb: float = 0.1,
                     user_id: Optional[str] = None,
                     ip_address: str = "unknown",
                     user_agent: str = "unknown") -> APIUsageInstance:
        """Track a single API request instance"""
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Calculate cost for this specific request
        cost_calculation = self._calculate_request_cost(
            endpoint, request_params, user_tier, data_volume_mb
        )
        
        # Create usage instance
        instance = APIUsageInstance(
            request_id=request_id,
            timestamp=datetime.now(),
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            user_tier=user_tier,
            request_params=request_params,
            response_status=response_status,
            processing_time_ms=processing_time_ms,
            data_volume_mb=data_volume_mb,
            cost_calculation=cost_calculation,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store instance with thread safety
        with self.lock:
            self.usage_instances.append(instance)
            self._update_internal_stats(instance)
        
        return instance
    
    def _calculate_request_cost(self, endpoint: str, params: Dict[str, Any], 
                               user_tier: CostTier, data_volume_mb: float) -> CostCalculation:
        """Calculate cost for a specific request"""
        
        # Determine operation type based on endpoint
        if "region" in endpoint:
            if "center_lat" in params and "center_lon" in params:
                return self.cost_tracker.calculate_region_cost(
                    user_tier=user_tier,
                    center_lat=params.get("center_lat", 0),
                    center_lon=params.get("center_lon", 0),
                    radius_km=params.get("radius", 1),
                    data_type=params.get("data_type", "default")
                )
        elif "path" in endpoint:
            waypoints = params.get("waypoints", [])
            if waypoints:
                return self.cost_tracker.calculate_path_cost(
                    user_tier=user_tier,
                    waypoints=waypoints,
                    data_type=params.get("data_type", "default")
                )
        
        # Default request cost calculation
        return self.cost_tracker.calculate_request_cost(
            user_tier=user_tier,
            data_type="default",
            estimated_size_mb=data_volume_mb,
            region_type="local",
            priority="normal"
        )
    
    def _update_internal_stats(self, instance: APIUsageInstance):
        """Update internal statistics (called within lock)"""
        # Update endpoint stats
        self.endpoint_stats[instance.endpoint].append({
            "timestamp": instance.timestamp,
            "processing_time": instance.processing_time_ms,
            "cost": instance.cost_calculation.total_cost
        })
        
        # Update user tier stats
        self.user_tier_stats[instance.user_tier.value] += 1
        
        # Update error stats
        if instance.response_status >= 400:
            self.error_counts[instance.endpoint] += 1
    
    def get_usage_instances(self, 
                           limit: int = 100,
                           endpoint_filter: Optional[str] = None,
                           user_tier_filter: Optional[CostTier] = None,
                           time_range_minutes: Optional[int] = None) -> List[APIUsageInstance]:
        """Get usage instances with optional filters"""
        
        with self.lock:
            instances = list(self.usage_instances)
        
        # Apply filters
        if time_range_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
            instances = [i for i in instances if i.timestamp >= cutoff_time]
        
        if endpoint_filter:
            instances = [i for i in instances if endpoint_filter in i.endpoint]
        
        if user_tier_filter:
            instances = [i for i in instances if i.user_tier == user_tier_filter]
        
        # Sort by timestamp (newest first) and limit
        instances.sort(key=lambda x: x.timestamp, reverse=True)
        return instances[:limit]
    
    def get_real_time_metrics(self, force_refresh: bool = False) -> UsageMetrics:
        """Get real-time usage metrics with caching"""
        
        now = datetime.now()
        
        # Check cache validity
        if (not force_refresh and 
            self.metrics_cache and 
            self.last_metrics_update and
            (now - self.last_metrics_update).total_seconds() < self.metrics_cache_duration):
            return self.metrics_cache
        
        # Calculate fresh metrics
        with self.lock:
            instances = list(self.usage_instances)
        
        if not instances:
            return UsageMetrics(
                total_requests=0,
                requests_per_minute=0.0,
                average_response_time=0.0,
                total_cost=0.0,
                cost_per_hour=0.0,
                most_used_endpoints=[],
                user_tier_distribution={},
                error_rate=0.0,
                last_updated=now
            )
        
        # Calculate metrics for last hour
        one_hour_ago = now - timedelta(hours=1)
        recent_instances = [i for i in instances if i.timestamp >= one_hour_ago]
        
        # Calculate request rate
        one_minute_ago = now - timedelta(minutes=1)
        recent_minute_instances = [i for i in instances if i.timestamp >= one_minute_ago]
        requests_per_minute = len(recent_minute_instances)
        
        # Calculate average response time
        if recent_instances:
            avg_response_time = sum(i.processing_time_ms for i in recent_instances) / len(recent_instances)
        else:
            avg_response_time = 0.0
        
        # Calculate costs
        total_cost = sum(i.cost_calculation.total_cost for i in instances)
        hourly_cost = sum(i.cost_calculation.total_cost for i in recent_instances)
        
        # Calculate most used endpoints
        endpoint_counts = defaultdict(int)
        for instance in recent_instances:
            endpoint_counts[instance.endpoint] += 1
        
        most_used = sorted(
            [{"endpoint": k, "count": v} for k, v in endpoint_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]
        
        # Calculate user tier distribution
        tier_counts = defaultdict(int)
        for instance in recent_instances:
            tier_counts[instance.user_tier.value] += 1
        
        # Calculate error rate
        error_count = sum(1 for i in recent_instances if i.response_status >= 400)
        error_rate = (error_count / len(recent_instances)) * 100 if recent_instances else 0.0
        
        # Create metrics object
        metrics = UsageMetrics(
            total_requests=len(instances),
            requests_per_minute=requests_per_minute,
            average_response_time=avg_response_time,
            total_cost=total_cost,
            cost_per_hour=hourly_cost,
            most_used_endpoints=most_used,
            user_tier_distribution=dict(tier_counts),
            error_rate=error_rate,
            last_updated=now
        )
        
        # Cache the results
        self.metrics_cache = metrics
        self.last_metrics_update = now
        
        return metrics
    
    def get_usage_by_endpoint(self, endpoint: str, hours: int = 24) -> Dict[str, Any]:
        """Get detailed usage statistics for a specific endpoint"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            endpoint_instances = [
                i for i in self.usage_instances 
                if i.endpoint == endpoint and i.timestamp >= cutoff_time
            ]
        
        if not endpoint_instances:
            return {
                "endpoint": endpoint,
                "totalRequests": 0,
                "averageResponseTime": 0.0,
                "totalCost": 0.0,
                "errorRate": 0.0,
                "requestsByHour": [],
                "costByHour": []
            }
        
        # Calculate hourly breakdown
        hourly_requests = defaultdict(int)
        hourly_costs = defaultdict(float)
        
        for instance in endpoint_instances:
            hour_key = instance.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_requests[hour_key] += 1
            hourly_costs[hour_key] += instance.cost_calculation.total_cost
        
        # Sort by hour
        sorted_hours = sorted(hourly_requests.keys())
        requests_by_hour = [{"hour": h.isoformat(), "requests": hourly_requests[h]} for h in sorted_hours]
        costs_by_hour = [{"hour": h.isoformat(), "cost": hourly_costs[h]} for h in sorted_hours]
        
        # Calculate summary stats
        total_requests = len(endpoint_instances)
        avg_response_time = sum(i.processing_time_ms for i in endpoint_instances) / total_requests
        total_cost = sum(i.cost_calculation.total_cost for i in endpoint_instances)
        error_count = sum(1 for i in endpoint_instances if i.response_status >= 400)
        error_rate = (error_count / total_requests) * 100
        
        return {
            "endpoint": endpoint,
            "totalRequests": total_requests,
            "averageResponseTime": avg_response_time,
            "totalCost": total_cost,
            "errorRate": error_rate,
            "requestsByHour": requests_by_hour,
            "costByHour": costs_by_hour
        }
    
    def get_user_usage_summary(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get usage summary for a specific user"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            user_instances = [
                i for i in self.usage_instances 
                if i.user_id == user_id and i.timestamp >= cutoff_time
            ]
        
        if not user_instances:
            return {
                "userId": user_id,
                "totalRequests": 0,
                "totalCost": 0.0,
                "averageResponseTime": 0.0,
                "endpointsUsed": [],
                "requestsByHour": []
            }
        
        # Calculate summary
        total_requests = len(user_instances)
        total_cost = sum(i.cost_calculation.total_cost for i in user_instances)
        avg_response_time = sum(i.processing_time_ms for i in user_instances) / total_requests
        
        # Endpoints used
        endpoint_counts = defaultdict(int)
        for instance in user_instances:
            endpoint_counts[instance.endpoint] += 1
        
        endpoints_used = [{"endpoint": k, "count": v} for k, v in endpoint_counts.items()]
        endpoints_used.sort(key=lambda x: x["count"], reverse=True)
        
        # Hourly breakdown
        hourly_requests = defaultdict(int)
        for instance in user_instances:
            hour_key = instance.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_requests[hour_key] += 1
        
        requests_by_hour = [
            {"hour": h.isoformat(), "requests": hourly_requests[h]} 
            for h in sorted(hourly_requests.keys())
        ]
        
        return {
            "userId": user_id,
            "totalRequests": total_requests,
            "totalCost": total_cost,
            "averageResponseTime": avg_response_time,
            "endpointsUsed": endpoints_used,
            "requestsByHour": requests_by_hour
        }
    
    def clear_old_instances(self, hours: int = 48):
        """Clear usage instances older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            # Convert to list, filter, and convert back to deque
            current_instances = list(self.usage_instances)
            recent_instances = [i for i in current_instances if i.timestamp >= cutoff_time]
            
            self.usage_instances.clear()
            self.usage_instances.extend(recent_instances)


# Global usage tracker instance
usage_tracker = UsageTracker()