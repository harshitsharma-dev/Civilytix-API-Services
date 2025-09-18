// src/components/LocationSearch.jsx
import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Search, MapPin } from "lucide-react";

const LocationSearch = ({ onLocationSelect, requestType }) => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Debounce search to avoid too many API calls
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query.length > 2) {
        searchLocations(query);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const searchLocations = async (searchQuery) => {
    setLoading(true);
    try {
      // Using Nominatim (OpenStreetMap) geocoding service - free and no API key required
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          searchQuery
        )}&limit=5&addressdetails=1`
      );

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error("Error searching locations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationClick = (location) => {
    const lat = parseFloat(location.lat);
    const lon = parseFloat(location.lon);

    setQuery(location.display_name);
    setShowSuggestions(false);

    // Call the parent component's callback
    onLocationSelect({ lat, lng: lon });
  };

  const handleManualCoords = () => {
    // Parse manual coordinates like "12.9141, 79.1325" or "lat, lon"
    const coords = query.split(",").map((c) => c.trim());
    if (coords.length === 2) {
      const lat = parseFloat(coords[0]);
      const lon = parseFloat(coords[1]);

      if (
        !isNaN(lat) &&
        !isNaN(lon) &&
        lat >= -90 &&
        lat <= 90 &&
        lon >= -180 &&
        lon <= 180
      ) {
        onLocationSelect({
          lat,
          lng: lon,
          name: `Coordinates (${lat.toFixed(4)}, ${lon.toFixed(4)})`,
        });
        setShowSuggestions(false);
        return;
      }
    }

    // If not manual coords, search for the location
    if (query.length > 2) {
      searchLocations(query);
    }
  };

  return (
    <div className="relative">
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Input
            type="text"
            placeholder={
              requestType === "region"
                ? "Search location or enter lat, lng..."
                : "Search starting location..."
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleManualCoords()}
            className="pr-10"
          />
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        </div>
        <Button
          onClick={handleManualCoords}
          size="sm"
          variant="outline"
          disabled={loading}
        >
          <MapPin className="h-4 w-4 mr-1" />
          Go
        </Button>
      </div>

      {/* Search Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <Card className="absolute top-full left-0 right-0 mt-1 z-50 max-h-60 overflow-y-auto">
          <CardContent className="p-2">
            {suggestions.map((location, index) => (
              <div
                key={index}
                className="p-2 hover:bg-muted cursor-pointer rounded text-sm border-b border-border last:border-b-0"
                onClick={() => handleLocationClick(location)}
              >
                <div className="font-medium text-foreground">
                  {location.display_name.split(",")[0]}
                </div>
                <div className="text-xs text-muted-foreground">
                  {location.display_name}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {parseFloat(location.lat).toFixed(4)},{" "}
                  {parseFloat(location.lon).toFixed(4)}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50">
          <Card>
            <CardContent className="p-4 text-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
              <p className="text-sm text-muted-foreground mt-2">Searching...</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Help text */}
      <div className="text-xs text-muted-foreground mt-2">
        💡 Try: "Mumbai", "Delhi", "Bangalore" or coordinates: "19.0760,
        72.8777" (lat, lng)
      </div>
    </div>
  );
};

export default LocationSearch;
