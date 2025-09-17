#!/usr/bin/env python3
"""
Test script to validate usage tracking integration with running server
"""

import requests
import time
import json
from datetime import datetime

def test_server_integration():
    """Test the usage tracking system with live server"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Usage Tracking Integration with Live Server")
    print("=" * 60)
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Server is running: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Test usage tracking endpoints
    endpoints_to_test = [
        "/usage/metrics",
        "/usage/instances",
        "/usage/analytics/endpoints",
        "/usage/analytics/trends/hourly",
        "/usage/analytics/costs/breakdown",
        "/usage/analytics/errors/analysis"
    ]
    
    print("\n📊 Testing Usage Analytics Endpoints:")
    print("-" * 40)
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"  {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/usage/metrics":
                    print(f"    📈 Total requests: {data.get('total_requests', 'N/A')}")
                    print(f"    💰 Total cost: ${data.get('total_cost', 0):.4f}")
                elif endpoint == "/usage/instances":
                    instances = data.get('instances', [])
                    print(f"    📋 Usage instances: {len(instances)}")
                
        except requests.exceptions.RequestException as e:
            print(f"  {endpoint}: ❌ Error - {e}")
    
    # Test making some API calls to generate usage data
    print("\n🧪 Making test API calls to generate usage data:")
    print("-" * 50)
    
    test_calls = [
        {"endpoint": "/health", "method": "GET"},
        {"endpoint": "/docs", "method": "GET"},
    ]
    
    for test_call in test_calls:
        try:
            if test_call["method"] == "GET":
                response = requests.get(f"{base_url}{test_call['endpoint']}", timeout=5)
            
            print(f"  ✅ {test_call['method']} {test_call['endpoint']}: {response.status_code}")
            
            # Check if usage tracking headers are present
            if 'X-Request-ID' in response.headers:
                print(f"    🆔 Request ID: {response.headers['X-Request-ID']}")
            if 'X-Processing-Time-MS' in response.headers:
                print(f"    ⏱️  Processing time: {response.headers['X-Processing-Time-MS']}ms")
            if 'X-Request-Cost' in response.headers:
                print(f"    💰 Request cost: ${response.headers['X-Request-Cost']}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {test_call['method']} {test_call['endpoint']}: Error - {e}")
    
    # Check usage metrics again to see if they updated
    print("\n📊 Checking updated usage metrics:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/usage/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  📈 Updated total requests: {data.get('total_requests', 'N/A')}")
            print(f"  💰 Updated total cost: ${data.get('total_cost', 0):.4f}")
            print(f"  ⚡ Average response time: {data.get('average_response_time', 0):.2f}ms")
            print(f"  📊 Error rate: {data.get('error_rate', 0)*100:.1f}%")
            
            print(f"\n  📋 Requests by tier:")
            for tier, count in data.get('requests_by_tier', {}).items():
                print(f"    {tier}: {count} requests")
        else:
            print(f"  ❌ Failed to get metrics: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error getting metrics: {e}")
    
    print("\n🎯 Integration test completed!")
    return True

if __name__ == "__main__":
    test_server_integration()