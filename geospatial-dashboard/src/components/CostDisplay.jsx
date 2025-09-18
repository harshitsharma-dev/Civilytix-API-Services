// src/components/CostDisplay.jsx
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  DollarSign, 
  TrendingUp, 
  Calculator, 
  AlertCircle,
  Info,
  Zap
} from "lucide-react";

const CostDisplay = ({ 
  costTracker, 
  requestType, 
  requestParams, 
  user,
  onUpgrade 
}) => {
  const [costEstimate, setCostEstimate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (requestParams && requestType && user) {
      estimateCost();
    }
  }, [requestParams, requestType, user]);

  const estimateCost = async () => {
    if (!requestParams || !requestType) return;

    setLoading(true);
    setError(null);

    try {
      let estimate;
      
      if (requestType === 'region' && requestParams.center && requestParams.radius) {
        estimate = await costTracker.estimateRegionCost(
          requestParams.center,
          requestParams.radius,
          requestParams.dataType || 'potholes'
        );
      } else if (requestType === 'path' && requestParams.startCoords && requestParams.endCoords) {
        estimate = await costTracker.estimatePathCost(
          requestParams.startCoords,
          requestParams.endCoords,
          requestParams.bufferWidth || 100,
          requestParams.dataType || 'potholes'
        );
      }

      setCostEstimate(estimate);
    } catch (err) {
      console.error('Error estimating cost:', err);
      setError('Unable to estimate cost. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderCostBreakdown = () => {
    if (!costEstimate?.costBreakdown) return null;

    const { costBreakdown } = costEstimate;

    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Base Cost:</span>
            <span className="font-medium">
              {costTracker.formatCost(costBreakdown.baseCost)}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-muted-foreground">Data Volume:</span>
            <span className="font-medium">
              {costTracker.formatCost(costBreakdown.dataVolumeCost)}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-muted-foreground">Processing:</span>
            <span className="font-medium">
              {costTracker.formatCost(costBreakdown.processingCost)}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-muted-foreground">Storage:</span>
            <span className="font-medium">
              {costTracker.formatCost(costBreakdown.storageCost)}
            </span>
          </div>
        </div>
        
        <div className="border-t pt-3">
          <div className="flex justify-between text-lg font-bold">
            <span>Total Cost:</span>
            <span className="text-green-600">
              {costTracker.formatCost(costBreakdown.totalCost)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const renderEstimateInfo = () => {
    if (!costEstimate) return null;

    return (
      <div className="space-y-2 text-sm text-muted-foreground">
        <div className="flex items-center justify-between">
          <span>Data Type:</span>
          <span className="capitalize font-medium">{costEstimate.dataType}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span>User Tier:</span>
          <span className={`px-2 py-1 rounded-md text-xs font-medium ${costTracker.getTierBadgeColor(costEstimate.userTier)}`}>
            {costEstimate.userTier.toUpperCase()}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span>Estimated Size:</span>
          <span className="font-medium">
            {costTracker.formatDataSize(costEstimate.estimatedDataSizeMb)}
          </span>
        </div>
        
        {costEstimate.coverageAreaKm2 && (
          <div className="flex items-center justify-between">
            <span>Coverage Area:</span>
            <span className="font-medium">{costEstimate.coverageAreaKm2.toFixed(1)} km²</span>
          </div>
        )}
        
        {costEstimate.pathLengthKm && (
          <div className="flex items-center justify-between">
            <span>Path Length:</span>
            <span className="font-medium">{costEstimate.pathLengthKm.toFixed(1)} km</span>
          </div>
        )}
      </div>
    );
  };

  const getTierUpgradeMessage = () => {
    if (!costEstimate) return null;
    
    const currentTier = costEstimate.userTier;
    
    if (currentTier === 'free') {
      return (
        <Alert>
          <TrendingUp className="h-4 w-4" />
          <AlertDescription>
            Upgrade to Basic to start making API requests. Current estimate is for Basic tier pricing.
          </AlertDescription>
        </Alert>
      );
    }
    
    if (currentTier === 'basic') {
      const savings = costTracker.calculateSavings('basic', 'premium', 100);
      return (
        <Alert>
          <Zap className="h-4 w-4" />
          <AlertDescription>
            Upgrade to Premium for 40% savings on high-volume usage. Save up to {costTracker.formatCost(savings)} per month!
          </AlertDescription>
        </Alert>
      );
    }
    
    return null;
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="w-5 h-5" />
            Calculating Cost...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            Cost Estimation Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button 
            onClick={estimateCost} 
            variant="outline" 
            className="mt-3"
          >
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!costEstimate) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            Cost Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Set your request parameters to see cost estimation.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-green-600" />
          Cost Estimate
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {renderCostBreakdown()}
        
        <div className="border-t pt-4">
          {renderEstimateInfo()}
        </div>
        
        {getTierUpgradeMessage() && (
          <div className="pt-2">
            {getTierUpgradeMessage()}
            {costEstimate.userTier === 'free' && (
              <Button 
                onClick={onUpgrade} 
                className="w-full mt-2"
              >
                Upgrade Now
              </Button>
            )}
          </div>
        )}
        
        <div className="text-xs text-muted-foreground text-center">
          * Prices shown in {costEstimate.costBreakdown?.currency || 'USD'}. 
          Final costs may vary based on actual data size and processing requirements.
        </div>
      </CardContent>
    </Card>
  );
};

export default CostDisplay;