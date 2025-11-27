# ParknGo Multi-Agent Parking System API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently no authentication required (add JWT in production)

---

## Endpoints Overview

### Parking Reservations
- `POST /api/parking/reserve` - Create parking reservation
- `GET /api/parking/spots` - Get available parking spots
- `POST /api/parking/price` - Calculate price for a spot

### Payments
- `POST /api/payment/verify` - Verify payment on blockchain
- `GET /api/payment/status/{payment_id}` - Get payment status

### Disputes
- `POST /api/disputes/create` - Create a new dispute
- `GET /api/disputes/{dispute_id}` - Get dispute status
- `POST /api/disputes/{dispute_id}/resolve` - Resolve dispute (admin only)

### Monitoring
- `GET /api/monitoring/sessions` - Get session monitoring status
- `GET /api/agents/earnings` - Get agent earnings breakdown

### System
- `GET /api/health` - Health check
- `GET /api/stats` - System statistics

---

## Detailed Endpoints

### 1. Create Parking Reservation

**Endpoint:** `POST /api/parking/reserve`

**Description:** Creates a parking reservation using the multi-agent system

**Request Body:**
```json
{
  "user_id": "user_123",
  "user_location": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "vehicle_type": "sedan",
  "desired_features": ["covered", "ev_charging"],
  "duration_hours": 2.5,
  "wallet_address": "addr1qy..."
}
```

**Response (200):**
```json
{
  "success": true,
  "reservation_id": "res_abc123",
  "payment_id": "pay_xyz789",
  "payment_address": "addr1qy...",
  "amount_lovelace": 1500000,
  "spot_recommendation": {
    "spot_id": "A-01",
    "zone": "A",
    "type": "premium",
    "features": ["covered", "ev_charging"],
    "distance_meters": 50,
    "ai_score": 95,
    "ai_reasoning": "Closest premium spot with all desired features"
  },
  "pricing": {
    "base_price": 0.75,
    "total_price": 1.5,
    "ai_reasoning": "Pricing adjusted for peak demand",
    "breakdown": {...}
  },
  "route": {
    "distance_meters": 50,
    "walking_time_minutes": 0.6,
    "directions": ["Exit main entrance...", "..."],
    "ai_suggestions": "Take the covered walkway to stay dry"
  },
  "expires_at": 1234567890,
  "instructions": "Send exactly 1.5 ADA to the payment address to confirm"
}
```

---

### 2. Get Available Spots

**Endpoint:** `GET /api/parking/spots`

**Query Parameters:**
- `zone` (optional): Filter by zone (A, B, C)
- `type` (optional): Filter by type (regular, premium, disabled)
- `features` (optional): Comma-separated features (covered,ev_charging)

**Example:**
```
GET /api/parking/spots?zone=A&features=covered
```

**Response (200):**
```json
{
  "success": true,
  "spots": {
    "A-01": {
      "zone": "A",
      "type": "premium",
      "features": ["covered", "ev_charging"],
      "occupied": false,
      "gpio_pin": 17
    }
  },
  "total_available": 5,
  "timestamp": "2025-11-27T12:00:00"
}
```

---

### 3. Calculate Price

**Endpoint:** `POST /api/parking/price`

**Description:** Calculate price using Gemini AI (without creating reservation)

**Request Body:**
```json
{
  "spot_id": "A-01",
  "duration_hours": 2.0
}
```

**Response (200):**
```json
{
  "success": true,
  "spot_id": "A-01",
  "pricing": {
    "base_price": 0.75,
    "total_price": 1.5,
    "demand_multiplier": 1.0,
    "time_multiplier": 1.0,
    "ai_reasoning": "Standard pricing for off-peak hours",
    "breakdown": {...}
  }
}
```

---

### 4. Verify Payment

**Endpoint:** `POST /api/payment/verify`

**Description:** Verify payment on Cardano blockchain using Gemini AI fraud detection

**Request Body:**
```json
{
  "payment_id": "pay_xyz789",
  "payment_address": "addr1qy..."
}
```

**Response (200):**
```json
{
  "verified": true,
  "amount_lovelace": 1500000,
  "tx_hash": "abc123...",
  "confirmations": 3,
  "fraud_check": {
    "fraud_score": 10,
    "risk_level": "low",
    "flags": [],
    "recommend_action": "approve",
    "reasoning": "Low-risk transaction from established wallet"
  },
  "timestamp": "2025-11-27T12:00:00"
}
```

---

### 5. Get Payment Status

**Endpoint:** `GET /api/payment/status/{payment_id}`

**Response (200):**
```json
{
  "payment_id": "pay_xyz789",
  "status": "completed",
  "amount_lovelace": 1500000,
  "success": true
}
```

---

### 6. Create Dispute

**Endpoint:** `POST /api/disputes/create`

**Description:** Create dispute case with Gemini AI investigation

**Request Body:**
```json
{
  "user_id": "user_123",
  "session_id": "session_456",
  "dispute_type": "incorrect_charge",
  "description": "Charged for 3 hours but only parked 2 hours",
  "evidence": ["receipt.jpg", "timestamp.jpg"],
  "disputed_amount_lovelace": 500000,
  "user_wallet": "addr1qy..."
}
```

**Response (200):**
```json
{
  "success": true,
  "dispute_id": "dispute_789",
  "escrow_id": "escrow_abc",
  "status": "under_investigation",
  "investigation_started": true,
  "estimated_resolution_hours": 24,
  "ai_initial_assessment": "Reviewing evidence..."
}
```

---

### 7. Get Dispute Status

**Endpoint:** `GET /api/disputes/{dispute_id}`

**Response (200):**
```json
{
  "dispute_id": "dispute_789",
  "status": "under_investigation",
  "created_at": "2025-11-27T12:00:00",
  "estimated_resolution": "24 hours",
  "updates": [
    {
      "timestamp": "2025-11-27T12:00:00",
      "message": "AI investigation started",
      "stage": "evidence_analysis"
    }
  ]
}
```

---

### 8. Resolve Dispute

**Endpoint:** `POST /api/disputes/{dispute_id}/resolve`

**Description:** Resolve dispute using Gemini AI arbitration (admin only)

**Response (200):**
```json
{
  "success": true,
  "dispute_id": "dispute_789",
  "ruling": "customer_wins",
  "confidence": 85,
  "payout_distribution": {
    "customer_receives": 0.8,
    "operator_receives": 0.2
  },
  "reasoning": "Evidence clearly shows customer was overcharged...",
  "resolved_at": "2025-11-27T13:00:00"
}
```

---

### 9. Monitor Sessions

**Endpoint:** `GET /api/monitoring/sessions`

**Description:** Get current session monitoring using Security Guard agent

**Response (200):**
```json
{
  "active_sessions": 5,
  "violations_detected": 1,
  "violations": [
    {
      "violation_type": "overstay",
      "session_id": "session_123",
      "spot_id": "A-01",
      "overstay_minutes": 45
    }
  ],
  "anomalies": [
    {
      "anomaly_detected": true,
      "session_id": "session_456",
      "anomaly_score": 75,
      "issues": ["unusually_long_duration"],
      "ai_reasoning": "Session duration exceeds normal patterns"
    }
  ],
  "checked_at": "2025-11-27T12:00:00"
}
```

---

### 10. Get Agent Earnings

**Endpoint:** `GET /api/agents/earnings`

**Description:** Get earnings breakdown for all agents

**Response (200):**
```json
{
  "success": true,
  "total_earnings_lovelace": 5000000,
  "total_earnings_ada": 5.0,
  "by_agent": {
    "spot_finder": 1500000,
    "pricing_agent": 1250000,
    "route_optimizer": 1250000,
    "payment_verifier": 1000000
  },
  "timestamp": "2025-11-27T12:00:00"
}
```

---

### 11. Health Check

**Endpoint:** `GET /api/health`

**Response (200):**
```json
{
  "status": "healthy",
  "services": {
    "firebase": "connected",
    "gemini": "available",
    "masumi": "healthy"
  },
  "agents": {
    "orchestrator": "ready",
    "spot_finder": "ready",
    "pricing_agent": "ready",
    "route_optimizer": "ready",
    "payment_verifier": "ready",
    "security_guard": "ready",
    "dispute_resolver": "ready"
  },
  "timestamp": "2025-11-27T12:00:00"
}
```

---

### 12. Get Statistics

**Endpoint:** `GET /api/stats`

**Response (200):**
```json
{
  "success": true,
  "total_spots": 30,
  "available_spots": 15,
  "active_sessions": 5,
  "timestamp": "2025-11-27T12:00:00"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Missing required field: user_id"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Endpoint not found",
  "message": "The requested resource does not exist"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Agent Integration

Each endpoint leverages one or more AI agents:

| Endpoint | Primary Agent | AI Features |
|----------|--------------|-------------|
| `/parking/reserve` | Orchestrator | Gemini aggregation of all sub-agent results |
| `/parking/spots` | SpotFinder | Gemini AI ranking by preferences |
| `/parking/price` | PricingAgent | Gemini demand forecasting, pricing explanation |
| `/payment/verify` | PaymentVerifier | Gemini fraud detection |
| `/monitoring/sessions` | SecurityGuard | Gemini anomaly detection |
| `/disputes/create` | DisputeResolver | Gemini evidence investigation |
| `/disputes/{id}/resolve` | DisputeResolver | Gemini AI arbitration |

---

## Testing

Run the test suite:
```bash
python tests/test_api.py
```

Test individual endpoints:
```bash
# Health check
curl http://localhost:5000/api/health

# Get available spots
curl http://localhost:5000/api/parking/spots

# Create reservation
curl -X POST http://localhost:5000/api/parking/reserve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "user_location": {"lat": 40.7128, "lng": -74.0060},
    "vehicle_type": "sedan",
    "desired_features": ["covered"],
    "duration_hours": 2.0,
    "wallet_address": "addr1qy..."
  }'
```

---

## Production Deployment

### Environment Variables
```bash
FLASK_ENV=production
PORT=5000
FIREBASE_DATABASE_URL=https://...
GEMINI_API_KEY=...
BLOCKFROST_PROJECT_ID=...
MASUMI_PAYMENT_SERVICE_URL=http://localhost:3001
MASUMI_REGISTRY_SERVICE_URL=http://localhost:3000
```

### Run with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```bash
docker build -t parkngo-api .
docker run -p 5000:5000 --env-file .env parkngo-api
```
