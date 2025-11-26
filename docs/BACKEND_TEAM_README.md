# 🔐 Backend Team - Multi-Agent Payment System

**Team Member:** [Your Name]  
**Responsibility:** 7 AI agents + Masumi blockchain payments  
**Timeline:** Week 1-4

---

## 🎯 Your Mission

Build a multi-agent system where 7 specialized AI agents coordinate through Masumi Network blockchain payments to handle parking reservations, dynamic pricing, route optimization, payment verification, security monitoring, and dispute resolution.

---

## 📋 What You're Building

**Input:** Customer reservation request from frontend app  
**Processing:** 7 AI agents work together, earning blockchain micropayments  
**Output:** Confirmed reservation with QR code, dynamic pricing, optimal route  
**Payment:** Cardano blockchain escrow via Masumi Network

---

## 🏗️ System Architecture

```
Customer App (Frontend)
    ↓
Flask API (Your Backend)
    ↓
Orchestrator Agent (Master)
    ↓
├─ Spot Finder Agent (Firebase → Raspberry Pi data)
├─ Pricing Agent (5-factor dynamic pricing)
├─ Route Optimizer Agent (Walking routes)
└─ Payment Verifier Agent (Blockchain verification)

Independent Monitoring:
├─ Security Guard Agent (Violation detection)
└─ Dispute Resolver Agent (AI arbitration)

    ↓
Masumi Network (Blockchain payments)
    ↓
Cardano Preprod Testnet
```

---

## 💰 Agent Economics

| Agent | Task | Earning | Cost to Customer |
|-------|------|---------|------------------|
| **Orchestrator** | Coordinates all agents | 0.4 ADA | 1.5 ADA (locked in escrow) |
| **Spot Finder** | Scans 66 spots, ranks top 5 | 0.3 ADA | (hired by Orchestrator) |
| **Pricing** | 5-factor dynamic pricing | 0.4 ADA | (hired by Orchestrator) |
| **Route Optimizer** | Calculates walking routes | 0.2 ADA | (hired by Orchestrator) |
| **Payment Verifier** | Blockchain verification | 0.2 ADA | (hired by Orchestrator) |
| **Security Guard** | Monitors violations | 20% of fines | Earns from violators |
| **Dispute Resolver** | AI arbitration | $2 per dispute | Both parties stake 5 ADA |

**Total:** Customer pays 1.5 ADA → Orchestrator earns 0.4 ADA profit (27% margin)

---

## 🔥 Firebase Configuration

### Firebase Project Setup:

```
Project Name: parkngo-ai
Database URL: https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app
Region: asia-southeast1
Authentication: Service Account
```

### Service Account JSON (parkngo-firebase-adminsdk.json):

**⚠️ CRITICAL: Store this file securely!**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select `parkngo-ai` project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Download `parkngo-firebase-adminsdk.json`
6. Store in: `secrets/parkngo-firebase-adminsdk.json`

**File structure:**
```json
{
  "type": "service_account",
  "project_id": "parkngo-ai",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@parkngo-ai.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### Environment Variables (.env):

```bash
# Firebase
FIREBASE_DATABASE_URL=https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app
FIREBASE_CREDENTIALS_PATH=./secrets/parkngo-firebase-adminsdk.json

# Masumi Network
MASUMI_PAYMENT_SERVICE_URL=http://localhost:3001/api/v1
MASUMI_NETWORK=preprod
MASUMI_AGENT_WALLET_ADDRESS=addr_test1qq3wrs0jq3lnrkasszv842v9fzfh02v3tvus9u6evmu98f7rp5kt6p7mft8jqd5kuzw4jdtng7nmk9pgm27h0sm74hpqjzwy4p
MASUMI_AGENT_SIGNING_KEY=ed25519_sk1...

# Blockfrost (Cardano API)
BLOCKFROST_PROJECT_ID=preprodXXXXXXXXXXXXXXXXXXXXXXXXXXX
BLOCKFROST_API_URL=https://cardano-preprod.blockfrost.io/api/v0

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Get Blockfrost API Key:

1. Go to [Blockfrost.io](https://blockfrost.io/)
2. Sign up / Login
3. Create new project: **Cardano Preprod**
4. Copy Project ID → `BLOCKFROST_PROJECT_ID`

---

## 📝 Firebase Database Schema (What You'll Read/Write)

### Read from Hardware Team:

```json
{
  "parking_spots": {
    "A-01": {
      "spot_id": "A-01",
      "occupied": false,
      "last_updated": "2025-11-27T10:30:00Z"
    }
  },
  "entries": {
    "ENTRY_20251127_001": {
      "timestamp": "2025-11-27T10:45:00Z"
    }
  },
  "sessions": {
    "SES_ABC123": {
      "spot_id": "B-15",
      "status": "active"
    }
  }
}
```

### Write for Frontend Team:

```json
{
  "reservations": {
    "RES_XYZ789": {
      "reservation_id": "RES_XYZ789",
      "customer_wallet": "addr_test1...",
      "spot": {
        "spot_id": "A-05",
        "type": "premium",
        "price_usd": 23.85
      },
      "pricing": {
        "base_price": 8.0,
        "time_multiplier": 1.5,
        "demand_premium": 0.9,
        "final_price": 23.85
      },
      "route": {
        "distance_m": 45,
        "walking_time_sec": 32,
        "directions": ["Enter main entrance", "Turn left", "Spot A-05 on right"]
      },
      "qr_code": "QR_ABC123XYZ",
      "masumi_payment": {
        "amount_ada": 1.5,
        "tx_hash": "a1b2c3...",
        "status": "locked"
      },
      "status": "confirmed"
    }
  },
  "violations": {
    "VIO_001": {
      "type": "overstay",
      "spot_id": "B-15",
      "fine_usd": 8.0,
      "status": "pending"
    }
  },
  "disputes": {
    "DIS_001": {
      "customer_stake": "5 ADA",
      "operator_stake": "5 ADA",
      "ruling": "customer_wins",
      "payout": "10 ADA to customer"
    }
  }
}
```

---

## 🐍 Python Backend Stack

### Required Packages:

```bash
pip install flask flask-cors
pip install firebase-admin
pip install requests
pip install python-dotenv
pip install pycardano
```

### Project Structure:

```
Project-ParknGo/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py          # Master coordinator (342 lines)
│   ├── spot_finder.py            # Availability scanner (199 lines)
│   ├── pricing_agent.py          # Dynamic pricing (207 lines)
│   ├── route_optimizer.py        # Route calculator (197 lines)
│   ├── payment_verifier.py       # Blockchain verification (229 lines)
│   ├── security_guard.py         # Violation monitor (197 lines)
│   └── dispute_resolver.py       # AI arbitration (244 lines)
├── app.py                         # Flask API (443 lines)
├── secrets/
│   └── parkngo-firebase-adminsdk.json
├── .env
├── requirements.txt
└── docker-compose.yml            # Masumi services
```

---

## 🤖 Agent Implementation Overview

### 1. Orchestrator Agent (Master)

**File:** `agents/orchestrator.py`

**Responsibilities:**
- Receives customer reservation request
- Creates 1.5 ADA Masumi escrow payment
- Hires 4 sub-agents sequentially
- Combines all results
- Generates QR code
- Submits SHA256 hash to unlock payment

**Key Functions:**
```python
def reserve_parking(customer_wallet, preferences):
    # 1. Create customer payment (1.5 ADA escrow)
    payment_id = _create_customer_payment(customer_wallet, 1.5)
    
    # 2. Hire sub-agents
    spots = spot_finder.find_available_spots(preferences)      # 0.3 ADA
    pricing = pricing_agent.calculate_pricing(spots)          # 0.4 ADA
    routes = route_optimizer.optimize_routes(spots)           # 0.2 ADA
    verification = payment_verifier.verify_payment(payment_id) # 0.2 ADA
    
    # 3. Combine results
    reservation = {
        'spot': spots[0],
        'pricing': pricing,
        'route': routes[0],
        'qr_code': generate_qr()
    }
    
    # 4. Submit result to unlock 0.4 ADA
    _submit_orchestrator_result(payment_id, reservation)
    
    return reservation
```

---

### 2. Spot Finder Agent

**File:** `agents/spot_finder.py`

**Responsibilities:**
- Queries Firebase for real-time spot data
- Filters by occupancy status
- Ranks by weighted scoring
- Returns top 5 spots

**Scoring Algorithm:**
```python
score = (
    0.4 * distance_score +      # 40% - Closer is better
    0.3 * preference_score +    # 30% - Matches customer needs
    0.2 * quality_score +       # 20% - Premium features
    0.1 * availability_score    # 10% - Recently freed spots
)
```

---

### 3. Pricing Agent

**File:** `agents/pricing_agent.py`

**Responsibilities:**
- 5-factor dynamic pricing model
- Time-based multipliers
- ML demand forecasting
- Event detection
- Weather premiums

**Pricing Formula:**
```python
price = base_price * time_multiplier * (1 + demand_premium) * (1 + event_premium) * (1 + weather_premium) * spot_type_multiplier + feature_fees

Example:
$8 base * 1.5 (peak) * 1.9 (demand) * 1.1 (event) * 1.25 (rain) * 1.0 (premium) + $2 (EV) = $23.85
```

**Factors:**
1. **Time Multiplier:** Peak (7-9am, 5-7pm) = 1.5x, Off-peak (10pm-6am) = 0.8x
2. **Demand Premium:** ML forecast 0-90% based on historical data
3. **Event Premium:** Concerts/movies within 500m = +10%
4. **Weather Premium:** Monsoon 20-30%, Summer 15-25%
5. **Spot Features:** EV charging +$2, Covered +$1.50

---

### 4. Route Optimizer Agent

**File:** `agents/route_optimizer.py`

**Responsibilities:**
- Calculates walking routes from entrance
- Distance, time, covered pathways
- Accessibility scoring (wheelchair/stroller)
- Turn-by-turn directions

**Scoring:**
```python
combined_score = (
    0.25 * spot_score +
    0.25 * price_score +
    0.20 * walking_score +
    0.15 * covered_score +
    0.15 * accessibility_score
)
```

---

### 5. Payment Verifier Agent

**File:** `agents/payment_verifier.py`

**Responsibilities:**
- Verifies Cardano transactions via Blockfrost
- Checks wallet reputation
- Fraud scoring
- Risk assessment

**Fraud Detection:**
```python
fraud_score = (
    0.4 * reputation_score +     # Transaction history
    0.3 * amount_score +         # Unusual payment amounts
    0.2 * timing_score +         # Off-hours activity
    0.1 * behavioral_score       # Suspicious patterns
)

# Risk levels:
# 0-20: Low (approve)
# 20-40: Medium (monitor)
# 40-70: High (additional verification)
# 70-100: Critical (decline)
```

---

### 6. Security Guard Agent

**File:** `agents/security_guard.py`

**Responsibilities:**
- Monitors Firebase sessions every 30 seconds
- Detects overstays
- Detects unauthorized vehicles
- Issues violation alerts

**Violation Rules:**
```python
# Overstay
if current_time > reserved_until + 15 minutes:
    fine = $2 per 15 minutes
    commission = 20% to Security Agent

# Unauthorized Vehicle
if vehicle_plate != reserved_plate:
    fine = $25 flat
    commission = $5 to Security Agent
```

---

### 7. Dispute Resolver Agent

**File:** `agents/dispute_resolver.py`

**Responsibilities:**
- Creates bilateral escrow (both parties stake 5 ADA)
- AI investigation with evidence analysis
- Final ruling based on confidence score
- Automatic payout distribution

**Dispute Process:**
```python
# 1. Customer disputes $15 charge
create_bilateral_escrow(customer, operator, 5 ADA each)

# 2. AI investigates
evidence = {
    'sensor_data': Firebase sessions,
    'payment_records': Masumi transactions,
    'customer_claim': "Spot unavailable",
    'operator_claim': "Spot was available"
}

confidence = investigate(evidence)  # 0-100%

# 3. Ruling
if confidence > 70:
    customer_wins → Gets $15 refund + 10 ADA (5+5)
elif confidence < 30:
    operator_wins → Keeps charge + 10 ADA
else:
    split → Both get 5 ADA back, 50% refund
```

---

## 🌐 Flask API Endpoints

### File: `app.py`

**10 Endpoints:**

```python
# Parking Reservations
POST   /api/v1/parking/reserve
GET    /api/v1/parking/reservation/<id>

# Agent Network
GET    /api/v1/agents/earnings
GET    /api/v1/agents/network/status

# Dispute Resolution
POST   /api/v1/disputes/create
POST   /api/v1/disputes/<id>/investigate
POST   /api/v1/disputes/<id>/ruling

# Security Monitoring
GET    /api/v1/security/violations
POST   /api/v1/security/violations/<id>/alert

# Health Check
GET    /health
```

---

## 🐳 Masumi Network Setup (Docker)

### docker-compose.yml:

```yaml
version: '3.8'

services:
  masumi-payment-service:
    image: masumi/payment-service:0.22.0
    ports:
      - "3001:3001"
    environment:
      - NETWORK=preprod
      - DATABASE_URL=postgresql://postgres:password@masumi-postgres-payment:5432/masumi_payments
    depends_on:
      - masumi-postgres-payment

  masumi-registry-service:
    image: masumi/registry-service:0.22.0
    ports:
      - "3000:3000"
    environment:
      - NETWORK=preprod
      - DATABASE_URL=postgresql://postgres:password@masumi-postgres-registry:5432/masumi_registry
    depends_on:
      - masumi-postgres-registry

  masumi-postgres-payment:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=masumi_payments
    ports:
      - "5433:5432"

  masumi-postgres-registry:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=masumi_registry
    ports:
      - "5432:5432"
```

**Start services:**

```bash
docker-compose up -d
```

---

## 🔑 Masumi Agent Registration

### Create Cardano Wallet:

```bash
# Generate new wallet
cardano-cli address key-gen \
  --verification-key-file payment.vkey \
  --signing-key-file payment.skey

# Build address
cardano-cli address build \
  --payment-verification-key-file payment.vkey \
  --out-file payment.addr \
  --testnet-magic 1

# View address
cat payment.addr
# Output: addr_test1qq3wrs0jq3lnrkasszv842v9fzfh02v3tvus9u6evmu98f7rp5kt6p7mft8jqd5kuzw4jdtng7nmk9pgm27h0sm74hpqjzwy4p
```

### Fund Wallet (Preprod Testnet):

1. Go to [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnet/tools/faucet/)
2. Paste your address
3. Receive 10,000 test ADA

### Register Agent on Masumi:

```bash
curl -X POST http://localhost:3000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "title": "ParknGo Orchestrator Agent",
      "identifier": "parkngo_orchestrator",
      "wallet_address": "addr_test1qq3wrs0jq3lnrkasszv842v9fzfh02v3tvus9u6evmu98f7rp5kt6p7mft8jqd5kuzw4jdtng7nmk9pgm27h0sm74hpqjzwy4p"
    }
  }'
```

---

## 🧪 Testing Strategy

### Unit Tests:

```bash
# Test each agent individually
python -m pytest tests/test_orchestrator.py
python -m pytest tests/test_spot_finder.py
python -m pytest tests/test_pricing_agent.py
```

### Integration Tests:

```bash
# Test full reservation flow
python -m pytest tests/test_reservation_flow.py

# Test dispute resolution
python -m pytest tests/test_disputes.py
```

### Load Testing:

```bash
# Simulate 100 concurrent requests
python tests/load_test.py --requests 100 --duration 60
```

---

## 📞 Communication with Other Teams

### To Hardware Team:
1. ✅ Send Firebase credentials (`parkngo-firebase-adminsdk.json`)
2. ✅ Confirm Firebase URL
3. ✅ Test Firebase listeners for sensor data

### To Frontend Team:
1. ✅ Provide API documentation
2. ✅ Share reservation response schema
3. ✅ Test QR code generation
4. ✅ Verify Firebase real-time updates

### Integration Testing:
- **Week 2:** Test with mock sensor data
- **Week 3:** Test with real Raspberry Pi sensors
- **Week 4:** End-to-end testing with frontend app

---

## 📅 Timeline

**Week 1: Foundation**
- [ ] Setup Firebase project
- [ ] Create service account credentials
- [ ] Setup Masumi Docker services
- [ ] Register agent wallet on Cardano
- [ ] Build Orchestrator Agent

**Week 2: Core Agents**
- [ ] Implement Spot Finder Agent
- [ ] Implement Pricing Agent
- [ ] Implement Route Optimizer Agent
- [ ] Implement Payment Verifier Agent
- [ ] Test with mock data

**Week 3: Monitoring Agents**
- [ ] Implement Security Guard Agent
- [ ] Implement Dispute Resolver Agent
- [ ] Integration with Hardware Team
- [ ] Firebase real-time listeners

**Week 4: API & Testing**
- [ ] Build Flask API endpoints
- [ ] Integration testing with Frontend
- [ ] Load testing (100+ concurrent requests)
- [ ] Deploy to staging environment

---

## ✅ Deliverables

When you're done, you should have:

1. ✅ 7 AI agents fully implemented
2. ✅ Flask API with 10 endpoints
3. ✅ Masumi Network integration
4. ✅ Firebase real-time listeners
5. ✅ Blockchain payment verification
6. ✅ Dispute resolution system
7. ✅ API documentation for frontend
8. ✅ Load testing results (>95% success rate)

---

**🎯 Your work is the BRAIN of the system - coordinating all agents and payments!**
