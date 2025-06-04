#!/usr/bin/env python3
"""
Dashboard API Test Script
Test the dashboard API endpoints to ensure everything is working
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5050"

def test_endpoint(endpoint, description):
    """Test a single API endpoint"""
    print(f"🧪 Testing {description}...")
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description} - Success")
            if isinstance(data, dict) and 'error' in data:
                print(f"   ⚠️ API Error: {data['error']}")
            else:
                # Show some basic info about the response
                if isinstance(data, list):
                    print(f"   📊 Returned {len(data)} items")
                elif isinstance(data, dict):
                    print(f"   📊 Returned {len(data)} keys: {list(data.keys())[:5]}")
            return True
        else:
            print(f"❌ {description} - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print("🚀 AIA Analytics Dashboard API Test")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test endpoints
    endpoints = [
        ("/api/dashboard-overview", "Dashboard Overview"),
        ("/api/conversations", "Conversations List"),
        ("/api/agents", "Agents Performance"),
        ("/api/sentiment-trends", "Sentiment Trends"),
        ("/api/product-insights", "Product Insights")
    ]
    
    results = []
    for endpoint, description in endpoints:
        success = test_endpoint(endpoint, description)
        results.append((description, success))
        time.sleep(1)  # Brief pause between requests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
    
    print(f"\n🎯 Overall: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All API endpoints are working correctly!")
        print("🌐 Dashboard is ready at: http://127.0.0.1:5050")
    else:
        print("⚠️ Some endpoints have issues. Check the logs above.")
    
    print("\n💡 Next Steps:")
    print("   1. Open http://127.0.0.1:5050 in your browser")
    print("   2. Navigate through the dashboard")
    print("   3. Test the AI analysis features")
    print("   4. Generate reports and insights")

if __name__ == "__main__":
    main()
