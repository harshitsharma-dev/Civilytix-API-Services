// src/components/MapComponent.jsx
import React from "react";
import {
  MapContainer,
  TileLayer,
  useMapEvents,
  Marker,
  Popup,
  Circle,
  GeoJSON,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import RouteComponent from "./RouteComponent";

// Import the leaflet fix
import "../utils/leafletFix.js";

// Map Click Handler Component
const MapClickHandler = ({ requestType, onRegionClick, onPathClick }) => {
  useMapEvents({
    click: (e) => {
      if (requestType === "region") {
        onRegionClick(e.latlng);
      } else if (requestType === "path") {
        onPathClick(e.latlng);
      }
    },
  });
  return null;
};

// UHI Overlay Component
const UHIOverlay = ({ data }) => {
  return (
    <>
      {data.map((point, index) => (
        <Circle
          key={index}
          center={[point.lat, point.lng]}
          radius={200}
          fillColor={
            point.intensity > 0.7
              ? "#ff4444"
              : point.intensity > 0.5
              ? "#ffaa44"
              : "#44ff44"
          }
          color={
            point.intensity > 0.7
              ? "#ff0000"
              : point.intensity > 0.5
              ? "#ff8800"
              : "#00ff00"
          }
          fillOpacity={0.6}
          opacity={0.8}
        >
          <Popup>
            <div>
              <strong>
                Heat Intensity: {(point.intensity * 100).toFixed(1)}%
              </strong>
              <br />
              Location: {point.lat.toFixed(4)}, {point.lng.toFixed(4)}
              <br />
              <small>Temperature anomaly detected</small>
            </div>
          </Popup>
        </Circle>
      ))}
    </>
  );
};

// Legend Component
const Legend = ({ mapData }) => {
  if (!mapData) return null;

  if (mapData.type === "uhi") {
    return (
      <div className="absolute bottom-4 right-4 bg-background border border-border p-3 rounded-lg shadow-lg z-[1000]">
        <h4 className="font-bold text-sm mb-2 text-foreground">
          Heat Intensity
        </h4>
        <div className="space-y-1 text-xs text-muted-foreground">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 mr-2 rounded"></div>
            <span>Low (0-50%)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 mr-2 rounded"></div>
            <span>Medium (50-70%)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 mr-2 rounded"></div>
            <span>High (70-100%)</span>
          </div>
        </div>
      </div>
    );
  }

  if (mapData.type === "geojson") {
    return (
      <div className="absolute bottom-4 right-4 bg-background border border-border p-3 rounded-lg shadow-lg z-[1000]">
        <h4 className="font-bold text-sm mb-2 text-foreground">
          Pothole Severity
        </h4>
        <div className="space-y-1 text-xs text-muted-foreground">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 mr-2 rounded-full"></div>
            <span>Minor</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 mr-2 rounded-full"></div>
            <span>Moderate</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 mr-2 rounded-full"></div>
            <span>Severe</span>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

// Main Map Component
const MapComponent = ({
  requestType,
  onRegionClick,
  onPathClick,
  regionCenter,
  pathPoints,
  radius,
  mapData,
}) => {
  // Style function for GeoJSON features
  const getGeoJSONStyle = (feature) => {
    const severity = feature.properties.severity;
    return {
      color:
        severity === "severe"
          ? "#ff0000"
          : severity === "moderate"
          ? "#ffaa00"
          : "#00ff00",
      radius: severity === "severe" ? 8 : severity === "moderate" ? 6 : 4,
      fillOpacity: 0.8,
      weight: 2,
    };
  };

  // Popup content for each feature
  const onEachFeature = (feature, layer) => {
    const { severity, timestamp, id } = feature.properties;
    layer.bindPopup(`
      <div>
        <strong>Pothole Detected</strong><br/>
        <strong>ID:</strong> ${id}<br/>
        <strong>Severity:</strong> <span style="color: ${
          severity === "severe"
            ? "#ff0000"
            : severity === "moderate"
            ? "#ffaa00"
            : "#00aa00"
        }">${severity}</span><br/>
        <strong>Detected:</strong> ${new Date(timestamp).toLocaleString()}<br/>
        <small>Click for more details</small>
      </div>
    `);
  };

  return (
    <div className="flex-1 relative">
      <MapContainer
        center={[12.9141, 79.1325]}
        zoom={13}
        className="h-full w-full"
        zoomControl={true}
        attributionControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        <MapClickHandler
          requestType={requestType}
          onRegionClick={onRegionClick}
          onPathClick={onPathClick}
        />

        {/* Show region selection */}
        {regionCenter && (
          <>
            <Marker position={regionCenter}>
              <Popup>
                <div>
                  <strong>Selected Center Point</strong>
                  <br />
                  Lat: {regionCenter.lat.toFixed(4)}
                  <br />
                  Lng: {regionCenter.lng.toFixed(4)}
                </div>
              </Popup>
            </Marker>
            <Circle
              center={regionCenter}
              radius={radius * 1000}
              color="blue"
              fillColor="blue"
              fillOpacity={0.1}
              weight={2}
            />
          </>
        )}

        {/* Show path selection and route */}
        {pathPoints.length > 0 && <RouteComponent pathPoints={pathPoints} />}

        {/* Show data visualization */}
        {mapData && mapData.type === "geojson" && (
          <GeoJSON
            data={mapData.data}
            style={getGeoJSONStyle}
            pointToLayer={(feature, latlng) => {
              return L.circleMarker(latlng, getGeoJSONStyle(feature));
            }}
            onEachFeature={onEachFeature}
          />
        )}

        {mapData && mapData.type === "uhi" && (
          <UHIOverlay data={mapData.data} />
        )}
      </MapContainer>

      {/* Map Instructions */}
      <div className="absolute top-4 left-4 bg-background border border-border p-3 rounded-lg shadow-lg z-[1000] max-w-xs">
        <h4 className="font-bold text-sm mb-2 text-foreground">
          Map Instructions
        </h4>
        <div className="text-xs text-muted-foreground space-y-1">
          {requestType === "region" ? (
            <>
              <p>• Click anywhere on the map to set center point</p>
              <p>• Use the radius slider to adjust area size</p>
              <p>• Blue circle shows selected region</p>
            </>
          ) : (
            <>
              <p>• Click twice on the map to set start and end points</p>
              <p>• Red line shows selected path</p>
              <p>• Adjust buffer width in the control panel</p>
            </>
          )}
        </div>
      </div>

      {/* Legend */}
      <Legend mapData={mapData} />

      {/* Loading Overlay */}
      {mapData === "loading" && (
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-[1001]">
          <div className="bg-background border border-border p-4 rounded-lg flex items-center space-x-3 shadow-lg">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span className="text-foreground">
              Processing geospatial data...
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapComponent;
