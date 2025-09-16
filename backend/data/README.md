# Data Directory

This directory contains the geospatial data files used by the Civilytix API Services.

## Required Files

### global_potholes.geojson
- **Description**: GeoJSON file containing pothole location data
- **Format**: GeoJSON FeatureCollection with Point features
- **Source**: Place your potholes dataset here
- **Example structure**:
  ```json
  {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [longitude, latitude]
        },
        "properties": {
          "id": "pothole_id",
          "severity": "high",
          "timestamp": "2024-01-01T00:00:00Z"
        }
      }
    ]
  }
  ```

## Additional Data Files (Future)

- **uhi_data.tif**: Urban Heat Island raster data (TIFF format)
- **traffic_data.geojson**: Traffic-related geospatial data
- **infrastructure.geojson**: Infrastructure data points

## Notes

- Ensure files are properly formatted GeoJSON or valid raster formats
- Large files should be compressed when possible
- Update the `.env` file paths when adding new data sources
- Consider using absolute paths for production deployments