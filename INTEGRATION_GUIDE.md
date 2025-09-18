# Frontend-Backend Integration Guide

This document explains how to run the Civilytix frontend and backend together for a fully integrated experience.

## Overview

The frontend has been updated to connect to the backend API instead of using dummy data. When users click on "Pothole Detection" or "Urban Heat Island", the frontend will:

1. Send a POST request to the backend API with coordinates and parameters
2. Receive a response with a `downloadUrl` to the processed data
3. Fetch the actual geospatial data from the download URL
4. Display the real latitude/longitude data as markers on the map

## Prerequisites

- Node.js (v16 or higher) for the frontend
- Python 3.8+ for the backend
- MongoDB instance (local or cloud)
- Google Cloud Storage bucket (optional, for file storage)

## Quick Start

### 1. Start the Backend

```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

The backend will start on `http://localhost:8000`

### 2. Start the Frontend

```bash
cd geospatial-dashboard
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

### 3. Test the Integration

1. Open the frontend at `http://localhost:5173`
2. Click "Login" and use any username (demo purposes)
3. Select either "Pothole Detection" or "Urban Heat Island"
4. Choose "Region" or "Path" mode
5. Click on the map to set coordinates
6. Click "Get Data" to fetch real data from the backend

## API Integration Details

### Authentication

- The frontend uses API key authentication via the `X-API-Key` header
- For demo purposes, the login sets `apiKey: "user3_paid_token"`
- This key is configured in the backend's `settings.VALID_API_KEYS`

### Data Flow

#### For Pothole Data:

1. Frontend → Backend: `POST /api/v1/data/region` or `POST /api/v1/data/path`
2. Backend processes request and returns:
   ```json
   {
     "status": "success",
     "message": "Your data is ready for download",
     "requestId": "uuid",
     "downloadUrl": "https://storage.googleapis.com/..."
   }
   ```
3. Frontend fetches data from `downloadUrl`
4. Backend returns GeoJSON format data which is displayed as markers on the map

#### For Urban Heat Island Data:

- Currently returns placeholder data from the backend
- The integration is ready for when real UHI processing is implemented

### Request Format

**Region Request:**

```json
{
  "center": { "lat": 12.9141, "lon": 79.1325 },
  "radius_km": 5.0,
  "dataType": "potholes"
}
```

**Path Request:**

```json
{
  "start_coords": { "lat": 12.9141, "lon": 79.1325 },
  "end_coords": { "lat": 12.92, "lon": 79.14 },
  "buffer_meters": 100.0,
  "dataType": "potholes"
}
```

## Configuration

### Frontend (.env file)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_API_KEY=user3_paid_token
VITE_NODE_ENV=development
VITE_DEBUG=true
```

### Backend (environment variables)

- See `backend/app/core/config.py` for full configuration options
- Key settings: MongoDB URI, GCS bucket, API keys

## Features Implemented

✅ **Real API Integration**: Frontend calls backend endpoints instead of using dummy data
✅ **Authentication**: API key-based authentication
✅ **Geospatial Data**: Real pothole data from GeoJSON files
✅ **Error Handling**: Proper error messages and fallback behavior
✅ **Loading States**: Loading indicators while fetching data
✅ **Map Visualization**: Real coordinates displayed as map markers

## Next Steps

The integration is complete for the core functionality. The AI model mentioned will be separate and can be integrated later by:

1. Adding new endpoints to the backend for AI processing
2. Updating the frontend to call these new endpoints
3. The current data flow will work seamlessly with AI-generated results

## Troubleshooting

### Backend Not Connected

- Ensure backend is running on `http://localhost:8000`
- Check `/health` endpoint for backend status
- Verify MongoDB connection

### Authentication Errors

- Check API key in frontend environment
- Verify API key exists in backend's `VALID_API_KEYS`

### No Data Displayed

- Check browser console for API errors
- Verify GeoJSON data format from backend
- Ensure cloud storage is properly configured for file uploads

## File Changes Made

### Frontend:

- `src/services/api.js`: Added logic to fetch data from download URLs
- `src/App.jsx`: Removed dummy data fallbacks, added proper error handling
- `src/components/LoginModal.jsx`: Updated to use real API keys
- `.env`: Added backend URL and API key configuration

### Backend:

- No changes needed - already had proper API structure
- Uses existing endpoints: `/api/v1/data/region` and `/api/v1/data/path`

The integration is now complete and the frontend will display real geospatial data from the backend API.
