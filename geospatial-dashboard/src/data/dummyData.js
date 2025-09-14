// src/data/dummyData.js

// Dummy Pothole Data (GeoJSON format)
export const DUMMY_POTHOLE_DATA = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1325, 12.9141] 
      },
      properties: { 
        severity: "severe", 
        timestamp: "2024-09-10T10:00:00Z", 
        id: 1,
        description: "Large pothole blocking traffic",
        depth: "15cm",
        width: "45cm"
      }
    },
    {
      type: "Feature", 
      geometry: { 
        type: "Point", 
        coordinates: [79.1335, 12.9151] 
      },
      properties: { 
        severity: "moderate", 
        timestamp: "2024-09-10T11:00:00Z", 
        id: 2,
        description: "Medium-sized pothole",
        depth: "8cm",
        width: "25cm"
      }
    },
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1315, 12.9131] 
      },
      properties: { 
        severity: "minor", 
        timestamp: "2024-09-10T12:00:00Z", 
        id: 3,
        description: "Small surface crack",
        depth: "3cm",
        width: "10cm"
      }
    },
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1345, 12.9161] 
      },
      properties: { 
        severity: "severe", 
        timestamp: "2024-09-11T09:30:00Z", 
        id: 4,
        description: "Deep pothole with water accumulation",
        depth: "20cm",
        width: "60cm"
      }
    },
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1305, 12.9121] 
      },
      properties: { 
        severity: "moderate", 
        timestamp: "2024-09-11T14:15:00Z", 
        id: 5,
        description: "Road surface deterioration",
        depth: "10cm",
        width: "30cm"
      }
    },
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1355, 12.9171] 
      },
      properties: { 
        severity: "minor", 
        timestamp: "2024-09-12T08:45:00Z", 
        id: 6,
        description: "Hairline crack in asphalt",
        depth: "2cm",
        width: "8cm"
      }
    },
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1295, 12.9111] 
      },
      properties: { 
        severity: "severe", 
        timestamp: "2024-09-12T16:20:00Z", 
        id: 7,
        description: "Major road damage affecting lane",
        depth: "25cm",
        width: "80cm"
      }
    },
    {
      type: "Feature",
      geometry: { 
        type: "Point", 
        coordinates: [79.1365, 12.9181] 
      },
      properties: { 
        severity: "moderate", 
        timestamp: "2024-09-13T11:10:00Z", 
        id: 8,
        description: "Pothole with loose gravel",
        depth: "12cm",
        width: "35cm"
      }
    }
  ]
};

// Dummy Urban Heat Island Data (Point-based intensity data)
export const DUMMY_UHI_DATA = [
  { 
    lat: 12.914, 
    lng: 79.132, 
    intensity: 0.85,
    temperature: 35.2,
    area: "Commercial District"
  },
  { 
    lat: 12.915, 
    lng: 79.133, 
    intensity: 0.65,
    temperature: 32.8,
    area: "Residential Area"
  },
  { 
    lat: 12.916, 
    lng: 79.134, 
    intensity: 0.92,
    temperature: 37.1,
    area: "Industrial Zone"
  },
  { 
    lat: 12.913, 
    lng: 79.131, 
    intensity: 0.45,
    temperature: 29.5,
    area: "Park Area"
  },
  { 
    lat: 12.917, 
    lng: 79.135, 
    intensity: 0.78,
    temperature: 34.6,
    area: "Urban Center"
  },
  { 
    lat: 12.912, 
    lng: 79.130, 
    intensity: 0.38,
    temperature: 28.2,
    area: "Water Body Vicinity"
  },
  { 
    lat: 12.918, 
    lng: 79.136, 
    intensity: 0.88,
    temperature: 36.4,
    area: "Dense Urban Area"
  },
  { 
    lat: 12.911, 
    lng: 79.129, 
    intensity: 0.42,
    temperature: 28.9,
    area: "Green Corridor"
  },
  { 
    lat: 12.919, 
    lng: 79.137, 
    intensity: 0.72,
    temperature: 33.7,
    area: "Mixed Development"
  },
  { 
    lat: 12.910, 
    lng: 79.128, 
    intensity: 0.35,
    temperature: 27.8,
    area: "Forest Edge"
  },
  { 
    lat: 12.920, 
    lng: 79.138, 
    intensity: 0.89,
    temperature: 36.8,
    area: "Highway Junction"
  },
  { 
    lat: 12.909, 
    lng: 79.127, 
    intensity: 0.31,
    temperature: 27.2,
    area: "Rural Outskirts"
  },
  { 
    lat: 12.921, 
    lng: 79.139, 
    intensity: 0.76,
    temperature: 34.1,
    area: "Shopping Complex"
  },
  { 
    lat: 12.908, 
    lng: 79.126, 
    intensity: 0.28,
    temperature: 26.8,
    area: "Agricultural Land"
  },
  { 
    lat: 12.922, 
    lng: 79.140, 
    intensity: 0.83,
    temperature: 35.7,
    area: "Bus Terminal"
  }
];

// Dummy User Data
export const DUMMY_USERS = [
  {
    id: 1,
    name: "John Doe",
    email: "john.doe@example.com",
    paymentStatus: "unpaid",
    token: "dummy_jwt_token_1"
  },
  {
    id: 2,
    name: "Jane Smith",
    email: "jane.smith@example.com", 
    paymentStatus: "paid",
    token: "dummy_jwt_token_2"
  },
  {
    id: 3,
    name: "Admin User",
    email: "admin@platform.com",
    paymentStatus: "paid",
    token: "dummy_jwt_token_admin"
  },
  {
    id: 4,
    name: "Test User",
    email: "test@example.com",
    paymentStatus: "unpaid",
    token: "dummy_jwt_token_test"
  }
];

// Dummy API Responses
export const DUMMY_API_RESPONSES = {
  payment: {
    success: {
      clientSecret: "pi_dummy_client_secret_123",
      orderId: "order_dummy_456",
      amount: 5000,
      currency: "usd",
      status: "succeeded"
    },
    error: {
      error: "Payment processing failed",
      code: "payment_failed",
      message: "Your card was declined"
    }
  },
  
  dataRequest: {
    success: {
      status: "success",
      downloadUrl: "https://dummy-api.com/download/data_123.json",
      requestId: "req_dummy_789",
      processedAt: new Date().toISOString(),
      fileSize: "2.3 MB",
      format: "GeoJSON",
      recordCount: 150
    },
    paymentRequired: {
      status: "payment_required",
      message: "Premium subscription required for data access",
      upgradeUrl: "/upgrade",
      code: 402
    },
    processing: {
      status: "processing",
      message: "Your request is being processed",
      estimatedTime: "2-3 minutes",
      requestId: "req_processing_456"
    },
    error: {
      status: "error",
      message: "Failed to process your request",
      code: "processing_error"
    }
  },
  
  history: [
    {
      id: "req_001",
      dataType: "potholes",
      requestType: "region",
      timestamp: "2024-09-10T10:00:00Z",
      status: "completed",
      downloadUrl: "https://dummy-api.com/download/potholes_001.json",
      fileSize: "1.8 MB",
      recordCount: 45
    },
    {
      id: "req_002", 
      dataType: "uhi",
      requestType: "path",
      timestamp: "2024-09-09T15:30:00Z",
      status: "completed",
      downloadUrl: "https://dummy-api.com/download/uhi_002.tiff",
      fileSize: "3.2 MB",
      recordCount: 120
    },
    {
      id: "req_003",
      dataType: "potholes",
      requestType: "region", 
      timestamp: "2024-09-08T09:15:00Z",
      status: "processing",
      downloadUrl: null,
      estimatedCompletion: "2024-09-08T09:18:00Z"
    },
    {
      id: "req_004",
      dataType: "uhi",
      requestType: "region",
      timestamp: "2024-09-07T14:22:00Z", 
      status: "failed",
      downloadUrl: null,
      error: "Insufficient data coverage for selected region"
    },
    {
      id: "req_005",
      dataType: "potholes",
      requestType: "path",
      timestamp: "2024-09-06T11:45:00Z",
      status: "completed",
      downloadUrl: "https://dummy-api.com/download/potholes_005.json",
      fileSize: "892 KB",
      recordCount: 23
    }
  ]
};

// Extended geographical data for different regions
export const REGIONAL_DATA = {
  vellore: {
    potholes: DUMMY_POTHOLE_DATA,
    uhi: DUMMY_UHI_DATA,
    center: { lat: 12.9141, lng: 79.1325 }
  },
  chennai: {
    potholes: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: { type: "Point", coordinates: [80.2707, 13.0827] },
          properties: { severity: "severe", timestamp: "2024-09-13T10:30:00Z", id: 101 }
        },
        {
          type: "Feature",
          geometry: { type: "Point", coordinates: [80.2717, 13.0837] },
          properties: { severity: "moderate", timestamp: "2024-09-13T11:15:00Z", id: 102 }
        }
      ]
    },
    uhi: [
      { lat: 13.0827, lng: 80.2707, intensity: 0.91, temperature: 38.5, area: "Marina Beach Area" },
      { lat: 13.0837, lng: 80.2717, intensity: 0.76, temperature: 34.2, area: "T. Nagar" }
    ],
    center: { lat: 13.0827, lng: 80.2707 }
  }
};

// Simulation helper functions
export const simulateAPICall = (endpoint, data, delay = 1000) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      try {
        switch (endpoint) {
          case 'login':
            // Simulate successful login
            resolve({
              user: data.name ? 
                { ...DUMMY_USERS[0], name: data.name } : 
                DUMMY_USERS[0],
              token: "dummy_jwt_token_" + Date.now()
            });
            break;
            
          case 'payment':
            // Simulate payment with 90% success rate
            if (Math.random() > 0.1) {
              resolve(DUMMY_API_RESPONSES.payment.success);
            } else {
              reject({
                status: 400,
                data: DUMMY_API_RESPONSES.payment.error
              });
            }
            break;
            
          case 'data/region':
          case 'data/path':
            // Check payment status
            if (data.paymentStatus !== 'paid') {
              reject({
                status: 402,
                data: DUMMY_API_RESPONSES.dataRequest.paymentRequired
              });
            } else {
              // Simulate occasional processing delays
              if (Math.random() > 0.8) {
                resolve(DUMMY_API_RESPONSES.dataRequest.processing);
              } else {
                resolve(DUMMY_API_RESPONSES.dataRequest.success);
              }
            }
            break;
            
          case 'history':
            resolve(DUMMY_API_RESPONSES.history);
            break;
            
          case 'history/req_001':
            resolve(DUMMY_API_RESPONSES.history[0]);
            break;
            
          default:
            reject({ 
              status: 404, 
              message: 'Endpoint not found',
              data: { error: 'API endpoint does not exist' }
            });
        }
      } catch (error) {
        reject({
          status: 500,
          message: 'Internal server error',
          data: { error: 'Something went wrong' }
        });
      }
    }, delay);
  });
};

// Utility functions for data processing
export const filterPotholesBySeverity = (severity) => {
  return {
    ...DUMMY_POTHOLE_DATA,
    features: DUMMY_POTHOLE_DATA.features.filter(
      feature => feature.properties.severity === severity
    )
  };
};

export const filterUHIByIntensity = (minIntensity) => {
  return DUMMY_UHI_DATA.filter(point => point.intensity >= minIntensity);
};

export const getDataInRadius = (center, radiusKm, dataType) => {
  const data = dataType === 'potholes' ? DUMMY_POTHOLE_DATA.features : DUMMY_UHI_DATA;
  
  return data.filter(item => {
    const itemLat = dataType === 'potholes' ? item.geometry.coordinates[1] : item.lat;
    const itemLng = dataType === 'potholes' ? item.geometry.coordinates[0] : item.lng;
    
    // Simple distance calculation (not precise but good for demo)
    const distance = Math.sqrt(
      Math.pow(center.lat - itemLat, 2) + Math.pow(center.lng - itemLng, 2)
    ) * 111; // Rough conversion to km
    
    return distance <= radiusKm;
  });
};

// Map center coordinates for different cities
export const CITY_COORDINATES = {
  vellore: { lat: 12.9141, lng: 79.1325, zoom: 13 },
  chennai: { lat: 13.0827, lng: 80.2707, zoom: 11 },
  bangalore: { lat: 12.9716, lng: 77.5946, zoom: 11 },
  mumbai: { lat: 19.0760, lng: 72.8777, zoom: 11 },
  delhi: { lat: 28.6139, lng: 77.2090, zoom: 11 },
  hyderabad: { lat: 17.3850, lng: 78.4867, zoom: 11 },
  pune: { lat: 18.5204, lng: 73.8567, zoom: 12 },
  kolkata: { lat: 22.5726, lng: 88.3639, zoom: 11 }
};

// Sample request/response formats for documentation
export const API_EXAMPLES = {
  regionRequest: {
    center: { lat: 12.9141, lon: 79.1325 },
    radius_km: 5,
    dataType: "potholes"
  },
  pathRequest: {
    start_coords: { lat: 12.9141, lon: 79.1325 },
    end_coords: { lat: 12.9151, lon: 79.1335 },
    buffer_meters: 100,
    dataType: "uhi"
  },
  paymentRequest: {
    amount: 5000,
    currency: "usd"
  }
};

export default {
  DUMMY_POTHOLE_DATA,
  DUMMY_UHI_DATA,
  DUMMY_USERS,
  DUMMY_API_RESPONSES,
  REGIONAL_DATA,
  simulateAPICall,
  filterPotholesBySeverity,
  filterUHIByIntensity,
  getDataInRadius,
  CITY_COORDINATES,
  API_EXAMPLES
};