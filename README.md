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
http://localhost:5173/* (for development)
https://your-domain.com/* (for production)
Enable Billing (Required for Directions API)

Go to "Billing" in Google Cloud Console
Add a payment method (Google provides $200/month free credit)
