// src/components/Sidebar.jsx
import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const Sidebar = ({
  user,
  selectedAPI,
  onAPIChange,
  requestType,
  onRequestTypeChange,
  radius,
  onRadiusChange,
  bufferWidth,
  onBufferWidthChange,
  onGetData,
  loading,
}) => {
  return (
    <div className="w-80 bg-background border-r border-border p-4 h-full overflow-y-auto">
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-foreground">Control Panel</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {!user ? (
            <p className="text-muted-foreground">
              Please login to access controls
            </p>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="api-select">Select API</Label>
                <Select value={selectedAPI} onValueChange={onAPIChange}>
                  <SelectTrigger id="api-select">
                    <SelectValue placeholder="Select an API" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="uhi">Urban Heat Island</SelectItem>
                    <SelectItem value="potholes">Pothole Detection</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label>Request Method</Label>
                <div className="flex flex-col space-y-2">
                  <div className="flex items-center space-x-2">
                    <input
                      id="region-radio"
                      type="radio"
                      value="region"
                      checked={requestType === "region"}
                      onChange={(e) => onRequestTypeChange(e.target.value)}
                      className="h-4 w-4 border-border"
                    />
                    <Label
                      htmlFor="region-radio"
                      className="text-sm font-normal cursor-pointer"
                    >
                      By Region
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      id="path-radio"
                      type="radio"
                      value="path"
                      checked={requestType === "path"}
                      onChange={(e) => onRequestTypeChange(e.target.value)}
                      className="h-4 w-4 border-border"
                    />
                    <Label
                      htmlFor="path-radio"
                      className="text-sm font-normal cursor-pointer"
                    >
                      By Path
                    </Label>
                  </div>
                </div>
              </div>

              {requestType === "region" && (
                <div className="space-y-2">
                  <Label htmlFor="radius-slider">Radius (km): {radius}</Label>
                  <input
                    id="radius-slider"
                    type="range"
                    min="1"
                    max="10"
                    value={radius}
                    onChange={(e) => onRadiusChange(Number(e.target.value))}
                    className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
              )}

              {requestType === "path" && (
                <div className="space-y-2">
                  <Label htmlFor="buffer-width">Buffer Width (meters)</Label>
                  <Input
                    id="buffer-width"
                    type="number"
                    value={bufferWidth}
                    onChange={(e) =>
                      onBufferWidthChange(Number(e.target.value))
                    }
                    min="50"
                    max="1000"
                    step="50"
                  />
                </div>
              )}

              <Button
                onClick={onGetData}
                disabled={loading}
                className="w-full"
                size="lg"
              >
                {loading ? "Processing..." : "Get Data"}
              </Button>

              <Card className="bg-muted/50">
                <CardContent className="pt-4">
                  <div className="text-xs text-muted-foreground">
                    <p className="font-medium mb-2">Instructions:</p>
                    <ul className="space-y-1">
                      <li>• Click on map to set center (Region mode)</li>
                      <li>• Click twice to set path (Path mode)</li>
                      <li>• Adjust parameters using controls above</li>
                      <li>• Click "Get Data" to fetch results</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Sidebar;
