"""
ParknGo Multi-Agent Parking System
Flask REST API Server

Integrates all 7 AI agents:
- Orchestrator (master coordinator)
- SpotFinder (Gemini AI spot ranking)
- PricingAgent (Gemini demand forecasting)
- RouteOptimizer (Gemini directions)
- PaymentVerifier (Gemini fraud detection)
- SecurityGuard (Gemini anomaly detection)
- DisputeResolver (Gemini AI arbitration)
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import agents
from agents import (
    orchestrator_agent,
    spot_finder_agent,
    pricing_agent,
    route_optimizer_agent,
    payment_verifier_agent,
    security_guard_agent,
    dispute_resolver_agent
)

# Import services
from services import firebase_service, gemini_service, masumi_service

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PARKING RESERVATION ENDPOINTS
# ============================================================================

@app.route('/api/parking/reserve', methods=['POST'])
def reserve_parking():
    """
    Create a parking reservation
    
    Request body:
    {
        "user_id": "user_123",
        "user_location": {"lat": 40.7128, "lng": -74.0060},
        "vehicle_type": "sedan",
        "desired_features": ["covered", "ev_charging"],
        "duration_hours": 2.5,
        "wallet_address": "addr1..."
    }
    
    Response:
    {
        "success": true,
        "reservation_id": "res_abc123",
        "payment_id": "pay_xyz789",
        "payment_address": "addr1...",
        "amount_lovelace": 1500000,
        "spot_recommendation": {...},
        "pricing": {...},
        "route": {...},
        "expires_at": 1234567890
    }
    """
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'user_location', 'vehicle_type', 'duration_hours', 'wallet_address']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        logger.info(f"📥 Parking reservation request from user: {data.get('user_id')}")
        
        # Delegate to Orchestrator Agent
        result = orchestrator_agent.handle_parking_request(data)
        
        if result.get('success'):
            logger.info(f"✅ Reservation created: {result.get('reservation_id')}")
            return jsonify(result), 200
        else:
            logger.error(f"❌ Reservation failed: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"❌ Error in reserve_parking: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/parking/spots', methods=['GET'])
def get_available_spots():
    """
    Get all available parking spots
    
    Query params:
    - zone: Filter by zone (A, B, C)
    - type: Filter by type (regular, premium, disabled)
    - features: Comma-separated features (covered,ev_charging)
    
    Response:
    {
        "success": true,
        "spots": [...],
        "total_available": 5
    }
    """
    
    try:
        # Get query parameters
        filters = {}
        
        if request.args.get('zone'):
            filters['zone'] = request.args.get('zone')
        
        if request.args.get('type'):
            filters['type'] = request.args.get('type')
        
        if request.args.get('features'):
            filters['features'] = request.args.get('features').split(',')
        
        logger.info(f"📥 Get available spots request with filters: {filters}")
        
        # Query Firebase
        spots = firebase_service.get_available_spots(filters)
        
        return jsonify({
            'success': True,
            'spots': spots,
            'total_available': len(spots) if spots else 0,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting spots: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/parking/price', methods=['POST'])
def calculate_price():
    """
    Calculate price for a parking spot (without reservation)
    
    Request body:
    {
        "spot_id": "A-01",
        "duration_hours": 2.0
    }
    
    Response:
    {
        "success": true,
        "pricing": {...},
        "ai_reasoning": "..."
    }
    """
    
    try:
        data = request.get_json()
        
        spot_id = data.get('spot_id')
        duration_hours = data.get('duration_hours', 1.0)
        
        if not spot_id:
            return jsonify({
                'success': False,
                'error': 'Missing spot_id'
            }), 400
        
        # Get spot data from Firebase
        spot_data = firebase_service.get_spot_by_id(spot_id)
        
        if not spot_data:
            return jsonify({
                'success': False,
                'error': f'Spot {spot_id} not found'
            }), 404
        
        # Calculate price using Pricing Agent
        pricing_result = pricing_agent.calculate_price(
            spot_data,
            {'duration_hours': duration_hours}
        )
        
        return jsonify({
            'success': True,
            'spot_id': spot_id,
            'pricing': pricing_result,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error calculating price: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# PAYMENT ENDPOINTS
# ============================================================================

@app.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    """
    Verify payment on blockchain
    
    Request body:
    {
        "payment_id": "pay_xyz789",
        "payment_address": "addr1..."
    }
    
    Response:
    {
        "verified": true,
        "amount_lovelace": 1500000,
        "tx_hash": "abc123...",
        "fraud_check": {...}
    }
    """
    
    try:
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        payment_address = data.get('payment_address')
        
        if not payment_id or not payment_address:
            return jsonify({
                'success': False,
                'error': 'Missing payment_id or payment_address'
            }), 400
        
        logger.info(f"📥 Payment verification request: {payment_id}")
        
        # Delegate to Payment Verifier Agent
        result = payment_verifier_agent.verify_payment(payment_id, payment_address)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"❌ Error verifying payment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/payment/status/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """
    Get payment status from Masumi Network
    
    Response:
    {
        "payment_id": "pay_xyz789",
        "status": "completed",
        "amount_lovelace": 1500000
    }
    """
    
    try:
        logger.info(f"📥 Payment status request: {payment_id}")
        
        status = masumi_service.get_payment_status(payment_id)
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting payment status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# DISPUTE ENDPOINTS
# ============================================================================

@app.route('/api/disputes/create', methods=['POST'])
def create_dispute():
    """
    Create a new dispute
    
    Request body:
    {
        "user_id": "user_123",
        "session_id": "session_456",
        "dispute_type": "incorrect_charge",
        "description": "Charged for 3 hours but only parked 2 hours",
        "evidence": ["receipt.jpg", "timestamp.jpg"],
        "disputed_amount_lovelace": 500000
    }
    
    Response:
    {
        "success": true,
        "dispute_id": "dispute_789",
        "escrow_id": "escrow_abc",
        "status": "under_investigation"
    }
    """
    
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'session_id', 'dispute_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        logger.info(f"📥 Dispute creation request from user: {data.get('user_id')}")
        
        # Delegate to Dispute Resolver Agent
        result = dispute_resolver_agent.create_dispute(data)
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ Error creating dispute: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/disputes/<dispute_id>', methods=['GET'])
def get_dispute_status(dispute_id):
    """
    Get dispute status
    
    Response:
    {
        "dispute_id": "dispute_789",
        "status": "under_investigation",
        "created_at": "2025-11-27T...",
        "updates": [...]
    }
    """
    
    try:
        logger.info(f"📥 Dispute status request: {dispute_id}")
        
        status = dispute_resolver_agent.get_dispute_status(dispute_id)
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting dispute status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/disputes/<dispute_id>/resolve', methods=['POST'])
def resolve_dispute(dispute_id):
    """
    Resolve a dispute (admin/arbiter only)
    
    Response:
    {
        "success": true,
        "ruling": "customer_wins",
        "confidence": 85,
        "payout_distribution": {...}
    }
    """
    
    try:
        logger.info(f"📥 Dispute resolution request: {dispute_id}")
        
        # Delegate to Dispute Resolver Agent
        result = dispute_resolver_agent.resolve_dispute(dispute_id)
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"❌ Error resolving dispute: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# MONITORING ENDPOINTS
# ============================================================================

@app.route('/api/monitoring/sessions', methods=['GET'])
def monitor_sessions():
    """
    Get current session monitoring status
    
    Response:
    {
        "active_sessions": 5,
        "violations_detected": 1,
        "violations": [...],
        "anomalies": [...]
    }
    """
    
    try:
        logger.info("📥 Session monitoring request")
        
        # Delegate to Security Guard Agent
        result = security_guard_agent.monitor_sessions()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"❌ Error monitoring sessions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/earnings', methods=['GET'])
def get_agent_earnings():
    """
    Get earnings breakdown for all agents
    
    Response:
    {
        "total_earnings_lovelace": 5000000,
        "by_agent": {
            "spot_finder": 1500000,
            "pricing_agent": 1250000,
            ...
        }
    }
    """
    
    try:
        logger.info("📥 Agent earnings request")
        
        # Query Firebase for agent earnings
        earnings_data = firebase_service.db.child('agent_earnings').get()
        
        # Aggregate by agent
        agent_totals = {}
        total = 0
        
        if earnings_data:
            for key, earning in earnings_data.items():
                agent_name = earning.get('agent_name')
                amount = earning.get('amount_lovelace', 0)
                
                if agent_name:
                    agent_totals[agent_name] = agent_totals.get(agent_name, 0) + amount
                    total += amount
        
        return jsonify({
            'success': True,
            'total_earnings_lovelace': total,
            'total_earnings_ada': total / 1_000_000,
            'by_agent': agent_totals,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting agent earnings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Response:
    {
        "status": "healthy",
        "services": {
            "firebase": "connected",
            "gemini": "available",
            "masumi": "healthy"
        },
        "agents": {
            "orchestrator": "ready",
            ...
        }
    }
    """
    
    try:
        # Check service health
        services_status = {
            'firebase': 'connected' if firebase_service.db else 'disconnected',
            'gemini': 'available',  # Gemini doesn't have a health endpoint
            'masumi': 'checking...'
        }
        
        # Check Masumi health
        masumi_health = masumi_service.check_service_health()
        services_status['masumi'] = 'healthy' if masumi_health.get('all_services_up') else 'degraded'
        
        # Check agents
        agents_status = {
            'orchestrator': 'ready',
            'spot_finder': 'ready',
            'pricing_agent': 'ready',
            'route_optimizer': 'ready',
            'payment_verifier': 'ready',
            'security_guard': 'ready',
            'dispute_resolver': 'ready'
        }
        
        all_healthy = all(
            status in ['connected', 'available', 'healthy'] 
            for status in services_status.values()
        )
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'degraded',
            'services': services_status,
            'agents': agents_status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    
    Response:
    {
        "total_spots": 30,
        "available_spots": 15,
        "active_sessions": 5,
        "total_reservations": 100,
        "total_revenue_ada": 150.5
    }
    """
    
    try:
        # Get all spots
        all_spots = firebase_service.get_all_parking_spots()
        available_spots = firebase_service.get_available_spots({})
        active_sessions = firebase_service.get_active_sessions()
        
        return jsonify({
            'success': True,
            'total_spots': len(all_spots) if all_spots else 0,
            'available_spots': len(available_spots) if available_spots else 0,
            'active_sessions': len(active_sessions) if active_sessions else 0,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested resource does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting ParknGo Multi-Agent Parking System API...")
    logger.info("=" * 60)
    logger.info("Agents initialized:")
    logger.info("  ✅ Orchestrator Agent (master coordinator)")
    logger.info("  ✅ SpotFinder Agent (Gemini AI ranking)")
    logger.info("  ✅ PricingAgent (Gemini demand forecasting)")
    logger.info("  ✅ RouteOptimizer Agent (Gemini directions)")
    logger.info("  ✅ PaymentVerifier Agent (Gemini fraud detection)")
    logger.info("  ✅ SecurityGuard Agent (Gemini anomaly detection)")
    logger.info("  ✅ DisputeResolver Agent (Gemini AI arbitration)")
    logger.info("=" * 60)
    
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
