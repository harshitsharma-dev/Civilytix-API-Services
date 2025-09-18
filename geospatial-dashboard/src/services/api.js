// API configuration and client for connecting to backend
import CostTracker from './costTracker.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

class APIClient {
  constructor() {
    this.baseURL = `${API_BASE_URL}${API_VERSION}`;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Set API key for authenticated requests
  setAPIKey(apiKey) {
    this.apiKey = apiKey;
  }

  // Get headers with API key if available
  getHeaders() {
    const headers = { ...this.defaultHeaders };
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    return headers;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Health check (no API prefix)
  async healthCheck() {
    const url = `${API_BASE_URL}/health`;
    const config = {
      headers: this.getHeaders(),
      method: 'GET',
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: /health`, error);
      throw error;
    }
  }

  // Data endpoints
  async getRegionData(requestData) {
    return this.request('/data/region', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  async getPathData(requestData) {
    return this.request('/data/path', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  // User endpoints
  async getUserHistory() {
    return this.request('/user/history', { method: 'GET' });
  }

  async getRequestDetails(requestId) {
    return this.request(`/user/history/${requestId}`, { method: 'GET' });
  }

  async getUserProfile() {
    return this.request('/user/profile', { method: 'GET' });
  }

  async getUserStats() {
    return this.request('/user/stats', { method: 'GET' });
  }
}

// Create and export API client instance
const apiClient = new APIClient();

// Create cost tracker instance
const costTracker = new CostTracker(apiClient);

// Set default API key if available
const defaultAPIKey = import.meta.env.VITE_DEFAULT_API_KEY;
if (defaultAPIKey) {
  apiClient.setAPIKey(defaultAPIKey);
}

export { apiClient, costTracker };

// Utility functions for common API operations
export const API = {
  // Test backend connectivity
  async testConnection() {
    try {
      const health = await apiClient.healthCheck();
      return { connected: true, health };
    } catch (error) {
      return { connected: false, error: error.message };
    }
  },

  // Set user API key
  setAPIKey(apiKey) {
    apiClient.setAPIKey(apiKey);
  },

  // Get data for map region
  async fetchRegionData(center, radiusKm, dataType) {
    const requestData = {
      center: {
        lat: center.lat,
        lon: center.lng || center.lon  // Handle both lng and lon formats
      },
      radius_km: radiusKm,
      dataType,
    };
    return apiClient.getRegionData(requestData);
  },

  // Get data for path/route
  async fetchPathData(startCoords, endCoords, bufferMeters, dataType) {
    const requestData = {
      start_coords: {
        lat: startCoords.lat,
        lon: startCoords.lng || startCoords.lon  // Handle both lng and lon formats
      },
      end_coords: {
        lat: endCoords.lat,
        lon: endCoords.lng || endCoords.lon  // Handle both lng and lon formats
      },
      buffer_meters: bufferMeters,
      dataType,
    };
    return apiClient.getPathData(requestData);
  },

  // User-related operations
  async fetchUserHistory() {
    return apiClient.getUserHistory();
  },

  async fetchRequestResult(requestId) {
    return apiClient.getRequestDetails(requestId);
  },

  async fetchUserProfile() {
    return apiClient.getUserProfile();
  },

  async fetchUserStats() {
    return apiClient.getUserStats();
  },
};

export default API;