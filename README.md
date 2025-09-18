# 🌍 Civilytix API Services

A comprehensive geospatial data analysis platform with premium user authentication, featuring real-time pothole detection and urban heat island monitoring.

## 📋 Table of Contents

- [🌍 Civilytix API Services](#-civilytix-api-services)
  - [📋 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [📦 Installation](#-installation)
    - [Prerequisites](#prerequisites)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
  - [⚙️ Configuration](#️-configuration)
    - [Environment Variables](#environment-variables)
    - [Google Cloud Setup](#google-cloud-setup)
    - [MongoDB Atlas Setup](#mongodb-atlas-setup)
  - [🚀 Running the Application](#-running-the-application)
    - [Development Mode](#development-mode)
    - [Production Mode](#production-mode)
  - [🔐 Authentication System](#-authentication-system)
    - [Demo Users](#demo-users)
  - [📡 API Endpoints](#-api-endpoints)
    - [User Authentication](#user-authentication)
    - [Geospatial Data](#geospatial-data)
  - [🗺️ Frontend Features](#️-frontend-features)
  - [📊 Data Models](#-data-models)
  - [🧪 Testing](#-testing)
  - [🚀 Deployment](#-deployment)
  - [📝 License](#-license)
  - [🤝 Contributing](#-contributing)

## 🚀 Features

### Core Features

- **🗺️ Interactive Geospatial Dashboard** - Leaflet-based mapping with real-time data visualization
- **🔐 Premium Authentication System** - Email-based login with API key authentication
- **💳 Tiered Access Control** - Free and premium user tiers with feature restrictions
- **📍 Location Search** - Support for both location names and coordinate input
- **🕳️ Pothole Detection** - Real-time pothole monitoring and analysis
- **🌡️ Urban Heat Island Analysis** - Environmental data visualization
- **📱 Responsive Design** - Mobile-friendly interface with modern UI components

### Technical Features

- **⚡ FastAPI Backend** - High-performance Python API with automatic documentation
- **🌐 React Frontend** - Modern React application with Tailwind CSS
- **🗄️ Dual Database Architecture** - MongoDB Atlas for geospatial data, Google Cloud Storage for user data
- **🔑 API Key Authentication** - Secure API access with role-based permissions
- **📊 RESTful API Design** - Clean, documented API endpoints
- **🧪 Environment Configuration** - Flexible setup for development and production

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │───▶│   FastAPI       │───▶│   MongoDB       │
│   Dashboard     │    │   Backend       │    │   Atlas         │
│                 │    │                 │    │  (Geospatial)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │  Google Cloud   │
         └──────────────│   Storage       │
                        │ (User Data)     │
                        └─────────────────┘
```

## 📦 Installation

### Prerequisites

- **Node.js** (v16+ recommended)
- **Python** (v3.8+ recommended)
- **MongoDB Atlas** account
- **Google Cloud Platform** account

### Backend Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/harshitsharma-dev/Civilytix-API-Services.git
   cd Civilytix-API-Services/backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd ../geospatial-dashboard
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# MongoDB Atlas Configuration
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_password
MONGO_CLUSTER_ADDRESS=your_cluster.mongodb.net
MONGO_DATABASE_NAME=civilytix_db
MONGO_APP_NAME=Cluster0

# Google Cloud Storage
GCS_BUCKET_NAME=civilytix-data-bucket
GCS_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Google Cloud Setup

1. **Create a Google Cloud Project:**

   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project

2. **Enable APIs:**

   - Cloud Storage API
   - Service Account API

3. **Create Service Account:**

   - Go to IAM & Admin → Service Accounts
   - Create service account with Storage Admin role
   - Download JSON key file

4. **Create Storage Bucket:**
   ```bash
   gsutil mb gs://civilytix-data-bucket
   ```

### MongoDB Atlas Setup

1. **Create MongoDB Atlas Account:**

   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Create a new cluster

2. **Configure Database Access:**

   - Create database user
   - Whitelist IP addresses

3. **Get Connection String:**
   - Copy connection string from Atlas dashboard

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**

```bash
cd backend
python main.py
# API will be available at http://localhost:8000
```

**Terminal 2 - Frontend:**

```bash
cd geospatial-dashboard
npm run dev
# Dashboard will be available at http://localhost:5173
```

### Production Mode

**Backend:**

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**

```bash
cd geospatial-dashboard
npm run build
npm run preview
```

## 🔐 Authentication System

The platform uses a tiered authentication system:

- **🆓 Free Users:** Map access only
- **💰 Premium Users:** Full feature access including data analysis tools

### Demo Users

Pre-configured users for testing:

**Premium Users:**

- `premium1@example.com` - Alice Premium
- `premium2@example.com` - Bob Premium
- `premium3@example.com` - Charlie Premium

**Free Users:**

- `free1@example.com` - David Free
- `free2@example.com` - Jane Free

## 📡 API Endpoints

### User Authentication

```http
POST /api/v1/user/login
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "user_id": "user_premium_001",
  "email": "premium1@example.com",
  "full_name": "Alice Premium",
  "subscription_status": "premium",
  "created_at": "2024-01-01T00:00:00Z",
  "api_key": "premium_user_key_001"
}
```

### Geospatial Data

```http
POST /api/v1/data/region
X-API-Key: your_api_key
Content-Type: application/json

{
  "center": {"lat": 40.7128, "lon": -74.0060},
  "radius_km": 5.0,
  "dataType": "potholes"
}
```

## 🗺️ Frontend Features

### Dashboard Components

- **🗺️ MapComponent:** Interactive Leaflet map with marker clustering
- **🔍 LocationSearch:** Smart search supporting locations and coordinates
- **📊 Sidebar:** Control panel with request configuration
- **🔐 LoginModal:** User authentication interface
- **💳 PaymentModal:** Premium upgrade interface
- **📱 Responsive Design:** Mobile-optimized layout

### Search Functionality

The location search supports multiple input formats:

- **Location Names:** "Mumbai", "New York", "London"
- **Coordinates:** "19.0760, 72.8777" (lat, lng format)
- **Natural Language:** "Central Park, NYC"

## 📊 Data Models

### User Profile

```python
{
  "user_id": str,
  "email": str,
  "full_name": str,
  "subscription_status": str,  # "free" | "premium"
  "created_at": str,
  "api_key": str
}
```

### Geospatial Request

```python
{
  "center": {"lat": float, "lon": float},
  "radius_km": float,
  "dataType": str  # "potholes" | "uhi"
}
```

## 🧪 Testing

**API Testing:**

```bash
cd backend
python -m pytest tests/
```

**Frontend Testing:**

```bash
cd geospatial-dashboard
npm run test
```

## 🚀 Deployment

### Backend Deployment (Railway/Heroku)

1. **Configure environment variables**
2. **Set up MongoDB Atlas connection**
3. **Configure Google Cloud Storage**
4. **Deploy using platform-specific commands**

### Frontend Deployment (Vercel/Netlify)

1. **Build the application:**

   ```bash
   npm run build
   ```

2. **Deploy to hosting platform**
3. **Configure environment variables**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with ❤️ by the Civilytix Team**

For questions or support, please open an issue or contact us at support@civilytix.com

Google Maps API Setup
Create a Google Cloud Project

Go to Google Cloud Console
Create a new project or select an existing one
Enable Required APIs

Navigate to "APIs & Services" → "Library"
Enable the following APIs:
Maps JavaScript API
Directions API
Create API Credentials

Go to "APIs & Services" → "Credentials"
Click "Create Credentials" → "API Key"
Copy the generated API key
Configure API Restrictions (Recommended)

Click on your API key to edit
Under "Application restrictions", select "HTTP referrers"
Add your domains:
http://localhost:5173/_ (for development)
https://your-domain.com/_ (for production)
Enable Billing (Required for Directions API)

Go to "Billing" in Google Cloud Console
Add a payment method (Google provides $200/month free credit)