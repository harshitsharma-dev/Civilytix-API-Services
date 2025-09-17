# app/middleware/usage_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import json
from typing import Dict, Any
import logging

from ..services.usage_tracker import usage_tracker, CostTier
from ..services.cost_tracker import CostTier as CostTierEnum


logger = logging.getLogger(__name__)


class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track API usage for each request"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = {
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/health", "/metrics", "/usage"  # Exclude monitoring endpoints
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip tracking for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract request information
        method = request.method
        endpoint = request.url.path
        query_params = dict(request.query_params)
        
        # Get user information (from headers or query params)
        user_id = self._extract_user_id(request)
        user_tier = self._extract_user_tier(request)
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Try to get request body for POST/PUT requests
        request_params = await self._extract_request_params(request)
        request_params.update(query_params)
        
        # Call the actual endpoint
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Estimate data volume (simplified)
        data_volume_mb = self._estimate_data_volume(request_params, response)
        
        # Track the usage instance
        try:
            usage_instance = usage_tracker.track_request(
                endpoint=endpoint,
                method=method,
                user_tier=user_tier,
                request_params=request_params,
                response_status=response.status_code,
                processing_time_ms=processing_time,
                data_volume_mb=data_volume_mb,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Add usage tracking headers to response
            response.headers["X-Request-ID"] = usage_instance.request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
            response.headers["X-Cost"] = f"${usage_instance.cost_calculation.total_cost:.6f}"
            
        except Exception as e:
            logger.error(f"Error tracking usage for {endpoint}: {str(e)}")
        
        return response
    
    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from request"""
        # Check headers first
        user_id = request.headers.get("x-user-id")
        if user_id:
            return user_id
        
        # Check query parameters
        user_id = request.query_params.get("user_id")
        if user_id:
            return user_id
        
        # Default to anonymous
        return "anonymous"
    
    def _extract_user_tier(self, request: Request) -> CostTier:
        """Extract user tier from request"""
        # Check headers
        tier_header = request.headers.get("x-user-tier", "").upper()
        if tier_header:
            try:
                return CostTier(tier_header.lower())
            except ValueError:
                pass
        
        # Check query parameters
        tier_param = request.query_params.get("user_tier", "").upper()
        if tier_param:
            try:
                return CostTier(tier_param.lower())
            except ValueError:
                pass
        
        # Default to FREE tier
        return CostTier.FREE
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (for load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    async def _extract_request_params(self, request: Request) -> Dict[str, Any]:
        """Extract request parameters from body"""
        request_params = {}
        
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Clone the request body to avoid consuming it
                body = await request.body()
                if body:
                    try:
                        # Try to parse as JSON
                        request_params = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # If not JSON, store as raw data indicator
                        request_params = {"_raw_data_size": len(body)}
            except Exception as e:
                logger.warning(f"Could not extract request params: {str(e)}")
        
        return request_params
    
    def _estimate_data_volume(self, request_params: Dict[str, Any], response: Response) -> float:
        """Estimate data volume in MB"""
        
        # Base estimation
        data_volume = 0.01  # 10KB base
        
        # Add based on request parameters
        if "radius" in request_params:
            radius = float(request_params.get("radius", 1))
            # Larger radius = more data
            data_volume += (radius / 10) * 0.1  # 0.1MB per 10km radius
        
        if "waypoints" in request_params:
            waypoints = request_params.get("waypoints", [])
            if isinstance(waypoints, list):
                # More waypoints = more data
                data_volume += len(waypoints) * 0.05  # 50KB per waypoint
        
        # Consider response status
        if hasattr(response, "status_code"):
            if response.status_code >= 400:
                data_volume *= 0.1  # Error responses are smaller
        
        return max(data_volume, 0.001)  # Minimum 1KB


class UsageReportingMiddleware(BaseHTTPMiddleware):
    """Middleware for periodic usage reporting and cleanup"""
    
    def __init__(self, app: ASGIApp, report_interval: int = 3600):  # 1 hour
        super().__init__(app)
        self.report_interval = report_interval
        self.last_report = time.time()
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        # Process the request normally
        response = await call_next(request)
        
        # Check if it's time for periodic tasks
        current_time = time.time()
        
        # Periodic reporting
        if current_time - self.last_report > self.report_interval:
            await self._generate_usage_report()
            self.last_report = current_time
        
        # Periodic cleanup (daily)
        if current_time - self.last_cleanup > 86400:  # 24 hours
            await self._cleanup_old_data()
            self.last_cleanup = current_time
        
        return response
    
    async def _generate_usage_report(self):
        """Generate periodic usage report"""
        try:
            metrics = usage_tracker.get_real_time_metrics(force_refresh=True)
            logger.info(f"Usage Report: {metrics.total_requests} requests, "
                       f"${metrics.cost_per_hour:.4f}/hour, "
                       f"{metrics.requests_per_minute:.1f} req/min")
        except Exception as e:
            logger.error(f"Error generating usage report: {str(e)}")
    
    async def _cleanup_old_data(self):
        """Clean up old usage data"""
        try:
            usage_tracker.clear_old_instances(hours=48)
            logger.info("Cleaned up old usage instances")
        except Exception as e:
            logger.error(f"Error cleaning up usage data: {str(e)}")