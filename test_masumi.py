"""
Test Masumi Network Integration
Verifies all services are running and accessible
"""

import requests
import sys

def test_masumi_services():
    """Test all Masumi services"""
    
    print("🧪 Testing Masumi Network Services...\n")
    
    services = {
        'Payment Service (Docs)': 'http://localhost:3001/docs',
        'Payment Service (Admin)': 'http://localhost:3001/admin',
        'Registry Service (Docs)': 'http://localhost:3000/docs',
    }
    
    all_healthy = True
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: UP ({url})")
            else:
                print(f"⚠️  {name}: STATUS {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: DOWN - {e}")
            all_healthy = False
    
    print("\n" + "="*60)
    if all_healthy:
        print("✅ All Masumi services are running successfully!")
        print("\n📖 Access Points:")
        print("   • Payment API Docs: http://localhost:3001/docs")
        print("   • Payment Admin:    http://localhost:3001/admin")
        print("   • Registry API:     http://localhost:3000/docs")
        print("\n🔗 Masumi Documentation: https://docs.masumi.network")
        return True
    else:
        print("❌ Some services are not responding")
        print("\n🔧 Try:")
        print("   cd masumi")
        print("   docker compose down")
        print("   docker compose up -d")
        return False

if __name__ == '__main__':
    success = test_masumi_services()
    sys.exit(0 if success else 1)
