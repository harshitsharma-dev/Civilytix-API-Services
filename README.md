## Backend Setup

The backend is a FastAPI service for geospatial data. Before running, ensure you have:

- **Python 3.11** (required; see `backend/requirements.txt` for version pinning)
- **NumPy <2.0.0** (pinned in requirements for compatibility with geospatial libraries)

**To set up the backend:**

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. See `backend/README.md` for environment variables, running, and API usage details.

---

## Installation

1. Make sure you have [Node.js](https://nodejs.org/) and [npm](https://www.npmjs.com/) installed.
2. Clone the repository:
   ```
   git clone https://github.com/your-username/Civilytix-API-Services.git
   ```
3. Navigate to the project directory:
   ```
   cd Civilytix-API-Services
   ```
4. Install dependencies:
   ```
   npm install
   ```

## Starting the Project

To start the development server with Vite, run:

```
npm run dev
```

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
