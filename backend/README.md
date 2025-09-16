# Civilytix API Services - Backend

A structured FastAPI backend for geospatial data retrieval and analysis, supporting potholes and urban heat island (UHI) data.

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configuration and settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── data_routes.py     # Data retrieval endpoints
│   │   └── user_routes.py     # User management endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication service
│   │   ├── database.py       # MongoDB operations
│   │   ├── geospatial.py     # Geospatial data processing
│   │   └── storage.py        # Google Cloud Storage
│   └── utils/
│       └── __init__.py
├── main.py                   # FastAPI application
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB Atlas account (or local MongoDB)
- Google Cloud Storage bucket (optional, for file storage)

### Installation

1. **Clone and navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the backend directory:

   ```env
   # MongoDB Configuration
   MONGO_USERNAME=your_username
   MONGO_PASSWORD=your_password
   MONGO_CLUSTER_ADDRESS=cluster0.xxxxx.mongodb.net
   MONGO_DATABASE_NAME=civilytix_db

   # Google Cloud Storage (Optional)
   GCS_BUCKET_NAME=your-bucket-name
   GCS_PROJECT_ID=your-project-id

   # Application Settings
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000

   # Data Paths
   POTHOLES_DATA_PATH=/path/to/your/potholes.geojson
   ```

5. **Run the application:**

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📚 API Documentation

Once running, visit:

- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🔑 Authentication

The API uses API key authentication via the `X-API-Key` header.

**Default API Keys:**

- `user1_secret_token` (basic user)
- `user2_another_token` (basic user)
- `user3_paid_token` (paid user - required for data access)

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/region" \
  -H "X-API-Key: user3_paid_token" \
  -H "Content-Type: application/json" \
  -d '{
    "center": {"lat": 12.9141, "lon": 79.1325},
    "radius_km": 5.0,
    "dataType": "potholes"
  }'
```

## 🛠️ API Endpoints

### Data Endpoints

#### `POST /api/v1/data/region`

Retrieve geospatial data for a circular region.

**Request Body:**

```json
{
  "center": { "lat": 12.9141, "lon": 79.1325 },
  "radius_km": 5.0,
  "dataType": "potholes"
}
```

#### `POST /api/v1/data/path`

Retrieve geospatial data along a path with buffer.

**Request Body:**

```json
{
  "start_coords": { "lat": 12.9141, "lon": 79.1325 },
  "end_coords": { "lat": 12.92, "lon": 79.14 },
  "buffer_meters": 100.0,
  "dataType": "potholes"
}
```

### User Endpoints

#### `GET /api/v1/user/history`

Get user's request history.

#### `GET /api/v1/user/history/{request_id}`

Get download URL for a specific request.

#### `GET /api/v1/user/profile`

Get user profile information.

#### `GET /api/v1/user/stats`

Get user usage statistics.

## 🗄️ Database Schema

### User Document

```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "paymentStatus": "paid",
  "api_key": "user3_paid_token",
  "created_at": "2024-01-01T00:00:00Z",
  "requestHistory": [
    {
      "requestId": "uuid-string",
      "timestamp": "2024-01-01T12:00:00Z",
      "endpoint": "/api/v1/data/region",
      "requestParams": {...},
      "resultUrl": "https://storage.googleapis.com/..."
    }
  ]
}
```

## 🌍 Data Types

### Potholes Data

- **Format:** GeoJSON FeatureCollection
- **Geometry:** Point features with coordinates
- **Processing:** Spatial filtering by distance or buffer

### UHI (Urban Heat Island) Data

- **Format:** Currently placeholder JSON (extend for TIFF/raster data)
- **Processing:** Spatial analysis for temperature data

## ☁️ Cloud Storage

Files are stored in Google Cloud Storage with the following structure:

```
your-bucket/
└── results/
    └── user_{api_key}/
        ├── {request_id}_potholes_region.geojson
        ├── {request_id}_potholes_path.geojson
        ├── {request_id}_uhi_region.json
        └── {request_id}_uhi_path.json
```

## 🔧 Configuration

### Environment Variables

| Variable                | Description                   | Default                         |
| ----------------------- | ----------------------------- | ------------------------------- |
| `MONGO_USERNAME`        | MongoDB username              | `uname`                         |
| `MONGO_PASSWORD`        | MongoDB password              | `pwd`                           |
| `MONGO_CLUSTER_ADDRESS` | MongoDB cluster address       | `cluster0.gv45ccj.mongodb.net`  |
| `MONGO_DATABASE_NAME`   | Database name                 | `civilytix_db`                  |
| `GCS_BUCKET_NAME`       | Google Cloud Storage bucket   | `civilytix-data-bucket`         |
| `GCS_PROJECT_ID`        | Google Cloud project ID       | `None`                          |
| `DEBUG`                 | Enable debug mode             | `False`                         |
| `HOST`                  | Server host                   | `0.0.0.0`                       |
| `PORT`                  | Server port                   | `8000`                          |
| `POTHOLES_DATA_PATH`    | Path to potholes GeoJSON file | `/data/global_potholes.geojson` |

## 🚀 Deployment

### Docker Deployment

1. **Create Dockerfile:**

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["python", "main.py"]
   ```

2. **Build and run:**
   ```bash
   docker build -t civilytix-api .
   docker run -p 8000:8000 --env-file .env civilytix-api
   ```

### Production Considerations

1. **Security:**

   - Use secure API key management
   - Implement rate limiting
   - Enable HTTPS
   - Restrict CORS origins

2. **Performance:**

   - Use connection pooling for MongoDB
   - Implement caching for frequently accessed data
   - Use async processing for large datasets

3. **Monitoring:**
   - Add logging configuration
   - Implement health checks
   - Monitor API performance

## 🧪 Testing

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Region data request
curl -X POST "http://localhost:8000/api/v1/data/region" \
  -H "X-API-Key: user3_paid_token" \
  -H "Content-Type: application/json" \
  -d '{
    "center": {"lat": 12.9141, "lon": 79.1325},
    "radius_km": 5.0,
    "dataType": "potholes"
  }'

# User history
curl -X GET "http://localhost:8000/api/v1/user/history" \
  -H "X-API-Key: user3_paid_token"
```

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed:**

   - Check MongoDB credentials and cluster address
   - Ensure IP whitelist includes your server IP
   - Verify network connectivity

2. **Potholes Data Not Found:**

   - Check `POTHOLES_DATA_PATH` environment variable
   - Ensure GeoJSON file exists and is properly formatted
   - Verify file permissions

3. **Google Cloud Storage Errors:**

   - Verify GCS credentials are properly configured
   - Check bucket permissions
   - Ensure bucket exists and is accessible

4. **API Key Authentication Failed:**
   - Verify `X-API-Key` header is included
   - Check API key value matches configured keys
   - Ensure user exists in database with correct payment status

## 📝 Migration from Notebook

This structured backend was created from the original `API.ipynb` notebook with the following improvements:

1. **Separation of Concerns:** Code organized into logical modules
2. **Error Handling:** Comprehensive error handling and logging
3. **Configuration Management:** Environment-based configuration
4. **Scalability:** Modular design for easy extension
5. **Documentation:** Comprehensive API documentation
6. **Production Ready:** Health checks, CORS, and deployment considerations

## 🤝 Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Update documentation for new features
4. Test thoroughly before deployment

## 📄 License

[Add your license information here]
