// src/components/UsageDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { usageAPI } from '../services/usageAPI';

const UsageDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [instances, setInstances] = useState([]);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState(24);

  useEffect(() => {
    loadDashboardData();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, selectedTimeRange]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load real-time metrics
      const metricsData = await usageAPI.getMetrics();
      setMetrics(metricsData);
      
      // Load recent instances
      const instancesData = await usageAPI.getInstances({ 
        limit: 50,
        time_range_minutes: 60 
      });
      setInstances(instancesData);
      
      // Load hourly trends
      const trendsData = await usageAPI.getHourlyTrends(selectedTimeRange);
      setTrends(trendsData);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4
    }).format(amount);
  };

  const formatTime = (timeMs) => {
    return `${timeMs.toFixed(1)}ms`;
  };

  const MetricsCard = ({ title, value, subtitle, color = 'blue' }) => (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`h-4 w-4 rounded-full bg-${color}-500`}></div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
      </CardContent>
    </Card>
  );

  if (loading && !metrics) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-300 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">API Usage Dashboard</h1>
        <div className="flex items-center gap-4">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(Number(e.target.value))}
            className="px-3 py-2 border rounded-md"
          >
            <option value={1}>Last Hour</option>
            <option value={6}>Last 6 Hours</option>
            <option value={24}>Last 24 Hours</option>
            <option value={168}>Last Week</option>
          </select>
          <Button
            variant={autoRefresh ? "default" : "outline"}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? "Auto Refresh On" : "Auto Refresh Off"}
          </Button>
          <Button onClick={loadDashboardData} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricsCard
            title="Total Requests"
            value={metrics.totalRequests.toLocaleString()}
            subtitle={`${metrics.requestsPerMinute.toFixed(1)} req/min`}
            color="blue"
          />
          <MetricsCard
            title="Total Cost"
            value={formatCurrency(metrics.totalCost)}
            subtitle={`${formatCurrency(metrics.costPerHour)}/hour`}
            color="green"
          />
          <MetricsCard
            title="Avg Response Time"
            value={formatTime(metrics.averageResponseTime)}
            subtitle="Average processing time"
            color="orange"
          />
          <MetricsCard
            title="Error Rate"
            value={`${metrics.errorRate.toFixed(1)}%`}
            subtitle="4xx and 5xx responses"
            color={metrics.errorRate > 5 ? "red" : "green"}
          />
        </div>
      )}

      {/* Usage Trends Chart */}
      {trends && (
        <Card>
          <CardHeader>
            <CardTitle>Usage Trends - Last {selectedTimeRange} Hours</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Requests by Hour */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Requests by Hour</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {trends.requestsByHour.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="text-sm">{new Date(item.hour).toLocaleTimeString()}</span>
                      <span className="font-medium">{item.requests} requests</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Costs by Hour */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Costs by Hour</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {trends.costByHour.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span className="text-sm">{new Date(item.hour).toLocaleTimeString()}</span>
                      <span className="font-medium">{formatCurrency(item.cost)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Most Used Endpoints */}
      {metrics && metrics.mostUsedEndpoints.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Most Used Endpoints</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics.mostUsedEndpoints.map((endpoint, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">{endpoint.endpoint}</span>
                  <div className="text-right">
                    <div className="font-semibold">{endpoint.count} requests</div>
                    <div className="text-sm text-gray-600">
                      {((endpoint.count / metrics.totalRequests) * 100).toFixed(1)}% of total
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* User Tier Distribution */}
      {metrics && Object.keys(metrics.userTierDistribution).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>User Tier Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(metrics.userTierDistribution).map(([tier, count]) => (
                <div key={tier} className="text-center p-4 bg-gray-50 rounded">
                  <div className="text-2xl font-bold capitalize">{tier}</div>
                  <div className="text-sm text-gray-600">{count} requests</div>
                  <div className="text-xs text-gray-500">
                    {((count / metrics.totalRequests) * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent API Requests */}
      <Card>
        <CardHeader>
          <CardTitle>Recent API Requests (Last Hour)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Time</th>
                  <th className="text-left p-2">Endpoint</th>
                  <th className="text-left p-2">Method</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">Response Time</th>
                  <th className="text-left p-2">User Tier</th>
                  <th className="text-left p-2">Cost</th>
                </tr>
              </thead>
              <tbody>
                {instances.slice(0, 20).map((instance) => (
                  <tr key={instance.requestId} className="border-b hover:bg-gray-50">
                    <td className="p-2">
                      {new Date(instance.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="p-2 font-mono text-xs">{instance.endpoint}</td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        instance.method === 'GET' ? 'bg-blue-100 text-blue-800' :
                        instance.method === 'POST' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {instance.method}
                      </span>
                    </td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        instance.responseStatus < 300 ? 'bg-green-100 text-green-800' :
                        instance.responseStatus < 400 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {instance.responseStatus}
                      </span>
                    </td>
                    <td className="p-2">{formatTime(instance.processingTimeMs)}</td>
                    <td className="p-2 capitalize">{instance.userTier}</td>
                    <td className="p-2 font-medium">
                      {formatCurrency(instance.costCalculation.totalCost)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {instances.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No recent API requests found
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500">
        Last updated: {metrics ? new Date(metrics.lastUpdated).toLocaleString() : 'Loading...'}
        {autoRefresh && ' • Auto-refreshing every 30 seconds'}
      </div>
    </div>
  );
};

export default UsageDashboard;