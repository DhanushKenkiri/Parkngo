"""
Security Guard Agent
Monitors active parking sessions and detects violations
Uses Gemini AI for anomaly detection
"""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from services import firebase_service, gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityGuardAgent:
    """
    Monitors parking sessions for:
    - Overstay violations (exceeding reserved time)
    - Unauthorized parking (no reservation)
    - Anomalous behavior (detected by Gemini AI)
    
    Runs as background worker checking every 30 seconds
    """
    
    def __init__(self):
        self.agent_id = "security_guard_001"
        self.agent_name = "Security Guard Agent"
        
        # Monitoring interval (seconds)
        self.check_interval = 30
        
        # Grace period before violation (minutes)
        self.grace_period_minutes = 15
        
        logger.info(f"✅ {self.agent_name} initialized")
    
    def monitor_sessions(self) -> Dict[str, Any]:
        """
        Monitor all active parking sessions
        Called periodically by background worker
        
        Returns:
            {
                'active_sessions': int,
                'violations_detected': int,
                'violations': List[...],
                'anomalies': List[...]
            }
        """
        
        logger.info("👮 Monitoring active parking sessions...")
        
        try:
            # Get all active sessions from Firebase
            active_sessions = firebase_service.get_active_sessions()
            
            if not active_sessions:
                logger.info("✅ No active sessions to monitor")
                return {
                    'active_sessions': 0,
                    'violations_detected': 0,
                    'violations': [],
                    'anomalies': []
                }
            
            logger.info(f"📊 Monitoring {len(active_sessions)} active sessions")
            
            violations = []
            anomalies = []
            
            # Check each session
            for session_id, session_data in active_sessions.items():
                # Check for overstay
                overstay_check = self._check_overstay(session_id, session_data)
                if overstay_check.get('is_violation'):
                    violations.append(overstay_check)
                    
                    # Create violation in Firebase
                    self._create_violation(session_id, overstay_check)
                
                # Check for anomalies using Gemini AI
                anomaly_check = self._check_anomalies_with_ai(session_id, session_data)
                if anomaly_check.get('anomaly_detected'):
                    anomalies.append(anomaly_check)
            
            logger.info(f"✅ Monitoring complete: {len(violations)} violations, {len(anomalies)} anomalies")
            
            return {
                'active_sessions': len(active_sessions),
                'violations_detected': len(violations),
                'violations': violations,
                'anomalies': anomalies,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Session monitoring failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    def _check_overstay(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if vehicle has overstayed reserved time"""
        
        try:
            # Get reservation details
            reserved_duration_hours = session_data.get('duration_hours', 1.0)
            start_time_str = session_data.get('start_time')
            
            if not start_time_str:
                return {'is_violation': False}
            
            # Parse start time
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            
            # Calculate expected end time
            expected_end = start_time + timedelta(hours=reserved_duration_hours)
            grace_end = expected_end + timedelta(minutes=self.grace_period_minutes)
            
            now = datetime.utcnow()
            
            # Check if overstayed (past grace period)
            if now > grace_end:
                overstay_minutes = (now - expected_end).total_seconds() / 60
                
                logger.warning(f"⚠️  Overstay detected: Session {session_id} ({overstay_minutes:.0f} min)")
                
                return {
                    'is_violation': True,
                    'violation_type': 'overstay',
                    'session_id': session_id,
                    'spot_id': session_data.get('spot_id'),
                    'user_id': session_data.get('user_id'),
                    'overstay_minutes': round(overstay_minutes, 1),
                    'expected_end': expected_end.isoformat(),
                    'detected_at': now.isoformat()
                }
            
            return {'is_violation': False}
            
        except Exception as e:
            logger.error(f"❌ Overstay check failed for session {session_id}: {e}")
            return {'is_violation': False}
    
    def _check_anomalies_with_ai(
        self, 
        session_id: str, 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Gemini AI to detect parking anomalies"""
        
        logger.info(f"🧠 Checking anomalies with Gemini AI for session: {session_id}")
        
        # Get historical patterns (simulate for now)
        historical_patterns = {
            'avg_duration_hours': 2.5,
            'typical_entry_times': ['08:00-10:00', '17:00-19:00'],
            'user_history': {
                'total_sessions': 10,
                'avg_payment': 1.5,
                'violations': 0
            }
        }
        
        try:
            anomaly_result = gemini_service.detect_parking_anomalies(
                session_data,
                historical_patterns
            )
            
            if anomaly_result.get('anomaly_score', 0) > 70:
                logger.warning(f"⚠️  Anomaly detected: {anomaly_result.get('detected_issues')}")
                
                return {
                    'anomaly_detected': True,
                    'session_id': session_id,
                    'anomaly_score': anomaly_result.get('anomaly_score'),
                    'issues': anomaly_result.get('detected_issues', []),
                    'recommendation': anomaly_result.get('recommendation'),
                    'ai_reasoning': anomaly_result.get('reasoning')
                }
            
            return {'anomaly_detected': False}
            
        except Exception as e:
            logger.error(f"❌ Gemini anomaly detection failed: {e}")
            
            # Fallback: basic anomaly check
            return self._fallback_anomaly_check(session_data)
    
    def _fallback_anomaly_check(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback anomaly detection when Gemini is unavailable"""
        
        # Simple rule: flag very long sessions (>12 hours)
        duration = session_data.get('duration_hours', 0)
        
        if duration > 12:
            return {
                'anomaly_detected': True,
                'session_id': session_data.get('session_id'),
                'anomaly_score': 80,
                'issues': ['unusually_long_duration'],
                'recommendation': 'Verify with user',
                'ai_reasoning': 'Rule-based check (Gemini unavailable)'
            }
        
        return {'anomaly_detected': False}
    
    def _create_violation(self, session_id: str, violation_data: Dict[str, Any]):
        """Create violation record in Firebase"""
        
        try:
            violation_record = {
                'session_id': session_id,
                'violation_type': violation_data.get('violation_type'),
                'spot_id': violation_data.get('spot_id'),
                'user_id': violation_data.get('user_id'),
                'details': {
                    'overstay_minutes': violation_data.get('overstay_minutes'),
                    'expected_end': violation_data.get('expected_end')
                },
                'status': 'pending_review',
                'created_at': datetime.utcnow().isoformat(),
                'fine_amount_lovelace': self._calculate_fine(violation_data)
            }
            
            result = firebase_service.create_violation(violation_record)
            
            logger.info(f"✅ Violation created: {result.get('violation_id')}")
            
            # In production: send notification to user
            
        except Exception as e:
            logger.error(f"❌ Failed to create violation: {e}")
    
    def _calculate_fine(self, violation_data: Dict[str, Any]) -> int:
        """Calculate fine amount for violation"""
        
        overstay_minutes = violation_data.get('overstay_minutes', 0)
        
        # Fine structure: 0.1 ADA per 30 minutes overstay
        fine_ada = (overstay_minutes / 30) * 0.1
        
        from services import masumi_service
        return masumi_service.ada_to_lovelace(fine_ada)
    
    def start_monitoring(self):
        """
        Start continuous monitoring loop
        Runs in background checking sessions every 30 seconds
        """
        
        logger.info(f"🚀 Starting continuous monitoring (interval: {self.check_interval}s)")
        
        try:
            while True:
                result = self.monitor_sessions()
                
                logger.info(
                    f"📊 Monitor cycle: {result.get('active_sessions', 0)} sessions, "
                    f"{result.get('violations_detected', 0)} violations"
                )
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring loop crashed: {e}")
            import traceback
            traceback.print_exc()


# Singleton instance
security_guard_agent = SecurityGuardAgent()
