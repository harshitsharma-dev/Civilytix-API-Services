// src/services/costTracker.js

class CostTracker {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.userId = null;
    this.userTier = 'FREE';
    this.currentUsage = {
      cost_today: 0,
      requests_today: 0,
      cost_month: 0,
      requests_month: 0
    };
  }

  /**
   * Initialize the cost tracker with user info
   */
  async initialize(userId, userTier = 'FREE') {
    this.userId = userId;
    this.userTier = userTier;
    
    // Initialize with default values for demo
    this.currentUsage = {
      cost_today: 0,
      requests_today: 0,
      cost_month: 0,
      requests_month: 0
    };
  }

  /**
   * Get current usage statistics
   */
  async getCurrentUsage() {
    return this.currentUsage;
  }

  /**
   * Check if user can make a request with given cost
   */
  async canMakeRequest(estimatedCost) {
    // For demo purposes, always allow requests
    // In production, this would check against usage limits
    return true;
  }

  /**
   * Record a completed request
   */
  async recordRequest(apiType, requestType, cost) {
    this.currentUsage.cost_today += cost;
    this.currentUsage.requests_today += 1;
    this.currentUsage.cost_month += cost;
    this.currentUsage.requests_month += 1;
  }

  /**
   * Estimate cost for a region-based request
   */
  async estimateRegionCost(center, radiusKm, dataType) {
    try {
      const response = await this.apiClient.request('/data/estimate-cost/region', {
        method: 'POST',
        body: JSON.stringify({
          center: { lat: center.lat, lon: center.lng || center.lon },
          radius_km: radiusKm,
          dataType: dataType
        }),
      });
      return response;
    } catch (error) {
      console.error('Error estimating region cost:', error);
      throw error;
    }
  }

  /**
   * Estimate cost for a path-based request
   */
  async estimatePathCost(startCoords, endCoords, bufferMeters, dataType) {
    try {
      const response = await this.apiClient.request('/data/estimate-cost/path', {
        method: 'POST',
        body: JSON.stringify({
          start_coords: { lat: startCoords.lat, lon: startCoords.lng || startCoords.lon },
          end_coords: { lat: endCoords.lat, lon: endCoords.lng || endCoords.lon },
          buffer_meters: bufferMeters,
          dataType: dataType
        }),
      });
      return response;
    } catch (error) {
      console.error('Error estimating path cost:', error);
      throw error;
    }
  }

  /**
   * Get user's cost summary
   */
  async getCostSummary(days = 30) {
    try {
      const response = await this.apiClient.request(`/user/cost-summary?days=${days}`, {
        method: 'GET',
      });
      return response;
    } catch (error) {
      console.error('Error fetching cost summary:', error);
      throw error;
    }
  }

  /**
   * Get detailed cost breakdown for a specific request
   */
  async getRequestCostBreakdown(requestId) {
    try {
      const response = await this.apiClient.request(`/user/cost-breakdown/${requestId}`, {
        method: 'GET',
      });
      return response;
    } catch (error) {
      console.error('Error fetching cost breakdown:', error);
      throw error;
    }
  }

  /**
   * Format cost for display
   */
  formatCost(cost, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    }).format(cost);
  }

  /**
   * Format data size for display
   */
  formatDataSize(sizeInMB) {
    if (sizeInMB < 1) {
      return `${(sizeInMB * 1024).toFixed(1)} KB`;
    } else if (sizeInMB < 1024) {
      return `${sizeInMB.toFixed(1)} MB`;
    } else {
      return `${(sizeInMB / 1024).toFixed(2)} GB`;
    }
  }

  /**
   * Get tier color for UI
   */
  getTierColor(tier) {
    const colors = {
      free: 'text-gray-600',
      basic: 'text-blue-600',
      premium: 'text-purple-600',
      enterprise: 'text-gold-600'
    };
    return colors[tier] || 'text-gray-600';
  }

  /**
   * Get tier badge background color
   */
  getTierBadgeColor(tier) {
    const colors = {
      free: 'bg-gray-100 text-gray-800',
      basic: 'bg-blue-100 text-blue-800',
      premium: 'bg-purple-100 text-purple-800',
      enterprise: 'bg-yellow-100 text-yellow-800'
    };
    return colors[tier] || 'bg-gray-100 text-gray-800';
  }

  /**
   * Calculate savings from upgrading tiers
   */
  calculateSavings(currentTier, targetTier, monthlyRequests) {
    const tierPricing = {
      free: { baseCost: 0, volumeDiscount: 0 },
      basic: { baseCost: 0.05, volumeDiscount: 0 },
      premium: { baseCost: 0.03, volumeDiscount: 0.4 },
      enterprise: { baseCost: 0.02, volumeDiscount: 0.6 }
    };

    const currentCost = monthlyRequests * tierPricing[currentTier]?.baseCost || 0;
    const targetCost = monthlyRequests * tierPricing[targetTier]?.baseCost || 0;
    
    return Math.max(0, currentCost - targetCost);
  }
}

export default CostTracker;