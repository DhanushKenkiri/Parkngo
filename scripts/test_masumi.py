"""
Test Masumi Network Services
Verifies Masumi Payment and Registry services are running
"""

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_masumi_services():
    """Test connectivity to Masumi services"""
    
    logger.info("🔍 Testing Masumi Network services...")
    
    results = {
        'payment_service': False,
        'registry_service': False
    }
    
    # Test Payment Service
    try:
        response = requests.get('http://localhost:3001/docs', timeout=5)
        results['payment_service'] = response.status_code == 200
        
        if results['payment_service']:
            logger.info("✅ Payment Service: UP (http://localhost:3001)")
        else:
            logger.error(f"❌ Payment Service: DOWN (status {response.status_code})")
            
    except Exception as e:
        logger.error(f"❌ Payment Service: ERROR - {e}")
    
    # Test Registry Service
    try:
        response = requests.get('http://localhost:3000/docs', timeout=5)
        results['registry_service'] = response.status_code == 200
        
        if results['registry_service']:
            logger.info("✅ Registry Service: UP (http://localhost:3000)")
        else:
            logger.error(f"❌ Registry Service: DOWN (status {response.status_code})")
            
    except Exception as e:
        logger.error(f"❌ Registry Service: ERROR - {e}")
    
    # Summary
    if all(results.values()):
        logger.info("\n🎉 All Masumi services are running!")
        logger.info("   Payment Service Docs: http://localhost:3001/docs")
        logger.info("   Payment Admin Panel: http://localhost:3001/admin")
        logger.info("   Registry Service Docs: http://localhost:3000/docs")
        return True
    else:
        logger.error("\n❌ Some services are not running. Check Docker: docker compose ps")
        return False


if __name__ == '__main__':
    import sys
    success = test_masumi_services()
    sys.exit(0 if success else 1)
