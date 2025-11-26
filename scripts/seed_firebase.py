"""
Firebase Database Seeder
Seeds initial parking spot data into Firebase Realtime Database
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.firebase_service import firebase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_firebase():
    """Seed Firebase with initial parking spot data"""
    
    logger.info("🌱 Starting Firebase seeding...")
    
    # Load seed data
    seed_file = Path(__file__).parent.parent / 'firebase-seed-data.json'
    
    if not seed_file.exists():
        logger.error(f"❌ Seed file not found: {seed_file}")
        return False
    
    try:
        with open(seed_file, 'r') as f:
            seed_data = json.load(f)
        
        logger.info(f"📄 Loaded seed data with {len(seed_data.get('parking_spots', {}))} parking spots")
        
        # Import to Firebase
        from firebase_admin import db
        ref = db.reference('/')
        ref.set(seed_data)
        
        logger.info("✅ Firebase seeded successfully!")
        logger.info(f"   - Parking spots: {len(seed_data.get('parking_spots', {}))}")
        logger.info(f"   - Collections created: parking_spots, entries, exits, sessions, reservations, violations, disputes")
        
        # Verify data
        spots = firebase_service.get_all_parking_spots()
        logger.info(f"✅ Verification: Retrieved {len(spots)} parking spots from Firebase")
        
        for spot_id, spot_data in spots.items():
            logger.info(f"   - {spot_id}: {spot_data.get('type')} ({'occupied' if spot_data.get('occupied') else 'available'})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = seed_firebase()
    sys.exit(0 if success else 1)
