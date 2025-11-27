"""
API Testing Script
Tests all endpoints of the ParknGo Multi-Agent Parking System
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_get_stats():
    """Test statistics endpoint"""
    print("\n📊 Testing Get Stats...")
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_get_available_spots():
    """Test get available spots endpoint"""
    print("\n🅿️  Testing Get Available Spots...")
    
    # Test without filters
    response = requests.get(f"{BASE_URL}/parking/spots")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test with filters
    response = requests.get(f"{BASE_URL}/parking/spots?zone=A&features=covered")
    print(f"\nWith filters (zone=A, features=covered):")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_calculate_price():
    """Test price calculation endpoint"""
    print("\n💰 Testing Calculate Price...")
    
    data = {
        "spot_id": "A-01",
        "duration_hours": 2.5
    }
    
    response = requests.post(
        f"{BASE_URL}/parking/price",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_parking_reservation():
    """Test parking reservation endpoint"""
    print("\n🎫 Testing Parking Reservation...")
    
    data = {
        "user_id": "test_user_123",
        "user_location": {"lat": 40.7128, "lng": -74.0060},
        "vehicle_type": "sedan",
        "desired_features": ["covered", "ev_charging"],
        "duration_hours": 2.0,
        "wallet_address": "addr1qytest_wallet_address_here_for_cardano_preprod_network"
    }
    
    response = requests.post(
        f"{BASE_URL}/parking/reserve",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Reservation created!")
        print(f"   Reservation ID: {result.get('reservation_id')}")
        print(f"   Payment ID: {result.get('payment_id')}")
        print(f"   Amount: {result.get('amount_lovelace')} lovelace")
        print(f"   Recommended Spot: {result.get('spot_recommendation', {}).get('spot_id')}")
        
        return result.get('payment_id')
    
    return None

def test_payment_verification(payment_id):
    """Test payment verification endpoint"""
    print("\n🔐 Testing Payment Verification...")
    
    data = {
        "payment_id": payment_id,
        "payment_address": "addr1qytest_payment_address_here"
    }
    
    response = requests.post(
        f"{BASE_URL}/payment/verify",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_payment_status(payment_id):
    """Test payment status endpoint"""
    print("\n📋 Testing Payment Status...")
    
    response = requests.get(f"{BASE_URL}/payment/status/{payment_id}")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_create_dispute():
    """Test dispute creation endpoint"""
    print("\n⚖️  Testing Create Dispute...")
    
    data = {
        "user_id": "test_user_123",
        "session_id": "session_456",
        "dispute_type": "incorrect_charge",
        "description": "I was charged for 3 hours but only parked for 2 hours",
        "evidence": ["parking_receipt.jpg", "timestamp_photo.jpg"],
        "disputed_amount_lovelace": 500000,
        "user_wallet": "addr1qytest_user_wallet"
    }
    
    response = requests.post(
        f"{BASE_URL}/disputes/create",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        result = response.json()
        return result.get('dispute_id')
    
    return None

def test_dispute_status(dispute_id):
    """Test dispute status endpoint"""
    print("\n📊 Testing Dispute Status...")
    
    response = requests.get(f"{BASE_URL}/disputes/{dispute_id}")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_monitor_sessions():
    """Test session monitoring endpoint"""
    print("\n👮 Testing Monitor Sessions...")
    
    response = requests.get(f"{BASE_URL}/monitoring/sessions")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_agent_earnings():
    """Test agent earnings endpoint"""
    print("\n💸 Testing Agent Earnings...")
    
    response = requests.get(f"{BASE_URL}/agents/earnings")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def run_all_tests():
    """Run all API tests"""
    print("=" * 70)
    print("🧪 ParknGo API Testing Suite")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Health Check
    results['health_check'] = test_health_check()
    
    # Test 2: Statistics
    results['stats'] = test_get_stats()
    
    # Test 3: Available Spots
    results['available_spots'] = test_get_available_spots()
    
    # Test 4: Price Calculation
    results['calculate_price'] = test_calculate_price()
    
    # Test 5: Parking Reservation
    payment_id = test_parking_reservation()
    results['parking_reservation'] = payment_id is not None
    
    # Test 6: Payment Verification (if reservation succeeded)
    if payment_id:
        results['payment_verification'] = test_payment_verification(payment_id)
        results['payment_status'] = test_payment_status(payment_id)
    
    # Test 7: Create Dispute
    dispute_id = test_create_dispute()
    results['create_dispute'] = dispute_id is not None
    
    # Test 8: Dispute Status (if dispute created)
    if dispute_id:
        results['dispute_status'] = test_dispute_status(dispute_id)
    
    # Test 9: Monitor Sessions
    results['monitor_sessions'] = test_monitor_sessions()
    
    # Test 10: Agent Earnings
    results['agent_earnings'] = test_agent_earnings()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("=" * 70)

if __name__ == '__main__':
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Make sure the Flask server is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
