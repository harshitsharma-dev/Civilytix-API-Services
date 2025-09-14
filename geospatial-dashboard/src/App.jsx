// src/App.jsx
import React, { useState } from "react";

// Import components
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import MapComponent from "./components/MapComponent";
import LoginModal from "./components/LoginModal";
import PaymentModal from "./components/PaymentModal";
import NotificationManager from "./components/NotificationManager";

// Import data
import {
  DUMMY_POTHOLE_DATA,
  DUMMY_UHI_DATA,
  simulateAPICall,
} from "./data/dummyData";

// Import styles
import "./index.css";

const App = () => {
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
      // Simulate API call
      const response = await simulateAPICall("login", userData, 500);
      setUser({
        ...userData,
        paymentStatus: userData.paymentStatus || "unpaid",
      });
      addNotification("Successfully logged in!", "success");
    } catch (error) {
      addNotification("Login failed. Please try again.", "error");
    }
  };

  const handleLogout = () => {
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
      const response = await simulateAPICall("payment", { amount: 5000 }, 2000);
      setUser((prev) => ({ ...prev, paymentStatus: "paid" }));
      addNotification(
        "Payment successful! Premium features unlocked.",
        "success"
      );
    } catch (error) {
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
    addNotification("Processing your request...", "info");

    try {
      // Prepare request data
      const requestData =
        requestType === "region"
          ? {
              center: { lat: regionCenter.lat, lon: regionCenter.lng },
              radius_km: radius,
              dataType: selectedAPI,
            }
          : {
              start_coords: { lat: pathPoints[0].lat, lon: pathPoints[0].lng },
              end_coords: { lat: pathPoints[1].lat, lon: pathPoints[1].lng },
              buffer_meters: bufferWidth,
              dataType: selectedAPI,
            };

      // Simulate API call
      const response = await simulateAPICall(
        `data/${requestType}`,
        {
          ...requestData,
          paymentStatus: user.paymentStatus,
        },
        2000
      );

      // Process response and update map
      if (selectedAPI === "potholes") {
        setMapData({ type: "geojson", data: DUMMY_POTHOLE_DATA });
        addNotification(
          `Found ${DUMMY_POTHOLE_DATA.features.length} potholes in the selected area`,
          "success"
        );
      } else {
        setMapData({ type: "uhi", data: DUMMY_UHI_DATA });
        addNotification(
          `Heat island data loaded for ${DUMMY_UHI_DATA.length} locations`,
          "success"
        );
      }
    } catch (error) {
      if (error.status === 402) {
        addNotification("Payment required for data access", "error");
        setShowPaymentModal(true);
      } else {
        addNotification("Failed to fetch data. Please try again.", "error");
      }
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
        />

        <MapComponent
          requestType={requestType}
          onRegionClick={handleRegionClick}
          onPathClick={handlePathClick}
          regionCenter={regionCenter}
          pathPoints={pathPoints}
          radius={radius}
          mapData={mapData}
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
