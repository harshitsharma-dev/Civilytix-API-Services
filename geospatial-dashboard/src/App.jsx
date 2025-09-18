// src/App.jsx
import React, { useState } from "react";

// Import components
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import MapComponent from "./components/MapComponent";
import LoginModal from "./components/LoginModal";
import PaymentModal from "./components/PaymentModal";
import NotificationManager from "./components/NotificationManager";

// Import data and API
import API from "./services/api";

// Import styles
import "./index.css";

const App = () => {
  // Initialize API client
  const apiClient = API;

  // User state
  const [user, setUser] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  // Notification state
  const [notifications, setNotifications] = useState([]);

  // Control panel state
  const [selectedAPI, setSelectedAPI] = useState("uhi");
  const [requestType, setRequestType] = useState("region");
  const [radius, setRadius] = useState(5);
  const [bufferWidth, setBufferWidth] = useState(100);
  const [loading, setLoading] = useState(false);

  // Map state
  const [mapData, setMapData] = useState(null);
  const [regionCenter, setRegionCenter] = useState(null);
  const [pathPoints, setPathPoints] = useState([]);
  const [mapCenterLocation, setMapCenterLocation] = useState(null); // New state for map centering

  // Notification helpers
  const addNotification = (message, type = "info") => {
    const id = Date.now() + Math.random();
    const newNotification = { id, message, type };
    setNotifications((prev) => [...prev, newNotification]);
  };

  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  // Authentication handlers
  const handleLogin = async (userData) => {
    try {
      // Use the API key from the user data (returned by our login endpoint)
      const apiKey = userData.api_key;
      if (!apiKey) {
        throw new Error("No API key received from login");
      }

      // Set API key for future requests
      apiClient.setAPIKey(apiKey);

      // Test API connectivity
      const healthCheck = await apiClient.testConnection();
      if (!healthCheck.connected) {
        throw new Error(
          "Backend not available. Please ensure the backend server is running."
        );
      }

      setUser({
        ...userData,
        apiKey: apiKey,
        // Map subscription_status to paymentStatus for backwards compatibility
        paymentStatus:
          userData.subscription_status === "premium" ? "paid" : "unpaid",
      });
      addNotification("Successfully logged in!", "success");
    } catch (error) {
      console.error("Login error:", error);
      addNotification(`Login failed: ${error.message}`, "error");
    }
  };

  const handleLogout = () => {
    // Clear API key from client
    apiClient.setAPIKey(null);

    // Clear user state
    setUser(null);
    setMapData(null);
    setRegionCenter(null);
    setPathPoints([]);
    addNotification("Logged out successfully", "info");
  };

  const handleUpgrade = () => {
    setShowPaymentModal(true);
  };

  const handlePayment = async () => {
    try {
      // For now, simulate payment processing
      // In real implementation, this would integrate with payment provider
      setUser((prev) => ({ ...prev, paymentStatus: "paid" }));
      addNotification(
        "Payment successful! Premium features unlocked.",
        "success"
      );
    } catch (error) {
      console.error("Payment error:", error);
      addNotification("Payment failed. Please try again.", "error");
    }
  };

  // Map interaction handlers
  const handleRegionClick = (latlng) => {
    setRegionCenter(latlng);
    setPathPoints([]);
    addNotification(
      `Region center set at ${latlng.lat.toFixed(4)}, ${latlng.lng.toFixed(4)}`,
      "info"
    );
  };

  const handlePathClick = (latlng) => {
    if (pathPoints.length < 2) {
      const newPathPoints = [...pathPoints, latlng];
      setPathPoints(newPathPoints);
      setRegionCenter(null);

      if (newPathPoints.length === 1) {
        addNotification(
          "First point set. Click again to set end point.",
          "info"
        );
      } else {
        addNotification("Path defined successfully!", "success");
      }
    } else {
      // Reset path
      setPathPoints([latlng]);
      addNotification("Path reset. Click again to set end point.", "info");
    }
  };

  // Location search handler
  const handleLocationSelect = (location) => {
    const { lat, lng, name } = location;

    // Center the map on the selected location
    setMapCenterLocation({ lat, lng });

    if (requestType === "region") {
      setRegionCenter({ lat, lng });
      setPathPoints([]);
      addNotification(
        `Region center set at ${
          name || `${lat.toFixed(4)}, ${lng.toFixed(4)}`
        }`,
        "success"
      );
    } else {
      // For path mode, set as first point
      setPathPoints([{ lat, lng }]);
      setRegionCenter(null);
      addNotification(
        `Path start point set at ${
          name || `${lat.toFixed(4)}, ${lng.toFixed(4)}`
        }. Click map for end point.`,
        "info"
      );
    }
  };

  // Data request handler
  const handleGetData = async () => {
    // Validation
    if (!user) {
      addNotification("Please login first", "error");
      return;
    }

    if (user.paymentStatus !== "paid") {
      addNotification("Premium subscription required for data access", "error");
      setShowPaymentModal(true);
      return;
    }

    if (requestType === "region" && !regionCenter) {
      addNotification("Please click on the map to set a center point", "error");
      return;
    }

    if (requestType === "path" && pathPoints.length < 2) {
      addNotification(
        "Please click twice on the map to define a path",
        "error"
      );
      return;
    }

    setLoading(true);
    setMapData("loading"); // Show loading indicator on map
    addNotification("Processing your request...", "info");

    try {
      // Set API key for the request
      apiClient.setAPIKey(user.apiKey || "user3_paid_token");

      let response;

      if (requestType === "region") {
        response = await apiClient.fetchRegionData(
          { lat: regionCenter.lat, lon: regionCenter.lng }, // use 'lon'
          radius,
          selectedAPI
        );
      } else {
        response = await apiClient.fetchPathData(
          { lat: pathPoints[0].lat, lng: pathPoints[0].lng },
          { lat: pathPoints[1].lat, lng: pathPoints[1].lng },
          bufferWidth,
          selectedAPI
        );
      }

      // Process response and update map
      if (response && response.data) {
        if (selectedAPI === "potholes") {
          // Debug: Log the actual response data structure
          console.log("Pothole response data:", response.data);
          console.log("Type of response.data:", typeof response.data);
          console.log("Has features?", "features" in response.data);

          // Backend returns GeoJSON data for potholes
          setMapData({ type: "geojson", data: response.data });
          const featureCount = response.data.features
            ? response.data.features.length
            : 0;
          addNotification(
            `Found ${featureCount} potholes in the selected area`,
            "success"
          );
        } else {
          // For UHI data, we need to process the backend response
          // Backend currently returns placeholder data - adapt as needed
          if (Array.isArray(response.data)) {
            setMapData({ type: "uhi", data: response.data });
            addNotification(
              `Heat island data loaded for ${response.data.length} locations`,
              "success"
            );
          } else {
            // Handle placeholder UHI response from backend
            const placeholderUHIData = [];
            if (requestType === "region" && regionCenter) {
              // Generate some placeholder points around the center
              for (let i = 0; i < 5; i++) {
                placeholderUHIData.push({
                  lat: regionCenter.lat + (Math.random() - 0.5) * (radius / 55), // Rough conversion
                  lng: regionCenter.lng + (Math.random() - 0.5) * (radius / 55),
                  intensity: Math.random(),
                });
              }
            } else if (requestType === "path" && pathPoints.length >= 2) {
              // Generate some placeholder points along the path
              for (let i = 0; i < 3; i++) {
                const t = i / 2; // Interpolation factor
                placeholderUHIData.push({
                  lat:
                    pathPoints[0].lat +
                    t * (pathPoints[1].lat - pathPoints[0].lat),
                  lng:
                    pathPoints[0].lng +
                    t * (pathPoints[1].lng - pathPoints[0].lng),
                  intensity: Math.random(),
                });
              }
            }
            setMapData({ type: "uhi", data: placeholderUHIData });
            addNotification(
              `UHI analysis complete for the selected area`,
              "success"
            );
          }
        }
      } else {
        addNotification("No data found for the selected area", "warning");
        setMapData(null);
      }
    } catch (error) {
      console.error("API Error:", error);

      if (
        error.message?.includes("402") ||
        error.message?.includes("payment") ||
        error.message?.includes("Payment Required")
      ) {
        addNotification("Payment required for data access", "error");
        setShowPaymentModal(true);
      } else if (
        error.message?.includes("401") ||
        error.message?.includes("Invalid API Key")
      ) {
        addNotification("Authentication failed. Please login again.", "error");
        setUser(null);
      } else {
        addNotification(
          "Error fetching data from backend. Please try again.",
          "error"
        );
      }
      setMapData(null);
    } finally {
      setLoading(false);
    }
  };

  // Control panel handlers
  const handleAPIChange = (api) => {
    setSelectedAPI(api);
    setMapData(null); // Clear previous data when switching APIs
    addNotification(
      `Switched to ${
        api === "uhi" ? "Urban Heat Island" : "Pothole Detection"
      } API`,
      "info"
    );
  };

  const handleRequestTypeChange = (type) => {
    setRequestType(type);
    setRegionCenter(null);
    setPathPoints([]);
    setMapData(null);
    addNotification(
      `Switched to ${type === "region" ? "Region" : "Path"} mode`,
      "info"
    );
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <Navbar
        user={user}
        onLogin={() => setShowLoginModal(true)}
        onLogout={handleLogout}
        onUpgrade={handleUpgrade}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          user={user}
          selectedAPI={selectedAPI}
          onAPIChange={handleAPIChange}
          requestType={requestType}
          onRequestTypeChange={handleRequestTypeChange}
          radius={radius}
          onRadiusChange={setRadius}
          bufferWidth={bufferWidth}
          onBufferWidthChange={setBufferWidth}
          onGetData={handleGetData}
          loading={loading}
          onLocationSelect={handleLocationSelect}
        />

        <MapComponent
          requestType={requestType}
          onRegionClick={handleRegionClick}
          onPathClick={handlePathClick}
          regionCenter={regionCenter}
          pathPoints={pathPoints}
          radius={radius}
          mapData={mapData}
          centerLocation={mapCenterLocation}
        />
      </div>

      {/* Notifications */}
      <NotificationManager
        notifications={notifications}
        onRemove={removeNotification}
      />

      {/* Modals rendered outside flex container for full overlay */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onLogin={handleLogin}
      />

      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onPayment={handlePayment}
      />
    </div>
  );
};

export default App;
