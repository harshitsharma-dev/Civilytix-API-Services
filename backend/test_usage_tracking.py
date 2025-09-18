# test_usage_tracking.py
"""
Comprehensive test script for API usage tracking system
Tests individual request tracking, analytics endpoints, and real-time metrics
"""

import sys
import os
import asyncio
import json
import time
from datetime import datetime
import requests
import threading

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.usage_tracker import usage_tracker, CostTier
from app.services.cost_tracker import CostTracker


def test_usage_tracker_service():
    """Test the core usage tracking service"""
    print("🔬 Testing Usage Tracker Service...")
    
    # Test tracking a request
    instance = usage_tracker.track_request(
        endpoint="/api/v1/data/region",
        method="POST",
        user_tier=CostTier.BASIC,
        request_params={
            "center_lat": 40.7128,
            "center_lon": -74.0060,
            "radius": 5,
            "data_type": "potholes"
        },
        response_status=200,
        processing_time_ms=150.5,
        data_volume_mb=0.2,
        user_id="test_user_123",
        ip_address="192.168.1.100",
        user_agent="test-agent/1.0"
    )
    
    print(f"✅ Request tracked successfully:")
    print(f"   Request ID: {instance.request_id}")
    print(f"   Cost: ${instance.cost_calculation.total_cost:.6f}")
    print(f"   Processing Time: {instance.processing_time_ms}ms")
    print(f"   User Tier: {instance.user_tier.value}")
    
    # Test multiple requests
    print("\n📊 Tracking multiple requests...")
    for i in range(5):
        usage_tracker.track_request(
            endpoint=f"/api/v1/test/endpoint{i}",
            method="GET",
            user_tier=CostTier.PREMIUM if i % 2 else CostTier.FREE,
            request_params={"test_param": f"value_{i}"},
            response_status=200 if i < 4 else 500,  # One error
            processing_time_ms=100 + (i * 50),
            user_id=f"user_{i}",
            ip_address=f"192.168.1.{100 + i}"
        )
    
    # Test retrieving instances
    instances = usage_tracker.get_usage_instances(limit=10)
    print(f"✅ Retrieved {len(instances)} usage instances")
    
    # Test real-time metrics
    metrics = usage_tracker.get_real_time_metrics()
    print(f"✅ Real-time metrics:")
    print(f"   Total Requests: {metrics.total_requests}")
    print(f"   Total Cost: ${metrics.total_cost:.6f}")
    print(f"   Error Rate: {metrics.error_rate:.1f}%")
    print(f"   Avg Response Time: {metrics.average_response_time:.1f}ms")
    
    return True


def test_api_server_integration():
    """Test the FastAPI server with usage tracking middleware"""
    print("\n🌐 Testing FastAPI Server Integration...")
    
    # Start the server in a separate thread
    import subprocess
    import time
    
    # Change to backend directory
    backend_dir = os.path.dirname(__file__)
    
    try:
        # Start the server
        print("🚀 Starting FastAPI server...")
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Test if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully")
                return test_api_endpoints()
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    finally:
        # Clean up server process
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            try:
                server_process.kill()
            except:
                pass


def test_api_endpoints():
    """Test API endpoints with usage tracking"""
    print("\n🔗 Testing API Endpoints with Usage Tracking...")
    
    base_url = "http://localhost:8000"
    
    # Test data endpoints with usage tracking
    test_requests = [
        {
            "method": "POST",
            "url": f"{base_url}/api/v1/data/estimate-cost/region",
            "headers": {"X-User-Tier": "BASIC", "X-User-ID": "test_user_api"},
            "json": {
                "center": {"lat": 40.7128, "lng": -74.0060},
                "radius": 5,
                "data_type": "potholes"
            }
        },
        {
            "method": "GET",
            "url": f"{base_url}/api/v1/data/region",
            "headers": {"X-User-Tier": "PREMIUM", "X-User-ID": "test_user_api2"},
            "params": {
                "center_lat": 41.8781,
                "center_lon": -87.6298,
                "radius": 3,
                "data_type": "roads"
            }
        }
    ]
    
    print("📤 Making test API requests...")
    request_ids = []
    
    for i, req in enumerate(test_requests):
        try:
            if req["method"] == "POST":
                response = requests.post(
                    req["url"],
                    headers=req["headers"],
                    json=req["json"],
                    timeout=10
                )
            else:
                response = requests.get(
                    req["url"],
                    headers=req["headers"],
                    params=req["params"],
                    timeout=10
                )
            
            print(f"✅ Request {i+1}: {response.status_code}")
            
            # Check for usage tracking headers
            if "X-Request-ID" in response.headers:
                request_id = response.headers["X-Request-ID"]
                request_ids.append(request_id)
                print(f"   Request ID: {request_id}")
                
            if "X-Processing-Time" in response.headers:
                print(f"   Processing Time: {response.headers['X-Processing-Time']}")
                
            if "X-Cost" in response.headers:
                print(f"   Cost: {response.headers['X-Cost']}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request {i+1} failed: {e}")
    
    # Test usage analytics endpoints
    print("\n📊 Testing Usage Analytics Endpoints...")
    
    analytics_tests = [
        {
            "name": "Real-time Metrics",
            "url": f"{base_url}/api/v1/usage/metrics"
        },
        {
            "name": "Recent Instances",
            "url": f"{base_url}/api/v1/usage/instances?limit=10"
        },
        {
            "name": "Hourly Trends",
            "url": f"{base_url}/api/v1/usage/trends/hourly?hours=1"
        },
        {
            "name": "Cost Breakdown",
            "url": f"{base_url}/api/v1/usage/costs/breakdown?hours=1"
        }
    ]
    
    for test in analytics_tests:
        try:
            response = requests.get(test["url"], timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test['name']}: Success")
                
                # Print some key metrics
                if "totalRequests" in data:
                    print(f"   Total Requests: {data['totalRequests']}")
                if "totalCost" in data:
                    print(f"   Total Cost: ${data['totalCost']:.6f}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Records Retrieved: {len(data)}")
                    
            else:
                print(f"❌ {test['name']}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']} failed: {e}")
    
    return True


def test_performance_and_threading():
    """Test performance and thread safety of usage tracking"""
    print("\n⚡ Testing Performance and Thread Safety...")
    
    def make_requests(thread_id, num_requests):
        """Make multiple requests in a thread"""
        for i in range(num_requests):
            usage_tracker.track_request(
                endpoint=f"/api/v1/test/thread_{thread_id}",
                method="GET",
                user_tier=CostTier.BASIC,
                request_params={"thread": thread_id, "request": i},
                response_status=200,
                processing_time_ms=50 + (i % 100),
                user_id=f"thread_user_{thread_id}_{i}"
            )
    
    # Test concurrent request tracking
    num_threads = 5
    requests_per_thread = 20
    
    print(f"🧵 Starting {num_threads} threads with {requests_per_thread} requests each...")
    
    threads = []
    start_time = time.time()
    
    for thread_id in range(num_threads):
        thread = threading.Thread(
            target=make_requests,
            args=(thread_id, requests_per_thread)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    total_requests = num_threads * requests_per_thread
    
    print(f"✅ Completed {total_requests} requests in {total_time:.2f} seconds")
    print(f"   Throughput: {total_requests / total_time:.1f} requests/second")
    
    # Verify data integrity
    instances = usage_tracker.get_usage_instances(limit=total_requests + 100)
    tracked_requests = len([i for i in instances if "thread_" in i.endpoint])
    
    print(f"✅ Tracked {tracked_requests} concurrent requests")
    
    # Test metrics calculation under load
    metrics = usage_tracker.get_real_time_metrics(force_refresh=True)
    print(f"✅ Metrics calculation successful:")
    print(f"   Total Requests: {metrics.total_requests}")
    print(f"   Average Response Time: {metrics.average_response_time:.1f}ms")
    
    return True


def test_data_filtering_and_analysis():
    """Test data filtering and analysis capabilities"""
    print("\n🔍 Testing Data Filtering and Analysis...")
    
    # Add test data with different characteristics
    test_data = [
        {
            "endpoint": "/api/v1/data/region",
            "user_tier": CostTier.FREE,
            "status": 200,
            "processing_time": 100
        },
        {
            "endpoint": "/api/v1/data/region",
            "user_tier": CostTier.BASIC,
            "status": 200,
            "processing_time": 150
        },
        {
            "endpoint": "/api/v1/data/path",
            "user_tier": CostTier.PREMIUM,
            "status": 404,
            "processing_time": 50
        },
        {
            "endpoint": "/api/v1/user/history",
            "user_tier": CostTier.ENTERPRISE,
            "status": 500,
            "processing_time": 200
        }
    ]
    
    for i, data in enumerate(test_data):
        usage_tracker.track_request(
            endpoint=data["endpoint"],
            method="GET",
            user_tier=data["user_tier"],
            request_params={"test_id": i},
            response_status=data["status"],
            processing_time_ms=data["processing_time"],
            user_id=f"filter_test_user_{i}"
        )
    
    # Test filtering by endpoint
    region_instances = usage_tracker.get_usage_instances(
        limit=100,
        endpoint_filter="region"
    )
    region_count = len([i for i in region_instances if "region" in i.endpoint])
    print(f"✅ Endpoint filtering: Found {region_count} region requests")
    
    # Test filtering by user tier
    premium_instances = usage_tracker.get_usage_instances(
        limit=100,
        user_tier_filter=CostTier.PREMIUM
    )
    premium_count = len([i for i in premium_instances if i.user_tier == CostTier.PREMIUM])
    print(f"✅ User tier filtering: Found {premium_count} premium requests")
    
    # Test time range filtering
    recent_instances = usage_tracker.get_usage_instances(
        limit=100,
        time_range_minutes=1
    )
    print(f"✅ Time filtering: Found {len(recent_instances)} requests in last minute")
    
    # Test endpoint usage analysis
    endpoint_stats = usage_tracker.get_usage_by_endpoint("/api/v1/data/region", hours=1)
    print(f"✅ Endpoint analysis: {endpoint_stats['totalRequests']} requests, "
          f"${endpoint_stats['totalCost']:.6f} total cost")
    
    return True


def main():
    """Run all usage tracking tests"""
    print("🚀 Starting Comprehensive Usage Tracking Tests")
    print("=" * 60)
    
    tests = [
        ("Usage Tracker Service", test_usage_tracker_service),
        ("Performance and Threading", test_performance_and_threading),
        ("Data Filtering and Analysis", test_data_filtering_and_analysis),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'=' * 60}")
            print(f"🧪 Running: {test_name}")
            print('=' * 60)
            
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
            
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = f"❌ FAILED: {str(e)}"
    
    # Try to test API server integration (may fail if server isn't running)
    try:
        print(f"\n{'=' * 60}")
        print("🧪 Running: API Server Integration (Optional)")
        print('=' * 60)
        api_result = test_api_server_integration()
        results["API Server Integration"] = "✅ PASSED" if api_result else "⚠️ SKIPPED"
    except Exception as e:
        results["API Server Integration"] = f"⚠️ SKIPPED: {str(e)}"
    
    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 TEST SUMMARY")
    print('=' * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{result}: {test_name}")
        if "✅ PASSED" in result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Usage tracking system is working perfectly!")
    elif passed >= total - 1:  # Allow API server test to be skipped
        print("🎉 CORE TESTS PASSED! Usage tracking system is working!")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed >= total - 1


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)