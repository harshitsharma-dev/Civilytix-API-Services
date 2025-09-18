#!/usr/bin/env python3
"""
Script to import pothole data from GeoJSON file into MongoDB Atlas
"""

import json
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pathlib import Path
from urllib.parse import quote_plus

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# MongoDB Atlas connection details from .env file
MONGO_USERNAME = os.getenv('MONGO_USERNAME', 'Manav')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'Ommanav@2005')
MONGO_CLUSTER_ADDRESS = os.getenv('MONGO_CLUSTER_ADDRESS', 'civilytix-cluster.uqq26ak.mongodb.net')
MONGO_DATABASE_NAME = os.getenv('MONGO_DATABASE_NAME', 'civilytix_db')

# Properly encode the password for URL
encoded_password = quote_plus(MONGO_PASSWORD)

# Construct MongoDB URI
MONGODB_URI = f"mongodb+srv://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER_ADDRESS}/{MONGO_DATABASE_NAME}?retryWrites=true&w=majority"

DATABASE_NAME = MONGO_DATABASE_NAME
COLLECTION_NAME = 'potholes'

print(f"Connecting to MongoDB cluster: {MONGO_CLUSTER_ADDRESS}")
print(f"Database: {DATABASE_NAME}")
print(f"Collection: {COLLECTION_NAME}")

def load_geojson_data(file_path):
    """Load pothole data from GeoJSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('features', [])
    except Exception as e:
        print(f"Error loading GeoJSON file: {e}")
        return []

def transform_feature_to_document(feature):
    """Transform GeoJSON feature to MongoDB document"""
    properties = feature.get('properties', {})
    geometry = feature.get('geometry', {})
    
    # Create MongoDB document
    document = {
        '_id': properties.get('id'),  # Use pothole ID as document ID
        'id': properties.get('id'),
        'coordinates': {
            'type': 'Point',
            'coordinates': geometry.get('coordinates', [])  # [longitude, latitude]
        },
        'latitude': geometry.get('coordinates', [0, 0])[1],
        'longitude': geometry.get('coordinates', [0, 0])[0],
        'center_x': properties.get('center_x'),
        'center_y': properties.get('center_y'),
        'confidence': properties.get('confidence'),
        'severity': properties.get('severity'),
        'city': properties.get('city'),
        'area': properties.get('area'),
        'timestamp': properties.get('timestamp', '2024-01-01T00:00:00Z'),
        'status': 'active'
    }
    
    return document

def upload_to_mongodb(features):
    """Upload pothole data to MongoDB Atlas"""
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Create geospatial index for location-based queries
        collection.create_index([("coordinates", "2dsphere")])
        
        # Transform and insert documents
        documents = []
        for feature in features:
            document = transform_feature_to_document(feature)
            documents.append(document)
        
        # Insert documents (replace existing if any)
        if documents:
            # Clear existing data first
            result = collection.delete_many({})
            print(f"Deleted {result.deleted_count} existing documents")
            
            # Insert new data
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} pothole records")
            
            # Verify insertion
            total_count = collection.count_documents({})
            print(f"Total documents in collection: {total_count}")
            
            # Show sample document
            sample = collection.find_one()
            print(f"Sample document: {sample}")
            
        client.close()
        return True
        
    except Exception as e:
        print(f"Error uploading to MongoDB: {e}")
        return False

def main():
    """Main function"""
    # Path to GeoJSON file
    geojson_file = Path(__file__).parent / 'data' / 'global_potholes.geojson'
    
    if not geojson_file.exists():
        print(f"GeoJSON file not found: {geojson_file}")
        return
    
    print(f"Loading data from: {geojson_file}")
    features = load_geojson_data(geojson_file)
    
    if not features:
        print("No features found in GeoJSON file")
        return
    
    print(f"Found {len(features)} pothole features")
    
    # Upload to MongoDB
    print("Uploading to MongoDB Atlas...")
    success = upload_to_mongodb(features)
    
    if success:
        print("✅ Successfully uploaded pothole data to MongoDB Atlas!")
    else:
        print("❌ Failed to upload data to MongoDB Atlas")

if __name__ == "__main__":
    main()