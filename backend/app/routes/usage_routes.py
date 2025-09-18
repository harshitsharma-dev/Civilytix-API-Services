# app/routes/usage_routes.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..services.usage_tracker import usage_tracker, CostTier
from ..models.schemas import UsageInstanceResponse, UsageMetricsResponse, EndpointUsageResponse


router = APIRouter(prefix="/api/v1/usage", tags=["usage"])


@router.get("/instances", response_model=List[Dict[str, Any]])
async def get_usage_instances(
    limit: int = Query(100, ge=1, le=1000, description="Number of instances to return"),
    endpoint_filter: Optional[str] = Query(None, description="Filter by endpoint path"),
    user_tier_filter: Optional[str] = Query(None, description="Filter by user tier"),
    time_range_minutes: Optional[int] = Query(None, ge=1, le=1440, description="Time range in minutes")
):
    """Get recent API usage instances with optional filters"""
    
    # Convert user tier filter
    tier_filter = None
    if user_tier_filter:
        try:
            tier_filter = CostTier(user_tier_filter.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid user tier: {user_tier_filter}"
            )
    
    instances = usage_tracker.get_usage_instances(
        limit=limit,
        endpoint_filter=endpoint_filter,
        user_tier_filter=tier_filter,
        time_range_minutes=time_range_minutes
    )
    
    return [instance.to_dict() for instance in instances]


@router.get("/metrics", response_model=Dict[str, Any])
async def get_real_time_metrics(
    force_refresh: bool = Query(False, description="Force refresh of cached metrics")
):
    """Get real-time usage metrics"""
    
    metrics = usage_tracker.get_real_time_metrics(force_refresh=force_refresh)
    return metrics.to_dict()


@router.get("/endpoint/{endpoint_name}", response_model=Dict[str, Any])
async def get_endpoint_usage(
    endpoint_name: str,
    hours: int = Query(24, ge=1, le=168, description="Time range in hours")
):
    """Get detailed usage statistics for a specific endpoint"""
    
    # Reconstruct the endpoint path
    endpoint_path = f"/api/v1/{endpoint_name}"
    
    usage_stats = usage_tracker.get_usage_by_endpoint(
        endpoint=endpoint_path,
        hours=hours
    )
    
    if usage_stats["totalRequests"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No usage data found for endpoint: {endpoint_path}"
        )
    
    return usage_stats


@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_usage(
    user_id: str,
    hours: int = Query(24, ge=1, le=168, description="Time range in hours")
):
    """Get usage summary for a specific user"""
    
    usage_summary = usage_tracker.get_user_usage_summary(
        user_id=user_id,
        hours=hours
    )
    
    if usage_summary["totalRequests"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No usage data found for user: {user_id}"
        )
    
    return usage_summary


@router.get("/trends/hourly", response_model=Dict[str, Any])
async def get_hourly_trends(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze")
):
    """Get hourly usage trends"""
    
    # Get all recent instances
    instances = usage_tracker.get_usage_instances(
        limit=10000,
        time_range_minutes=hours * 60
    )
    
    if not instances:
        return {
            "hoursAnalyzed": hours,
            "requestsByHour": [],
            "costByHour": [],
            "errorsByHour": [],
            "avgResponseTimeByHour": []
        }
    
    # Group by hour
    from collections import defaultdict
    hourly_data = defaultdict(lambda: {
        "requests": 0,
        "cost": 0.0,
        "errors": 0,
        "response_times": []
    })
    
    for instance in instances:
        hour_key = instance.timestamp.replace(minute=0, second=0, microsecond=0)
        hourly_data[hour_key]["requests"] += 1
        hourly_data[hour_key]["cost"] += instance.cost_calculation.total_cost
        hourly_data[hour_key]["response_times"].append(instance.processing_time_ms)
        
        if instance.response_status >= 400:
            hourly_data[hour_key]["errors"] += 1
    
    # Sort by hour and format response
    sorted_hours = sorted(hourly_data.keys())
    
    requests_by_hour = []
    costs_by_hour = []
    errors_by_hour = []
    response_times_by_hour = []
    
    for hour in sorted_hours:
        data = hourly_data[hour]
        hour_str = hour.isoformat()
        
        requests_by_hour.append({
            "hour": hour_str,
            "requests": data["requests"]
        })
        
        costs_by_hour.append({
            "hour": hour_str,
            "cost": data["cost"]
        })
        
        errors_by_hour.append({
            "hour": hour_str,
            "errors": data["errors"]
        })
        
        avg_response_time = (
            sum(data["response_times"]) / len(data["response_times"])
            if data["response_times"] else 0
        )
        response_times_by_hour.append({
            "hour": hour_str,
            "avgResponseTime": avg_response_time
        })
    
    return {
        "hoursAnalyzed": hours,
        "requestsByHour": requests_by_hour,
        "costByHour": costs_by_hour,
        "errorsByHour": errors_by_hour,
        "avgResponseTimeByHour": response_times_by_hour
    }


@router.get("/costs/breakdown", response_model=Dict[str, Any])
async def get_cost_breakdown(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    group_by: str = Query("endpoint", description="Group by: endpoint, user_tier, or hour")
):
    """Get detailed cost breakdown"""
    
    instances = usage_tracker.get_usage_instances(
        limit=10000,
        time_range_minutes=hours * 60
    )
    
    if not instances:
        return {
            "totalCost": 0.0,
            "requestCount": 0,
            "averageCostPerRequest": 0.0,
            "breakdown": []
        }
    
    # Calculate totals
    total_cost = sum(i.cost_calculation.total_cost for i in instances)
    request_count = len(instances)
    avg_cost_per_request = total_cost / request_count if request_count > 0 else 0
    
    # Group breakdown
    from collections import defaultdict
    breakdown_data = defaultdict(lambda: {"cost": 0.0, "requests": 0})
    
    for instance in instances:
        if group_by == "endpoint":
            key = instance.endpoint
        elif group_by == "user_tier":
            key = instance.user_tier.value
        elif group_by == "hour":
            key = instance.timestamp.strftime("%Y-%m-%d %H:00")
        else:
            key = "unknown"
        
        breakdown_data[key]["cost"] += instance.cost_calculation.total_cost
        breakdown_data[key]["requests"] += 1
    
    # Sort and format breakdown
    breakdown = []
    for key, data in breakdown_data.items():
        percentage = (data["cost"] / total_cost * 100) if total_cost > 0 else 0
        breakdown.append({
            group_by: key,
            "cost": data["cost"],
            "requests": data["requests"],
            "averageCostPerRequest": data["cost"] / data["requests"],
            "percentageOfTotal": percentage
        })
    
    # Sort by cost (highest first)
    breakdown.sort(key=lambda x: x["cost"], reverse=True)
    
    return {
        "totalCost": total_cost,
        "requestCount": request_count,
        "averageCostPerRequest": avg_cost_per_request,
        "groupBy": group_by,
        "hoursAnalyzed": hours,
        "breakdown": breakdown
    }


@router.get("/performance/slowest", response_model=List[Dict[str, Any]])
async def get_slowest_requests(
    limit: int = Query(10, ge=1, le=100, description="Number of slowest requests to return"),
    hours: int = Query(24, ge=1, le=168, description="Time range in hours")
):
    """Get the slowest API requests"""
    
    instances = usage_tracker.get_usage_instances(
        limit=10000,
        time_range_minutes=hours * 60
    )
    
    # Sort by processing time (slowest first)
    slowest_instances = sorted(
        instances,
        key=lambda x: x.processing_time_ms,
        reverse=True
    )[:limit]
    
    return [
        {
            "requestId": instance.request_id,
            "endpoint": instance.endpoint,
            "processingTimeMs": instance.processing_time_ms,
            "timestamp": instance.timestamp.isoformat(),
            "userTier": instance.user_tier.value,
            "responseStatus": instance.response_status,
            "cost": instance.cost_calculation.total_cost
        }
        for instance in slowest_instances
    ]


@router.get("/performance/errors", response_model=Dict[str, Any])
async def get_error_analysis(
    hours: int = Query(24, ge=1, le=168, description="Time range in hours")
):
    """Get error analysis and statistics"""
    
    instances = usage_tracker.get_usage_instances(
        limit=10000,
        time_range_minutes=hours * 60
    )
    
    if not instances:
        return {
            "totalRequests": 0,
            "errorCount": 0,
            "errorRate": 0.0,
            "errorsByEndpoint": [],
            "errorsByStatus": [],
            "recentErrors": []
        }
    
    # Calculate error statistics
    total_requests = len(instances)
    error_instances = [i for i in instances if i.response_status >= 400]
    error_count = len(error_instances)
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
    
    # Group errors by endpoint
    from collections import defaultdict
    errors_by_endpoint = defaultdict(int)
    errors_by_status = defaultdict(int)
    
    for instance in error_instances:
        errors_by_endpoint[instance.endpoint] += 1
        errors_by_status[instance.response_status] += 1
    
    # Format response
    endpoint_errors = [
        {"endpoint": k, "errorCount": v}
        for k, v in errors_by_endpoint.items()
    ]
    endpoint_errors.sort(key=lambda x: x["errorCount"], reverse=True)
    
    status_errors = [
        {"statusCode": k, "errorCount": v}
        for k, v in errors_by_status.items()
    ]
    status_errors.sort(key=lambda x: x["errorCount"], reverse=True)
    
    # Recent errors (last 10)
    recent_errors = sorted(error_instances, key=lambda x: x.timestamp, reverse=True)[:10]
    recent_error_details = [
        {
            "requestId": instance.request_id,
            "endpoint": instance.endpoint,
            "statusCode": instance.response_status,
            "timestamp": instance.timestamp.isoformat(),
            "userTier": instance.user_tier.value,
            "processingTimeMs": instance.processing_time_ms
        }
        for instance in recent_errors
    ]
    
    return {
        "totalRequests": total_requests,
        "errorCount": error_count,
        "errorRate": error_rate,
        "errorsByEndpoint": endpoint_errors,
        "errorsByStatus": status_errors,
        "recentErrors": recent_error_details
    }