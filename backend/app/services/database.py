from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson.objectid import ObjectId
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.config import settings
from app.models.schemas import User, RequestHistoryEntry


class DatabaseService:
    """Service for handling MongoDB operations."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.users_collection: Optional[Collection] = None
        
    def connect(self) -> None:
        """Establish connection to MongoDB with fallback to mock data."""
        try:
            self.client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test the connection with short timeout
            self.client.admin.command('ping')
            self.db = self.client[settings.MONGO_DATABASE_NAME]
            self.users_collection = self.db['users']
            print(f"Successfully connected to MongoDB: {settings.MONGO_DATABASE_NAME}")
            
            # Initialize with test users if collection is empty
            if self.users_collection.count_documents({}) == 0:
                test_users = [
                    {
                        "email": "user1@test.com",
                        "paymentStatus": "paid",
                        "api_key": "user1_secret_token",
                        "requestHistory": []
                    },
                    {
                        "email": "user2@test.com",
                        "paymentStatus": "paid",
                        "api_key": "user2_another_token",
                        "requestHistory": []
                    },
                    {
                        "email": "user3@test.com",
                        "paymentStatus": "paid",
                        "api_key": "user3_paid_token",
                        "requestHistory": []
                    }
                ]
                self.users_collection.insert_many(test_users)
                print("Initialized database with test users")
                
        except Exception as e:
            print(f"MongoDB connection failed, using mock data: {e}")
            # Use mock data as fallback
            self.client = None
            self.db = None
            self.users_collection = None
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by API key."""
        try:
            if self.users_collection is not None:
                user = self.users_collection.find_one({"api_key": api_key})
                return user
            else:
                # Fallback to mock data when DB not available
                mock_users = {
                    "user1_secret_token": {"_id": "user1", "email": "user1@test.com", "paymentStatus": "paid", "api_key": "user1_secret_token", "requestHistory": []},
                    "user2_another_token": {"_id": "user2", "email": "user2@test.com", "paymentStatus": "paid", "api_key": "user2_another_token", "requestHistory": []},
                    "user3_paid_token": {"_id": "user3", "email": "user3@test.com", "paymentStatus": "paid", "api_key": "user3_paid_token", "requestHistory": []}
                }
                return mock_users.get(api_key)
        except Exception as e:
            print(f"Error retrieving user by API key: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email."""
        try:
            user = self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user."""
        try:
            # Add timestamp for user creation
            user_data["created_at"] = datetime.utcnow()
            user_data["requestHistory"] = []
            
            result = self.users_collection.insert_one(user_data)
            print(f"Created user with id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user_payment_status(self, user_id: ObjectId, payment_status: str) -> bool:
        """Update user payment status."""
        try:
            result = self.users_collection.update_one(
                {"_id": user_id},
                {"$set": {"paymentStatus": payment_status, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return False
    
    def add_request_to_history(self, user_id: str, request_entry: Dict[str, Any]) -> bool:
        """Add a request to user's history."""
        try:
            if self.users_collection is not None:
                result = self.users_collection.update_one(
                    {"_id": user_id},
                    {"$push": {"requestHistory": request_entry}}
                )
                return result.modified_count > 0
            else:
                # Mock implementation - just return True for development
                print(f"Mock: Added request {request_entry.get('requestId')} to user {user_id} history")
                return True
        except Exception as e:
            print(f"Error adding request to history: {e}")
            return False
    
    def get_user_request_history(self, user_id: ObjectId) -> List[Dict[str, Any]]:
        """Get user's request history."""
        try:
            user = self.users_collection.find_one(
                {"_id": user_id},
                {"requestHistory": 1}
            )
            return user.get("requestHistory", []) if user else []
        except Exception as e:
            print(f"Error retrieving request history: {e}")
            return []
    
    def find_user_request(self, user_id: ObjectId, request_id: str) -> Optional[Dict[str, Any]]:
        """Find a specific request in user's history."""
        try:
            user = self.users_collection.find_one(
                {"_id": user_id, "requestHistory.requestId": request_id},
                {"requestHistory.$": 1}
            )
            if user and "requestHistory" in user and user["requestHistory"]:
                return user["requestHistory"][0]
            return None
        except Exception as e:
            print(f"Error finding user request: {e}")
            return None
    
    def create_sample_user(self) -> Optional[str]:
        """Create a sample user for testing."""
        sample_user = {
            "email": "user@example.com",
            "paymentStatus": "paid",
            "api_key": "user3_paid_token",
            "requestHistory": []
        }
        return self.create_user(sample_user)


# Global database service instance
db_service = DatabaseService()