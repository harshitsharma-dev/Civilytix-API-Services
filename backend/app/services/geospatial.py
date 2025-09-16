import math
import json
from typing import Dict, List, Any, Optional
from shapely.geometry import Point, LineString
from pathlib import Path

from app.core.config import settings


class GeospatialService:
    """Service for handling geospatial data operations."""
    
    def __init__(self):
        self.potholes_data: Optional[Dict] = None
        self.uhi_data: Optional[Dict] = None
    
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
    
    def load_potholes_data(self, file_path: Optional[str] = None) -> bool:
        """
        Load potholes data from GeoJSON file.
        
        Args:
            file_path: Optional path to potholes data file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = file_path or settings.POTHOLES_DATA_PATH
            if not Path(path).exists():
                print(f"Potholes data file not found at: {path}")
                return False
                
            with open(path, 'r') as f:
                self.potholes_data = json.load(f)
            
            print(f"Successfully loaded potholes data from {path}")
            return True
        except Exception as e:
            print(f"Error loading potholes data: {e}")
            return False
    
    def filter_potholes_by_region(self, center_lat: float, center_lon: float, 
                                 radius_km: float) -> Dict[str, Any]:
        """
        Filter potholes within a circular region.
        
        Args:
            center_lat: Latitude of center point
            center_lon: Longitude of center point
            radius_km: Radius in kilometers
            
        Returns:
            Dict: GeoJSON FeatureCollection with filtered potholes
        """
        if not self.potholes_data or 'features' not in self.potholes_data:
            return {"type": "FeatureCollection", "features": []}
        
        filtered_features = []
        
        for feature in self.potholes_data['features']:
            if (feature.get('geometry') and 
                feature['geometry'].get('type') == 'Point'):
                
                coords = feature['geometry'].get('coordinates')
                if coords and len(coords) >= 2:
                    # GeoJSON coordinates are [longitude, latitude]
                    pothole_lon = coords[0]
                    pothole_lat = coords[1]
                    
                    distance = self.haversine_distance(
                        center_lat, center_lon, pothole_lat, pothole_lon
                    )
                    
                    if distance <= radius_km:
                        filtered_features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": filtered_features
        }
    
    def filter_potholes_by_path(self, start_lat: float, start_lon: float,
                               end_lat: float, end_lon: float, 
                               buffer_meters: float) -> Dict[str, Any]:
        """
        Filter potholes within a buffer around a path.
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            buffer_meters: Buffer distance in meters
            
        Returns:
            Dict: GeoJSON FeatureCollection with filtered potholes
        """
        if not self.potholes_data or 'features' not in self.potholes_data:
            return {"type": "FeatureCollection", "features": []}
        
        filtered_features = []
        
        # Create path line and buffer
        start_point = Point(start_lon, start_lat)
        end_point = Point(end_lon, end_lat)
        path_line = LineString([start_point, end_point])
        
        # Convert meters to degrees (rough approximation)
        # 1 degree ≈ 111,320 meters at the equator
        buffer_degrees = buffer_meters / 111320.0
        path_buffer = path_line.buffer(buffer_degrees)
        
        for feature in self.potholes_data['features']:
            if (feature.get('geometry') and 
                feature['geometry'].get('type') == 'Point'):
                
                coords = feature['geometry'].get('coordinates')
                if coords and len(coords) >= 2:
                    # GeoJSON coordinates are [longitude, latitude]
                    pothole_point = Point(coords[0], coords[1])
                    
                    if path_buffer.contains(pothole_point):
                        filtered_features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": filtered_features
        }
    
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


# Global geospatial service instance
geo_service = GeospatialService()