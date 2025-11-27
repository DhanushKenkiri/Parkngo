"""
Dispute Resolver Agent
Uses Gemini AI for intelligent dispute investigation and resolution
Manages bilateral escrow on Masumi Network
"""

import logging
import hashlib
from typing import Dict, Any, List
from datetime import datetime

from services import firebase_service, gemini_service, masumi_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DisputeResolverAgent:
    """
    Resolves parking disputes using:
    - Gemini AI for evidence analysis and arbitration
    - Masumi bilateral escrow for fund management
    - Firebase for dispute record keeping
    
    Dispute types:
    - Incorrect charges
    - Faulty equipment
    - Unfair violations
    - Payment issues
    """
    
    def __init__(self):
        self.agent_id = "dispute_resolver_001"
        self.agent_name = "Dispute Resolver Agent"
        
        # Arbitration fee (ADA)
        self.arbitration_fee = 0.5
        
        logger.info(f"✅ {self.agent_name} initialized")
    
    def create_dispute(self, dispute_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new dispute case
        
        Args:
            dispute_data: {
                'user_id': str,
                'session_id': str,
                'dispute_type': str,
                'description': str,
                'evidence': List[str],
                'disputed_amount_lovelace': int
            }
        
        Returns:
            {
                'dispute_id': str,
                'escrow_id': str,
                'status': str,
                'investigation_started': bool
            }
        """
        
        logger.info(f"📋 Creating dispute for user: {dispute_data.get('user_id')}")
        
        try:
            # Step 1: Create dispute record in Firebase
            dispute_record = {
                'user_id': dispute_data.get('user_id'),
                'session_id': dispute_data.get('session_id'),
                'dispute_type': dispute_data.get('dispute_type'),
                'description': dispute_data.get('description'),
                'evidence': dispute_data.get('evidence', []),
                'disputed_amount_lovelace': dispute_data.get('disputed_amount_lovelace'),
                'status': 'under_investigation',
                'created_at': datetime.utcnow().isoformat(),
                'arbitrator': self.agent_name
            }
            
            firebase_result = firebase_service.create_dispute(dispute_record)
            dispute_id = firebase_result.get('dispute_id')
            
            logger.info(f"✅ Dispute created: {dispute_id}")
            
            # Step 2: Create bilateral escrow on Masumi
            escrow_result = self._create_bilateral_escrow(dispute_data, dispute_id)
            
            # Step 3: Start AI investigation
            investigation_result = self._investigate_with_ai(dispute_data)
            
            return {
                'success': True,
                'dispute_id': dispute_id,
                'escrow_id': escrow_result.get('escrow_id'),
                'status': 'under_investigation',
                'investigation_started': True,
                'estimated_resolution_hours': 24,
                'ai_initial_assessment': investigation_result.get('initial_assessment')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create dispute: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_bilateral_escrow(
        self, 
        dispute_data: Dict[str, Any], 
        dispute_id: str
    ) -> Dict[str, Any]:
        """Create bilateral escrow on Masumi Network"""
        
        logger.info("🔒 Creating bilateral escrow on Masumi...")
        
        escrow_data = {
            'party_a': {
                'name': 'Customer',
                'wallet': dispute_data.get('user_wallet'),
                'stake_lovelace': dispute_data.get('disputed_amount_lovelace')
            },
            'party_b': {
                'name': 'ParknGo Operator',
                'wallet': 'operator_wallet_address',
                'stake_lovelace': dispute_data.get('disputed_amount_lovelace')
            },
            'arbiter': {
                'name': self.agent_name,
                'wallet': 'arbiter_wallet_address',
                'fee_lovelace': masumi_service.ada_to_lovelace(self.arbitration_fee)
            },
            'metadata': {
                'dispute_id': dispute_id,
                'dispute_type': dispute_data.get('dispute_type'),
                'created_at': datetime.utcnow().isoformat()
            }
        }
        
        try:
            escrow_result = masumi_service.create_bilateral_escrow(escrow_data)
            
            if escrow_result.get('success'):
                logger.info(f"✅ Bilateral escrow created: {escrow_result.get('escrow_id')}")
            else:
                logger.warning(f"⚠️  Escrow creation skipped: {escrow_result.get('error')}")
            
            return escrow_result
            
        except Exception as e:
            logger.error(f"❌ Bilateral escrow failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _investigate_with_ai(self, dispute_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini AI to investigate dispute"""
        
        logger.info("🧠 Starting AI investigation with Gemini...")
        
        try:
            investigation = gemini_service.investigate_dispute(
                dispute_data,
                dispute_data.get('evidence', [])
            )
            
            logger.info(
                f"✅ Investigation complete: {investigation.get('ruling')} "
                f"(confidence: {investigation.get('confidence')}%)"
            )
            
            return {
                'initial_assessment': investigation.get('reasoning', '')[:200],
                'full_investigation': investigation
            }
            
        except Exception as e:
            logger.error(f"❌ AI investigation failed: {e}")
            
            return {
                'initial_assessment': 'Investigation in progress (AI analysis pending)',
                'full_investigation': None
            }
    
    def resolve_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """
        Resolve dispute using Gemini AI arbitration
        Distributes funds via Masumi bilateral escrow
        
        Args:
            dispute_id: Firebase dispute ID
        
        Returns:
            {
                'ruling': str (customer_wins | operator_wins | split),
                'confidence': int (0-100),
                'payout_distribution': {...},
                'reasoning': str
            }
        """
        
        logger.info(f"⚖️  Resolving dispute: {dispute_id}")
        
        try:
            # Step 1: Get dispute data from Firebase
            # (In production, query Firebase for dispute by ID)
            dispute_data = {
                'dispute_id': dispute_id,
                'user_id': 'user_123',
                'dispute_type': 'incorrect_charge',
                'description': 'Charged for 3 hours but only parked 2 hours',
                'evidence': ['parking_receipt.jpg', 'timestamp_photo.jpg'],
                'disputed_amount_lovelace': masumi_service.ada_to_lovelace(0.5)
            }
            
            # Step 2: Use Gemini AI for final ruling
            ruling = gemini_service.investigate_dispute(
                dispute_data,
                dispute_data.get('evidence', [])
            )
            
            # Step 3: Resolve bilateral escrow on Masumi
            escrow_resolution = self._resolve_escrow(dispute_id, ruling)
            
            # Step 4: Update dispute status in Firebase
            # (In production, update Firebase dispute record)
            
            logger.info(
                f"✅ Dispute resolved: {ruling.get('ruling')} "
                f"(confidence: {ruling.get('confidence')}%)"
            )
            
            return {
                'success': True,
                'dispute_id': dispute_id,
                'ruling': ruling.get('ruling'),
                'confidence': ruling.get('confidence'),
                'payout_distribution': ruling.get('payout_distribution'),
                'reasoning': ruling.get('reasoning'),
                'escrow_resolution': escrow_resolution,
                'resolved_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Dispute resolution failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _resolve_escrow(
        self, 
        dispute_id: str, 
        ruling: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve bilateral escrow based on AI ruling"""
        
        logger.info("🔓 Resolving bilateral escrow...")
        
        # Map AI ruling to escrow distribution
        escrow_id = f"escrow_{dispute_id}"
        
        try:
            resolution = masumi_service.resolve_bilateral_escrow(
                escrow_id,
                ruling
            )
            
            if resolution.get('success'):
                logger.info(f"✅ Escrow resolved: {ruling.get('ruling')}")
            else:
                logger.warning(f"⚠️  Escrow resolution skipped: {resolution.get('error')}")
            
            return resolution
            
        except Exception as e:
            logger.error(f"❌ Escrow resolution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dispute_status(self, dispute_id: str) -> Dict[str, Any]:
        """Get current status of dispute"""
        
        logger.info(f"📊 Getting dispute status: {dispute_id}")
        
        try:
            # In production, query Firebase for dispute
            # For now, return sample status
            
            return {
                'dispute_id': dispute_id,
                'status': 'under_investigation',
                'created_at': datetime.utcnow().isoformat(),
                'estimated_resolution': '24 hours',
                'updates': [
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'message': 'AI investigation started',
                        'stage': 'evidence_analysis'
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get dispute status: {e}")
            return {
                'error': str(e)
            }
    
    def list_pending_disputes(self) -> List[Dict[str, Any]]:
        """Get all pending disputes for review"""
        
        logger.info("📋 Listing pending disputes...")
        
        try:
            # In production, query Firebase for disputes with status='under_investigation'
            
            return {
                'pending_disputes': [],
                'count': 0,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list disputes: {e}")
            return {
                'error': str(e)
            }


# Singleton instance
dispute_resolver_agent = DisputeResolverAgent()
