// src/components/CostAnalytics.jsx
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  DollarSign,
  Database,
  Activity,
  AlertTriangle
} from "lucide-react";

const CostAnalytics = ({ costTracker, user }) => {
  const [costSummary, setCostSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user && costTracker) {
      loadCostSummary();
    }
  }, [user, costTracker, selectedPeriod]);

  const loadCostSummary = async () => {
    setLoading(true);
    setError(null);

    try {
      const summary = await costTracker.getCostSummary(parseInt(selectedPeriod));
      setCostSummary(summary);
    } catch (err) {
      console.error('Error loading cost summary:', err);
      setError('Unable to load cost analytics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderUsageLimits = () => {
    if (!costSummary?.currentMonthUsage) return null;

    const usage = costSummary.currentMonthUsage;
    const requestsPercentage = usage.requestsLimit > 0 
      ? (usage.requestsUsed / usage.requestsLimit) * 100 
      : 0;
    const dataPercentage = usage.dataLimitMb > 0 
      ? (usage.dataUsedMb / usage.dataLimitMb) * 100 
      : 0;

    const getUsageColor = (percentage) => {
      if (percentage >= 90) return 'text-red-600 bg-red-100';
      if (percentage >= 75) return 'text-yellow-600 bg-yellow-100';
      return 'text-green-600 bg-green-100';
    };

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Current Month Usage
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>API Requests</span>
              <span className="font-medium">
                {usage.requestsUsed} / {usage.requestsLimit > 0 ? usage.requestsLimit : '∞'}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  requestsPercentage >= 90 ? 'bg-red-500' :
                  requestsPercentage >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(requestsPercentage, 100)}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Data Volume</span>
              <span className="font-medium">
                {costTracker.formatDataSize(usage.dataUsedMb)} / {
                  usage.dataLimitMb > 0 
                    ? costTracker.formatDataSize(usage.dataLimitMb) 
                    : '∞'
                }
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${
                  dataPercentage >= 90 ? 'bg-red-500' :
                  dataPercentage >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(dataPercentage, 100)}%` }}
              ></div>
            </div>
          </div>

          {usage.warnings && usage.warnings.length > 0 && (
            <div className="space-y-2">
              {usage.warnings.map((warning, index) => (
                <div key={index} className="flex items-center gap-2 text-sm text-yellow-600 bg-yellow-50 p-2 rounded">
                  <AlertTriangle className="w-4 h-4" />
                  {warning}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderCostBreakdown = () => {
    if (!costSummary?.usageSummary) return null;

    const summary = costSummary.usageSummary;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Cost Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {costTracker.formatCost(summary.totalCost)}
              </div>
              <div className="text-sm text-muted-foreground">Total Cost</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {summary.totalRequests}
              </div>
              <div className="text-sm text-muted-foreground">Total Requests</div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Cost by Endpoint</h4>
            <div className="space-y-2">
              {Object.entries(summary.costByEndpoint || {}).map(([endpoint, cost]) => (
                <div key={endpoint} className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{endpoint}</span>
                  <span className="font-medium">{costTracker.formatCost(cost)}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Cost by Data Type</h4>
            <div className="space-y-2">
              {Object.entries(summary.costByDataType || {}).map(([dataType, cost]) => (
                <div key={dataType} className="flex justify-between text-sm">
                  <span className="text-muted-foreground capitalize">{dataType}</span>
                  <span className="font-medium">{costTracker.formatCost(cost)}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t">
            <span className="text-sm text-muted-foreground">Data Volume:</span>
            <span className="font-medium">{summary.dataVolumeGb.toFixed(2)} GB</span>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderProjections = () => {
    if (!costSummary) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Cost Projections
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-xl font-bold text-purple-600">
                {costTracker.formatCost(costSummary.projectedMonthlyCost)}
              </div>
              <div className="text-sm text-muted-foreground">
                Projected Monthly Cost
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Based on {selectedPeriod} day average
              </div>
            </div>
          </div>

          <div className="text-sm text-muted-foreground">
            <div className="flex justify-between mb-2">
              <span>Current Tier:</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${costTracker.getTierBadgeColor(costSummary.userTier)}`}>
                {costSummary.userTier.toUpperCase()}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span>Period:</span>
              <span className="font-medium">{costSummary.summaryPeriod}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5" />
          <h2 className="text-xl font-bold">Cost Analytics</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse space-y-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5" />
          <h2 className="text-xl font-bold">Cost Analytics</h2>
        </div>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-red-600 mb-4">{error}</div>
            <Button onClick={loadCostSummary}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          <h2 className="text-xl font-bold">Cost Analytics</h2>
        </div>
        
        <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">7 days</SelectItem>
            <SelectItem value="30">30 days</SelectItem>
            <SelectItem value="90">90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {renderUsageLimits()}
        {renderCostBreakdown()}
        {renderProjections()}
      </div>
    </div>
  );
};

export default CostAnalytics;