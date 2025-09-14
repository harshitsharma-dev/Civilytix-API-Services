// src/utils/googleMaps.js

// Load Google Maps JavaScript API
let googleMapsLoaded = false;
let googleMapsPromise = null;

const loadGoogleMaps = (apiKey) => {
  if (googleMapsLoaded) {
    console.log("Google Maps already loaded");
    return Promise.resolve(window.google);
  }

  if (googleMapsPromise) {
    console.log("Google Maps loading in progress");
    return googleMapsPromise;
  }

  console.log("Starting to load Google Maps API...");

  googleMapsPromise = new Promise((resolve, reject) => {
    if (window.google) {
      googleMapsLoaded = true;
      console.log("Google Maps found in window object");
      resolve(window.google);
      return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=geometry`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      console.log("Google Maps script loaded successfully");
      googleMapsLoaded = true;
      resolve(window.google);
    };

    script.onerror = (error) => {
      console.error("Failed to load Google Maps script:", error);
      reject(new Error("Failed to load Google Maps API"));
    };

    document.head.appendChild(script);
    console.log("Google Maps script tag added to head");
  });

  return googleMapsPromise;
};

// Google Maps Directions API utility using JavaScript API
export const fetchDirections = async (startPoint, endPoint, apiKey) => {
  console.log("fetchDirections called with:", {
    startPoint,
    endPoint,
    hasApiKey: !!apiKey,
  });

  if (!apiKey) {
    console.warn(
      "Google Maps API key not provided, falling back to straight line"
    );
    return null;
  }

  try {
    console.log("Loading Google Maps API...");
    // Add timeout for Google Maps loading
    const google = await Promise.race([
      loadGoogleMaps(apiKey),
      new Promise((_, reject) =>
        setTimeout(
          () => reject(new Error("Google Maps API loading timeout")),
          10000
        )
      ),
    ]);

    console.log("Google Maps API loaded, creating directions service...");

    return new Promise((resolve, reject) => {
      const directionsService = new google.maps.DirectionsService();

      // Add timeout for directions request
      const timeoutId = setTimeout(() => {
        console.error("Directions request timeout");
        resolve(null);
      }, 8000);

      console.log("Requesting directions...");

      directionsService.route(
        {
          origin: new google.maps.LatLng(startPoint.lat, startPoint.lng),
          destination: new google.maps.LatLng(endPoint.lat, endPoint.lng),
          travelMode: google.maps.TravelMode.DRIVING,
          unitSystem: google.maps.UnitSystem.METRIC,
          optimizeWaypoints: false,
          avoidHighways: false,
          avoidTolls: false,
        },
        (result, status) => {
          clearTimeout(timeoutId);
          console.log("Directions response:", { status, result });

          if (
            status === google.maps.DirectionsStatus.OK &&
            result.routes.length > 0
          ) {
            console.log("Directions request successful");
            const route = result.routes[0];
            const leg = route.legs[0];

            // Convert Google Maps polyline to Leaflet format
            const path = google.maps.geometry.encoding
              .decodePath(route.overview_polyline)
              .map((point) => [point.lat(), point.lng()]);

            console.log("Route processed, path points:", path.length);

            resolve({
              path,
              distance: leg.distance.text,
              duration: leg.duration.text,
              steps: leg.steps,
            });
          } else {
            console.error("Directions request failed:", status);
            resolve(null);
          }
        }
      );
    });
  } catch (error) {
    console.error("Error loading Google Maps API:", error);
    return null;
  }
};

// Simple fallback routing that creates a curved path between two points
export const createSimpleRoute = (startPoint, endPoint) => {
  console.log("Using simple route fallback");

  const lat1 = startPoint.lat;
  const lng1 = startPoint.lng;
  const lat2 = endPoint.lat;
  const lng2 = endPoint.lng;

  // Create a simple curved path with intermediate points
  const path = [];
  const numPoints = 10;

  for (let i = 0; i <= numPoints; i++) {
    const ratio = i / numPoints;

    // Linear interpolation with a slight curve
    const lat = lat1 + (lat2 - lat1) * ratio;
    const lng = lng1 + (lng2 - lng1) * ratio;

    // Add slight curve by offsetting middle points
    const curveOffset = Math.sin(ratio * Math.PI) * 0.002;
    const adjustedLat = lat + curveOffset;

    path.push([adjustedLat, lng]);
  }

  // Calculate approximate distance and duration
  const distance = calculateDistance(lat1, lng1, lat2, lng2);
  const duration = Math.round(distance * 2.5); // Rough estimate: 2.5 minutes per km

  return {
    path,
    distance: `${distance.toFixed(1)} km`,
    duration: `${duration} mins`,
    steps: [],
  };
};

// Calculate distance between two points using Haversine formula
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371; // Earth's radius in kilometers
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};
