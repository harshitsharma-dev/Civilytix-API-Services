// src/services/usageAPI.js
import { api } from './api';

export const usageAPI = {
  // Get usage instances with filters
  async getInstances(params = {}) {
    const searchParams = new URLSearchParams();
    
    if (params.limit) searchParams.append('limit', params.limit);
    if (params.endpoint_filter) searchParams.append('endpoint_filter', params.endpoint_filter);
    if (params.user_tier_filter) searchParams.append('user_tier_filter', params.user_tier_filter);
    if (params.time_range_minutes) searchParams.append('time_range_minutes', params.time_range_minutes);
    
    const response = await api.get(`/usage/instances?${searchParams}`);
    return response.data;
  },

  // Get real-time metrics
  async getMetrics(forceRefresh = false) {
    const params = forceRefresh ? '?force_refresh=true' : '';
    const response = await api.get(`/usage/metrics${params}`);
    return response.data;
  },

  // Get endpoint-specific usage
  async getEndpointUsage(endpointName, hours = 24) {
    const response = await api.get(`/usage/endpoint/${endpointName}?hours=${hours}`);
    return response.data;
  },

  // Get user-specific usage
  async getUserUsage(userId, hours = 24) {
    const response = await api.get(`/usage/user/${userId}?hours=${hours}`);
    return response.data;
  },

  // Get hourly trends
  async getHourlyTrends(hours = 24) {
    const response = await api.get(`/usage/trends/hourly?hours=${hours}`);
    return response.data;
  },

  // Get cost breakdown
  async getCostBreakdown(hours = 24, groupBy = 'endpoint') {
    const response = await api.get(`/usage/costs/breakdown?hours=${hours}&group_by=${groupBy}`);
    return response.data;
  },

  // Get slowest requests
  async getSlowestRequests(limit = 10, hours = 24) {
    const response = await api.get(`/usage/performance/slowest?limit=${limit}&hours=${hours}`);
    return response.data;
  },

  // Get error analysis
  async getErrorAnalysis(hours = 24) {
    const response = await api.get(`/usage/performance/errors?hours=${hours}`);
    return response.data;
  }
};