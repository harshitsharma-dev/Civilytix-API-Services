import os
from typing import Optional
from urllib.parse import quote_plus


class Settings:
    """Application settings and configuration."""
    
    # MongoDB Configuration
    MONGO_USERNAME: str = os.getenv("MONGO_USERNAME", "uname")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD", "pwd")
    MONGO_CLUSTER_ADDRESS: str = os.getenv("MONGO_CLUSTER_ADDRESS", "cluster0.gv45ccj.mongodb.net")
    MONGO_DATABASE_NAME: str = os.getenv("MONGO_DATABASE_NAME", "civilytix_db")
    MONGO_APP_NAME: str = os.getenv("MONGO_APP_NAME", "Cluster0")
    
    @property
    def MONGO_URI(self) -> str:
        """Generate MongoDB connection URI."""
        username = quote_plus(self.MONGO_USERNAME)
        password = quote_plus(self.MONGO_PASSWORD)
        return f"mongodb+srv://{username}:{password}@{self.MONGO_CLUSTER_ADDRESS}/{self.MONGO_DATABASE_NAME}?retryWrites=true&w=majority&appName={self.MONGO_APP_NAME}"
    
    # Google Cloud Storage Configuration
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "civilytix-data-bucket")
    GCS_PROJECT_ID: Optional[str] = os.getenv("GCS_PROJECT_ID")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Civilytix API Services"
    PROJECT_VERSION: str = "1.0.0"
    
    # Security
    VALID_API_KEYS: list = [
        "user1_secret_token",
        "user2_another_token", 
        "user3_paid_token"
    ]
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Data Configuration
    POTHOLES_DATA_PATH: str = os.getenv("POTHOLES_DATA_PATH", "data/global_potholes.geojson")
    
    class Config:
        case_sensitive = True


# Global settings instance
settings = Settings()