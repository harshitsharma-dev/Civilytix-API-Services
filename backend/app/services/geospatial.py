import math
import json
from typing import Dict, List, Any, Optional
from shapely.geometry import Point, LineString
from pathlib import Path
from pymongo import MongoClient
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

from app.core.config import settings

# Load environment variables
load_dotenv()


class GeospatialService:
    """Service for handling geospatial data operations."""
    
    def __init__(self):
        self.potholes_data: Optional[Dict] = None
        self.uhi_data: Optional[Dict] = None
        self.mongo_client: Optional[MongoClient] = None
        self.db = None
        self.potholes_collection = None
        self._setup_mongodb()
    
    def _setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            # Get MongoDB credentials from environment
            username = os.getenv('MONGO_USERNAME', 'Manav')
            password = os.getenv('MONGO_PASSWORD', 'Ommanav@2005')
            cluster_address = os.getenv('MONGO_CLUSTER_ADDRESS', 'civilytix-cluster.uqq26ak.mongodb.net')
            database_name = os.getenv('MONGO_DATABASE_NAME', 'civilytix_db')
            
            # Encode password for URL
            encoded_password = quote_plus(password)
            
            # Create MongoDB URI
            mongodb_uri = f"mongodb+srv://{username}:{encoded_password}@{cluster_address}/{database_name}?retryWrites=true&w=majority"
            
            # Connect to MongoDB with a shorter timeout for faster failure detection
            self.mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            self.mongo_client.admin.command('ping')
            
            self.db = self.mongo_client[database_name]
            self.potholes_collection = self.db['potholes']
            
            print(f"Connected to MongoDB: {cluster_address}")
            
        except Exception as e:
            print(f"MongoDB connection failed, using mock data: {e}")
            self.mongo_client = None
            self.db = None
            self.potholes_collection = None
    
    def __del__(self):
        """Close MongoDB connection when service is destroyed"""
        if self.mongo_client:
            self.mongo_client.close()
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points on Earth using the Haversine formula.
        
        Args:
            lat1, lon1: Latitude and longitude of first point
            lat2, lon2: Latitude and longitude of second point
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Radius of Earth in kilometers

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = (math.sin(dlat / 2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance
    
    def filter_potholes_by_region(self, center_lat: float, center_lon: float, 
                                 radius_km: float) -> Dict[str, Any]:
        """
        Filter potholes within a circular region using MongoDB geospatial queries.
        
        Args:
            center_lat: Latitude of center point
            center_lon: Longitude of center point
            radius_km: Radius in kilometers
            
        Returns:
            Dict: GeoJSON FeatureCollection with filtered potholes
        """
        if not self.mongo_client or self.potholes_collection is None:
            print("MongoDB connection not available, returning mock data")
            return self._get_mock_potholes_data()
        
        try:
            # Convert radius from km to meters for MongoDB query
            radius_meters = radius_km * 1000
            
            # MongoDB geospatial query using $geoWithin and $centerSphere
            query = {
                "coordinates": {
                    "$geoWithin": {
                        "$centerSphere": [[center_lon, center_lat], radius_km / 6378.1]  # radius in radians
                    }
                },
                "status": "active"
            }
            
            # Execute query
            cursor = self.potholes_collection.find(query)
            
            # Convert MongoDB documents to GeoJSON features
            features = []
            for doc in cursor:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "id": doc.get('id'),
                        "severity": doc.get('severity'),
                        "confidence": doc.get('confidence'),
                        "city": doc.get('city'),
                        "area": doc.get('area'),
                        "timestamp": doc.get('timestamp')
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": doc.get('coordinates', {}).get('coordinates', [])
                    }
                }
                features.append(feature)
            
            print(f"Found {len(features)} potholes in region ({center_lat}, {center_lon}) with radius {radius_km}km")
            
            return {
                "type": "FeatureCollection",
                "features": features
            }
            
        except Exception as e:
            print(f"Error querying potholes by region: {e}")
            return {"type": "FeatureCollection", "features": []}
    
    def filter_potholes_by_path(self, start_lat: float, start_lon: float,
                               end_lat: float, end_lon: float, 
                               buffer_meters: float) -> Dict[str, Any]:
        """
        Filter potholes within a buffer around a path using MongoDB geospatial queries.
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            buffer_meters: Buffer distance in meters
            
        Returns:
            Dict: GeoJSON FeatureCollection with filtered potholes
        """
        if not self.mongo_client or self.potholes_collection is None:
            print("MongoDB connection not available, returning mock data")
            return self._get_mock_potholes_data()
        
        try:
            # Create a line geometry and buffer it
            start_point = Point(start_lon, start_lat)
            end_point = Point(end_lon, end_lat)
            path_line = LineString([start_point, end_point])
            
            # Convert meters to degrees (rough approximation)
            buffer_degrees = buffer_meters / 111320.0
            path_buffer = path_line.buffer(buffer_degrees)
            
            # Get all potholes and filter using Shapely (MongoDB doesn't have direct line buffer queries)
            all_potholes = self.potholes_collection.find({"status": "active"})
            
            features = []
            for doc in all_potholes:
                coords = doc.get('coordinates', {}).get('coordinates', [])
                if len(coords) >= 2:
                    pothole_point = Point(coords[0], coords[1])  # [lon, lat]
                    
                    if path_buffer.contains(pothole_point):
                        feature = {
                            "type": "Feature",
                            "properties": {
                                "id": doc.get('id'),
                                "severity": doc.get('severity'),
                                "confidence": doc.get('confidence'),
                                "city": doc.get('city'),
                                "area": doc.get('area'),
                                "timestamp": doc.get('timestamp')
                            },
                            "geometry": {
                                "type": "Point",
                                "coordinates": coords
                            }
                        }
                        features.append(feature)
            
            print(f"Found {len(features)} potholes along path with {buffer_meters}m buffer")
            
            return {
                "type": "FeatureCollection",
                "features": features
            }
            
        except Exception as e:
            print(f"Error querying potholes by path: {e}")
            return {"type": "FeatureCollection", "features": []}
    
    def process_uhi_data_by_region(self, center_lat: float, center_lon: float,
                                  radius_km: float) -> Dict[str, Any]:
        """
        Process UHI (Urban Heat Island) data for a region.
        
        Args:
            center_lat: Latitude of center point
            center_lon: Longitude of center point
            radius_km: Radius in kilometers
            
        Returns:
            Dict: Processed UHI data (placeholder implementation)
        """
        # Placeholder implementation - replace with actual UHI processing
        return {
            "message": f"Placeholder for UHI data retrieval in region {center_lat},{center_lon} with radius {radius_km} km",
            "dataType": "uhi",
            "region": {
                "center": {"lat": center_lat, "lon": center_lon},
                "radius_km": radius_km
            }
        }
    
    def process_uhi_data_by_path(self, start_lat: float, start_lon: float,
                                end_lat: float, end_lon: float,
                                buffer_meters: float) -> Dict[str, Any]:
        """
        Process UHI data along a path.
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            buffer_meters: Buffer distance in meters
            
        Returns:
            Dict: Processed UHI data (placeholder implementation)
        """
        # Placeholder implementation - replace with actual UHI processing
        return {
            "message": f"Placeholder for UHI data retrieval along path from {start_lat},{start_lon} to {end_lat},{end_lon} with buffer {buffer_meters} meters",
            "dataType": "uhi",
            "path": {
                "start": {"lat": start_lat, "lon": start_lon},
                "end": {"lat": end_lat, "lon": end_lon},
                "buffer_meters": buffer_meters
            }
        }
    
    def get_data_by_region(self, center_lat: float, center_lon: float,
                          radius_km: float, data_type: str) -> Dict[str, Any]:
        """
        Get geospatial data for a region based on data type.
        
        Args:
            center_lat: Latitude of center point
            center_lon: Longitude of center point
            radius_km: Radius in kilometers
            data_type: Type of data ("potholes" or "uhi")
            
        Returns:
            Dict: Processed geospatial data
        """
        if data_type == "potholes":
            return self.filter_potholes_by_region(center_lat, center_lon, radius_km)
        elif data_type == "uhi":
            return self.process_uhi_data_by_region(center_lat, center_lon, radius_km)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def get_data_by_path(self, start_lat: float, start_lon: float,
                        end_lat: float, end_lon: float,
                        buffer_meters: float, data_type: str) -> Dict[str, Any]:
        """
        Get geospatial data for a path based on data type.
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            buffer_meters: Buffer distance in meters
            data_type: Type of data ("potholes" or "uhi")
            
        Returns:
            Dict: Processed geospatial data
        """
        if data_type == "potholes":
            return self.filter_potholes_by_path(
                start_lat, start_lon, end_lat, end_lon, buffer_meters
            )
        elif data_type == "uhi":
            return self.process_uhi_data_by_path(
                start_lat, start_lon, end_lat, end_lon, buffer_meters
            )
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _get_mock_potholes_data(self) -> Dict[str, Any]:
        """
        Return mock pothole data when MongoDB is not available.
        
        Returns:
            Dict: Mock GeoJSON FeatureCollection with sample potholes
        """
        mock_features = [
            {
                "type": "Feature",
                "properties": {
                    "id": 0,
                    "severity": 2,
                    "confidence": 0.85,
                    "city": "Delhi",
                    "area": "Connaught Place",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.209, 28.6139]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "id": 1,
                    "severity": 3,
                    "confidence": 0.92,
                    "city": "Mumbai", 
                    "area": "Marine Drive",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [72.8225, 18.9437]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "id": 2,
                    "severity": 1,
                    "confidence": 0.78,
                    "city": "Bangalore",
                    "area": "MG Road",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.6094, 12.9716]
                }
            }
        ]
        
        return {
            "type": "FeatureCollection",
            "features": mock_features
        }


# Global geospatial service instance
geo_service = GeospatialService()