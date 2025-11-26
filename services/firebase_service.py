"""
ParknGo - Firebase Service Module
Handles all Firebase Realtime Database operations with professional error handling
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirebaseService:
    """Professional Firebase Realtime Database service"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase connection"""
        if not self._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            database_url = os.getenv('FIREBASE_DATABASE_URL')
            
            if not creds_path or not database_url:
                raise ValueError("Missing Firebase configuration in .env file")
            
            # Initialize Firebase
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
            logger.info("✅ Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {e}")
            raise
    
    # ============================================
    # PARKING SPOTS OPERATIONS
    # ============================================
    
    def get_all_parking_spots(self) -> Dict[str, Any]:
        """
        Get all parking spots with their current status
        Returns: Dictionary of spot_id -> spot_data
        """
        try:
            ref = db.reference('parking_spots')
            spots = ref.get()
            
            if not spots:
                logger.warning("No parking spots found in database")
                return {}
            
            logger.info(f"Retrieved {len(spots)} parking spots")
            return spots
            
        except Exception as e:
            logger.error(f"Error fetching parking spots: {e}")
            return {}
    
    def get_available_spots(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all available (unoccupied) parking spots with optional filters
        
        Args:
            filters: Optional dict with keys: zone, type, features
        Returns:
            List of available spot dictionaries
        """
        try:
            all_spots = self.get_all_parking_spots()
            
            # Filter available spots
            available = [
                spot for spot in all_spots.values()
                if not spot.get('occupied', True)
            ]
            
            # Apply additional filters
            if filters:
                if 'zone' in filters:
                    available = [s for s in available if s.get('zone') == filters['zone']]
                
                if 'type' in filters:
                    available = [s for s in available if s.get('type') == filters['type']]
                
                if 'features' in filters:
                    required_features = set(filters['features'])
                    available = [
                        s for s in available 
                        if required_features.issubset(set(s.get('features', [])))
                    ]
            
            logger.info(f"Found {len(available)} available spots (filters: {filters})")
            return available
            
        except Exception as e:
            logger.error(f"Error fetching available spots: {e}")
            return []
    
    def get_spot_by_id(self, spot_id: str) -> Optional[Dict]:
        """
        Get specific parking spot by ID
        
        Args:
            spot_id: Spot identifier (e.g., 'A-01')
        Returns:
            Spot data dictionary or None
        """
        try:
            ref = db.reference(f'parking_spots/{spot_id}')
            spot = ref.get()
            
            if spot:
                logger.info(f"Retrieved spot {spot_id}")
            else:
                logger.warning(f"Spot {spot_id} not found")
            
            return spot
            
        except Exception as e:
            logger.error(f"Error fetching spot {spot_id}: {e}")
            return None
    
    def update_spot_status(self, spot_id: str, occupied: bool) -> bool:
        """
        Update parking spot occupancy status
        
        Args:
            spot_id: Spot identifier
            occupied: True if occupied, False if available
        Returns:
            Success boolean
        """
        try:
            ref = db.reference(f'parking_spots/{spot_id}')
            ref.update({
                'occupied': occupied,
                'last_updated': datetime.utcnow().isoformat() + 'Z'
            })
            
            logger.info(f"Updated {spot_id}: occupied={occupied}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating spot {spot_id}: {e}")
            return False
    
    # ============================================
    # RESERVATIONS OPERATIONS
    # ============================================
    
    def create_reservation(self, reservation_data: Dict) -> Optional[str]:
        """
        Create new parking reservation
        
        Args:
            reservation_data: Reservation details
        Returns:
            Reservation ID or None
        """
        try:
            reservation_id = reservation_data.get('reservation_id')
            ref = db.reference(f'reservations/{reservation_id}')
            
            # Add timestamp
            reservation_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
            reservation_data['status'] = 'confirmed'
            
            ref.set(reservation_data)
            logger.info(f"Created reservation {reservation_id}")
            
            return reservation_id
            
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            return None
    
    def get_reservation(self, reservation_id: str) -> Optional[Dict]:
        """Get reservation by ID"""
        try:
            ref = db.reference(f'reservations/{reservation_id}')
            reservation = ref.get()
            
            if reservation:
                logger.info(f"Retrieved reservation {reservation_id}")
            
            return reservation
            
        except Exception as e:
            logger.error(f"Error fetching reservation {reservation_id}: {e}")
            return None
    
    # ============================================
    # SESSIONS OPERATIONS
    # ============================================
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active parking sessions"""
        try:
            ref = db.reference('sessions')
            all_sessions = ref.get()
            
            if not all_sessions:
                return []
            
            active = [
                session for session in all_sessions.values()
                if session.get('status') == 'active'
            ]
            
            logger.info(f"Found {len(active)} active sessions")
            return active
            
        except Exception as e:
            logger.error(f"Error fetching active sessions: {e}")
            return []
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        try:
            ref = db.reference(f'sessions/{session_id}')
            return ref.get()
            
        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """Update session data"""
        try:
            ref = db.reference(f'sessions/{session_id}')
            ref.update(updates)
            
            logger.info(f"Updated session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    # ============================================
    # VIOLATIONS OPERATIONS
    # ============================================
    
    def create_violation(self, violation_data: Dict) -> Optional[str]:
        """Create new violation"""
        try:
            violation_id = violation_data.get('violation_id')
            ref = db.reference(f'violations/{violation_id}')
            
            violation_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
            violation_data['status'] = 'pending'
            
            ref.set(violation_data)
            logger.info(f"Created violation {violation_id}")
            
            return violation_id
            
        except Exception as e:
            logger.error(f"Error creating violation: {e}")
            return None
    
    def get_violations(self, session_id: Optional[str] = None) -> List[Dict]:
        """Get violations, optionally filtered by session"""
        try:
            ref = db.reference('violations')
            all_violations = ref.get()
            
            if not all_violations:
                return []
            
            violations = list(all_violations.values())
            
            if session_id:
                violations = [v for v in violations if v.get('session_id') == session_id]
            
            logger.info(f"Retrieved {len(violations)} violations")
            return violations
            
        except Exception as e:
            logger.error(f"Error fetching violations: {e}")
            return []
    
    # ============================================
    # DISPUTES OPERATIONS
    # ============================================
    
    def create_dispute(self, dispute_data: Dict) -> Optional[str]:
        """Create new dispute"""
        try:
            dispute_id = dispute_data.get('dispute_id')
            ref = db.reference(f'disputes/{dispute_id}')
            
            dispute_data['created_at'] = datetime.utcnow().isoformat() + 'Z'
            dispute_data['status'] = 'investigating'
            
            ref.set(dispute_data)
            logger.info(f"Created dispute {dispute_id}")
            
            return dispute_id
            
        except Exception as e:
            logger.error(f"Error creating dispute: {e}")
            return None
    
    def update_dispute(self, dispute_id: str, updates: Dict) -> bool:
        """Update dispute data"""
        try:
            ref = db.reference(f'disputes/{dispute_id}')
            ref.update(updates)
            
            logger.info(f"Updated dispute {dispute_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dispute {dispute_id}: {e}")
            return False
    
    def get_dispute(self, dispute_id: str) -> Optional[Dict]:
        """Get dispute by ID"""
        try:
            ref = db.reference(f'disputes/{dispute_id}')
            return ref.get()
            
        except Exception as e:
            logger.error(f"Error fetching dispute {dispute_id}: {e}")
            return None
    
    # ============================================
    # REAL-TIME LISTENERS
    # ============================================
    
    def listen_to_spots(self, callback):
        """
        Setup real-time listener for parking spots changes
        
        Args:
            callback: Function to call when data changes
        """
        try:
            ref = db.reference('parking_spots')
            ref.listen(callback)
            logger.info("✅ Real-time listener setup for parking spots")
            
        except Exception as e:
            logger.error(f"Error setting up spots listener: {e}")
    
    def listen_to_sessions(self, callback):
        """Setup real-time listener for sessions"""
        try:
            ref = db.reference('sessions')
            ref.listen(callback)
            logger.info("✅ Real-time listener setup for sessions")
            
        except Exception as e:
            logger.error(f"Error setting up sessions listener: {e}")


# Singleton instance
firebase_service = FirebaseService()
