from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.services.database import db_service
from app.services.geospatial import geo_service
from app.services.storage import storage_service
from app.routes.data_routes import router as data_router
from app.routes.user_routes import router as user_router
from app.routes.usage_routes import router as usage_router
from app.middleware.usage_middleware import UsageTrackingMiddleware, UsageReportingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application."""
    # Startup
    print("Starting Civilytix API Services...")
    
    # Initialize database connection
    try:
        db_service.connect()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
    
    # Load geospatial data
    try:
        geo_service.load_potholes_data()
    except Exception as e:
        print(f"Failed to load potholes data: {e}")
    
    # Initialize cloud storage
    try:
        storage_service.initialize()
    except Exception as e:
        print(f"Failed to initialize cloud storage: {e}")
    
    print("Civilytix API Services started successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down Civilytix API Services...")
    try:
        db_service.disconnect()
    except Exception as e:
        print(f"Error during database disconnect: {e}")
    
    print("Civilytix API Services shut down successfully!")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API for geospatial data retrieval and analysis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add usage tracking middleware
app.add_middleware(UsageTrackingMiddleware)
app.add_middleware(UsageReportingMiddleware)

# Include routers
app.include_router(data_router, prefix=settings.API_V1_STR)
app.include_router(user_router, prefix=settings.API_V1_STR)
app.include_router(usage_router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Civilytix API Services",
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check database connection
    try:
        # Simple ping to check if database is responsive
        if db_service.client:
            db_service.client.admin.command('ping')
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "not_connected"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
    
    # Check if geospatial data is loaded
    health_status["services"]["geospatial_data"] = (
        "loaded" if geo_service.potholes_data else "not_loaded"
    )
    
    # Check cloud storage
    try:
        if storage_service.client and storage_service.bucket:
            health_status["services"]["cloud_storage"] = "healthy"
        else:
            health_status["services"]["cloud_storage"] = "not_initialized"
    except Exception as e:
        health_status["services"]["cloud_storage"] = f"unhealthy: {str(e)}"
    
    # Determine overall health
    unhealthy_services = [
        service for service, status in health_status["services"].items() 
        if "unhealthy" in status or "not_" in status
    ]
    
    if unhealthy_services:
        health_status["status"] = "degraded"
        health_status["issues"] = unhealthy_services
    
    return health_status


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return HTTPException(
        status_code=404,
        detail={
            "status": "error",
            "message": "The requested endpoint was not found.",
            "available_endpoints": {
                "docs": "/docs",
                "health": "/health",
                "data_region": f"{settings.API_V1_STR}/data/region",
                "data_path": f"{settings.API_V1_STR}/data/path",
                "user_history": f"{settings.API_V1_STR}/user/history"
            }
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )