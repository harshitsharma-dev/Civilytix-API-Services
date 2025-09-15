#!/usr/bin/env python3
"""
Database initialization script for Civilytix API Services.
Creates sample users and sets up initial data.
"""

import os
import sys
from datetime import datetime
from bson.objectid import ObjectId

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.services.database import db_service


def create_sample_users():
    """Create sample users for testing."""
    sample_users = [
        {
            "email": "user1@example.com",
            "paymentStatus": "unpaid",
            "api_key": "user1_secret_token",
            "created_at": datetime.utcnow(),
            "requestHistory": []
        },
        {
            "email": "user2@example.com", 
            "paymentStatus": "unpaid",
            "api_key": "user2_another_token",
            "created_at": datetime.utcnow(),
            "requestHistory": []
        },
        {
            "email": "paid_user@example.com",
            "paymentStatus": "paid",
            "api_key": "user3_paid_token",
            "created_at": datetime.utcnow(),
            "requestHistory": []
        }
    ]
    
    for user_data in sample_users:
        # Check if user already exists
        existing_user = db_service.get_user_by_api_key(user_data["api_key"])
        if existing_user:
            print(f"User with API key {user_data['api_key']} already exists, skipping...")
            continue
            
        # Create user
        user_id = db_service.create_user(user_data)
        if user_id:
            print(f"Created user: {user_data['email']} (ID: {user_id})")
        else:
            print(f"Failed to create user: {user_data['email']}")


def main():
    """Main initialization function."""
    print("Initializing Civilytix API Services database...")
    
    # Connect to database
    try:
        db_service.connect()
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        sys.exit(1)
    
    # Create sample users
    try:
        create_sample_users()
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)
    finally:
        db_service.disconnect()


if __name__ == "__main__":
    main()