// src/App.jsx
import { useState, useEffect } from 'react';
import MapComponent from './components/MapComponent';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import LoginModal from './components/LoginModal';
import PaymentModal from './components/PaymentModal';
import RouteComponent from './components/RouteComponent';
import NotificationManager from './components/NotificationManager';
import CostDisplay from './components/CostDisplay';
import CostAnalytics from './components/CostAnalytics';
import { apiClient, costTracker } from './services/api';
import { DUMMY_POTHOLE_DATA, DUMMY_UHI_DATA } from './data/dummyData';
import './index.css';

const App = () => {
  // User state
  const [user, setUser] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  // Notification state
  const [notifications, setNotifications] = useState([]);
  
  // Cost tracking state
  const [showCostAnalytics, setShowCostAnalytics] = useState(false);
  const [currentCost, setCurrentCost] = useState(0);

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

  // Initialize cost tracker
  useEffect(() => {
    const initCostTracker = async () => {
      if (user?.id) {
        try {
          await costTracker.initialize(user.id, user.subscription_tier || 'FREE');
          const usage = await costTracker.getCurrentUsage();
          setCurrentCost(usage.cost_today);
        } catch (error) {
          console.error('Failed to initialize cost tracker:', error);
        }
      }
    };

    initCostTracker();
  }, [user]);

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
      // Test API connectivity first
      const healthCheck = await apiClient.testConnection();
      if (!healthCheck.connected) {
        throw new Error("Backend not available");
      }

      setUser({
        ...userData,
        paymentStatus: userData.paymentStatus || "unpaid",
      });
      addNotification("Successfully logged in!", "success");
    } catch (error) {
      console.error("Login error:", error);
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
      // Prepare request data and call appropriate API endpoint
      let response;
      let estimatedCost = 0;

      // Calculate cost before making the request
      if (requestType === "region") {
        estimatedCost = await costTracker.estimateRegionCost(
          { lat: regionCenter.lat, lng: regionCenter.lng },
          radius,
          selectedAPI
        );
        
        // Check if user can afford this request
        if (!(await costTracker.canMakeRequest(estimatedCost))) {
          addNotification("Request would exceed your usage limits", "error");
          setShowPaymentModal(true);
          return;
        }

        response = await apiClient.fetchRegionData(
          { lat: regionCenter.lat, lng: regionCenter.lng },
          radius,
          selectedAPI
        );
      } else {
        estimatedCost = await costTracker.estimatePathCost(
          { lat: pathPoints[0].lat, lng: pathPoints[0].lng },
          { lat: pathPoints[1].lat, lng: pathPoints[1].lng },
          bufferWidth,
          selectedAPI
        );
        
        // Check if user can afford this request
        if (!(await costTracker.canMakeRequest(estimatedCost))) {
          addNotification("Request would exceed your usage limits", "error");
          setShowPaymentModal(true);
          return;
        }

        response = await apiClient.fetchPathData(
          { lat: pathPoints[0].lat, lng: pathPoints[0].lng },
          { lat: pathPoints[1].lat, lng: pathPoints[1].lng },
          bufferWidth,
          selectedAPI
        );
      }

      // Record the request cost
      await costTracker.recordRequest(selectedAPI, requestType, estimatedCost);
      
      // Update current cost display
      const usage = await costTracker.getCurrentUsage();
      setCurrentCost(usage.cost_today);
      
      addNotification(`Request cost: $${estimatedCost.toFixed(4)}`, "info");

      // Process response and update map
      if (response && response.data) {
        if (selectedAPI === "potholes") {
          setMapData({ type: "geojson", data: response.data });
          const featureCount = response.data.features
            ? response.data.features.length
            : 0;
          addNotification(
            `Found ${featureCount} potholes in the selected area`,
            "success"
          );
        } else {
          setMapData({ type: "uhi", data: response.data });
          const dataCount = Array.isArray(response.data)
            ? response.data.length
            : 0;
          addNotification(
            `Heat island data loaded for ${dataCount} locations`,
            "success"
          );
        }
      } else {
        // Fallback to dummy data if no response
        if (selectedAPI === "potholes") {
          setMapData({ type: "geojson", data: DUMMY_POTHOLE_DATA });
          addNotification(
            `Using sample data: ${DUMMY_POTHOLE_DATA.features.length} potholes`,
            "warning"
          );
        } else {
          setMapData({ type: "uhi", data: DUMMY_UHI_DATA });
          addNotification(
            `Using sample data: ${DUMMY_UHI_DATA.length} locations`,
            "warning"
          );
        }
      }
    } catch (error) {
      console.error("API Error:", error);

      if (
        error.message?.includes("402") ||
        error.message?.includes("payment")
      ) {
        addNotification("Payment required for data access", "error");
        setShowPaymentModal(true);
      } else {
        // Fallback to dummy data on error
        addNotification("API unavailable, using sample data", "warning");
        if (selectedAPI === "potholes") {
          setMapData({ type: "geojson", data: DUMMY_POTHOLE_DATA });
        } else {
          setMapData({ type: "uhi", data: DUMMY_UHI_DATA });
        }
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

        <div className="flex-1 flex flex-col">
          <MapComponent
            requestType={requestType}
            onRegionClick={handleRegionClick}
            onPathClick={handlePathClick}
            regionCenter={regionCenter}
            pathPoints={pathPoints}
            radius={radius}
            mapData={mapData}
          />
          
          {/* Cost Display */}
          {user && (
            <div className="border-t p-4 bg-background">
              <div className="flex items-center justify-between mb-2">
                <CostDisplay
                  currentCost={currentCost}
                  tier={user.subscription_tier || 'FREE'}
                  costTracker={costTracker}
                />
                <button
                  onClick={() => setShowCostAnalytics(!showCostAnalytics)}
                  className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  {showCostAnalytics ? 'Hide Analytics' : 'Show Analytics'}
                </button>
              </div>
              
              {showCostAnalytics && (
                <CostAnalytics
                  userId={user.id}
                  tier={user.subscription_tier || 'FREE'}
                  costTracker={costTracker}
                />
              )}
            </div>
          )}
        </div>
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
