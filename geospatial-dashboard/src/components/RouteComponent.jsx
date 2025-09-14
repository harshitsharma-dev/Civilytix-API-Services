// src/components/RouteComponent.jsx
import React, { useEffect, useState } from "react";
import { Polyline, Marker, Popup } from "react-leaflet";
import { fetchDirections } from "../utils/googleMaps";

const RouteComponent = ({ pathPoints }) => {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (pathPoints.length === 2) {
      fetchRoute();
    } else {
      setRouteData(null);
    }
  }, [pathPoints]);

  const fetchRoute = async () => {
    setLoading(true);
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

    try {
      // Add timeout for the entire routing operation
      const directions = await Promise.race([
        fetchDirections(pathPoints[0], pathPoints[1], apiKey),
        new Promise((_, reject) =>
          setTimeout(
            () => reject(new Error("Route calculation timeout")),
            15000
          )
        ),
      ]);

      setRouteData(directions);
    } catch (error) {
      console.error("Error fetching route:", error);
      setRouteData(null);
    } finally {
      setLoading(false);
    }
  };

  if (pathPoints.length !== 2) return null;

  return (
    <>
      {/* Start and End markers */}
      <Marker position={[pathPoints[0].lat, pathPoints[0].lng]}>
        <Popup>
          <div className="text-sm">
            <strong>Start Point</strong>
            <br />
            Lat: {pathPoints[0].lat.toFixed(4)}
            <br />
            Lng: {pathPoints[0].lng.toFixed(4)}
          </div>
        </Popup>
      </Marker>

      <Marker position={[pathPoints[1].lat, pathPoints[1].lng]}>
        <Popup>
          <div className="text-sm">
            <strong>End Point</strong>
            <br />
            Lat: {pathPoints[1].lat.toFixed(4)}
            <br />
            Lng: {pathPoints[1].lng.toFixed(4)}
            {routeData && (
              <>
                <br />
                <br />
                <strong>Route Info:</strong>
                <br />
                Distance: {routeData.distance}
                <br />
                Duration: {routeData.duration}
              </>
            )}
          </div>
        </Popup>
      </Marker>

      {/* Route polyline */}
      {routeData && routeData.path ? (
        <Polyline
          positions={routeData.path}
          color="#2563eb"
          weight={4}
          opacity={0.8}
          dashArray="10, 10"
        />
      ) : (
        // Fallback to straight line if no route data
        <Polyline
          positions={pathPoints}
          color="#dc2626"
          weight={3}
          opacity={0.7}
          dashArray="5, 5"
        />
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-background border border-border px-3 py-2 rounded-lg shadow-lg z-[1002]">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
            <span className="text-sm text-foreground">
              Calculating route...
            </span>
          </div>
        </div>
      )}
    </>
  );
};

export default RouteComponent;
