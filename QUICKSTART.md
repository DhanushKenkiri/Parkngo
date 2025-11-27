# ParknGo Multi-Agent Parking System - Quick Start Guide

## 🚀 Complete System Overview

**Multi-Agent AI Parking System with Blockchain Payments**
- 7 AI agents using Google Gemini API
- Firebase Realtime Database
- Masumi Network blockchain payments (Cardano)
- Flask REST API with 12 endpoints

---

## 📋 Prerequisites

- Python 3.10+
- Docker & Docker Compose (for Masumi services)
- Firebase account with Realtime Database
- Google Gemini API key
- Blockfrost API key (Cardano preprod)

---

## ⚡ Quick Start

### 1. Start Masumi Network Services

```powershell
# Navigate to Masumi directory
cd masumi

# Start Docker services
docker compose up -d

# Verify services are running
docker ps
```

**Expected:** 4 containers running (payment-service, registry-service, 2x postgres)

### 2. Install Python Dependencies

```powershell
# Back to project root
cd ..

# Install packages
pip install -r requirements.txt
```

**Installed packages:**
- flask, flask-cors (API server)
- firebase-admin (database)
- google-generativeai (Gemini AI)
- requests, python-dotenv (utilities)

### 3. Configure Environment Variables

File: `.env` (already configured)

```bash
# Firebase
FIREBASE_DATABASE_URL=https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app

# Gemini AI
GEMINI_API_KEY=AIzaSyAev0zQDBDpjCxKHVgDX0tVvz6aQOiDfWg

# Blockfrost (Cardano)
BLOCKFROST_PROJECT_ID=preprod90EY0ncWFPdpvU1G5VS4LUye0mlZL2tJ

# Masumi Network
MASUMI_PAYMENT_SERVICE_URL=http://localhost:3001
MASUMI_REGISTRY_SERVICE_URL=http://localhost:3000
```

### 4. Start the Flask API Server

```powershell
# Run the API
python app.py
```

**Expected output:**
```
🚀 Starting ParknGo Multi-Agent Parking System API...
============================================================
Agents initialized:
  ✅ Orchestrator Agent (master coordinator)
  ✅ SpotFinder Agent (Gemini AI ranking)
  ✅ PricingAgent (Gemini demand forecasting)
  ✅ RouteOptimizer Agent (Gemini directions)
  ✅ PaymentVerifier Agent (Gemini fraud detection)
  ✅ SecurityGuard Agent (Gemini anomaly detection)
  ✅ DisputeResolver Agent (Gemini AI arbitration)
============================================================
 * Running on http://0.0.0.0:5000
```

### 5. Test the API

```powershell
# Run test suite (in new terminal)
python tests/test_api.py
```

**Or test manually:**

```powershell
# Health check
curl http://localhost:5000/api/health

# Get available spots
curl http://localhost:5000/api/parking/spots

# Get system stats
curl http://localhost:5000/api/stats
```

---

## 🎯 Key Endpoints

### Create Parking Reservation
```powershell
curl -X POST http://localhost:5000/api/parking/reserve `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "user_123",
    "user_location": {"lat": 40.7128, "lng": -74.0060},
    "vehicle_type": "sedan",
    "desired_features": ["covered"],
    "duration_hours": 2.0,
    "wallet_address": "addr1qy_test_wallet"
  }'
```

### Calculate Price (Gemini AI)
```powershell
curl -X POST http://localhost:5000/api/parking/price `
  -H "Content-Type: application/json" `
  -d '{
    "spot_id": "A-01",
    "duration_hours": 2.5
  }'
```

### Monitor Sessions (Security Guard)
```powershell
curl http://localhost:5000/api/monitoring/sessions
```

---

## 🧠 AI Agent Architecture

### Core Agents (Parking Flow)
1. **Orchestrator** - Master coordinator
   - Creates Masumi payment (1.5 ADA)
   - Coordinates 4 sub-agents
   - Gemini aggregates results

2. **SpotFinder** - Find best spot
   - Firebase queries
   - **Gemini AI ranks spots** (95/100 confidence)

3. **PricingAgent** - Dynamic pricing
   - **Gemini demand forecasting**
   - 5-factor pricing (time/demand/features)

4. **RouteOptimizer** - Walking directions
   - Distance calculation
   - **Gemini generates directions**

### Monitoring Agents
5. **PaymentVerifier** - Blockchain verification
   - Blockfrost API queries
   - **Gemini fraud detection** (0-100 score)

6. **SecurityGuard** - Violation detection
   - Monitors every 30 seconds
   - **Gemini anomaly detection**

7. **DisputeResolver** - AI arbitration
   - **Gemini investigates evidence**
   - Bilateral escrow management

---

## 📊 System Status

### Check Services Health
```powershell
curl http://localhost:5000/api/health
```

**Expected Response:**
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
  }
}
```

---

## 🔧 Troubleshooting

### Masumi Services Not Running
```powershell
cd masumi
docker compose down
docker compose up -d
docker ps  # Check status
```

### Firebase Connection Error
- Verify `secrets/parkngo-firebase-adminsdk.json` exists
- Check FIREBASE_DATABASE_URL in `.env`

### Gemini API Errors
- Verify GEMINI_API_KEY in `.env`
- Check quota limits on Google AI Studio

### Port Already in Use
```powershell
# Change port in app.py or use environment variable
$env:PORT=5001
python app.py
```

---

## 📁 Project Structure

```
Project-ParknGo/
├── agents/                  # 7 AI agents
│   ├── orchestrator.py     # Master coordinator
│   ├── spot_finder.py      # Gemini AI ranking
│   ├── pricing_agent.py    # Gemini demand forecasting
│   ├── route_optimizer.py  # Gemini directions
│   ├── payment_verifier.py # Gemini fraud detection
│   ├── security_guard.py   # Gemini anomaly detection
│   └── dispute_resolver.py # Gemini AI arbitration
│
├── services/               # Core services
│   ├── firebase_service.py # Firebase integration
│   ├── gemini_service.py   # Gemini AI wrapper
│   └── masumi_service.py   # Masumi Network API
│
├── tests/                  # Testing
│   └── test_api.py        # API test suite
│
├── docs/                   # Documentation
│   ├── HARDWARE_TEAM_README.md
│   ├── BACKEND_TEAM_README.md
│   └── FRONTEND_TEAM_README.md
│
├── masumi/                 # Masumi Docker setup
│   └── docker-compose.yml
│
├── app.py                  # Flask API (12 endpoints)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── API_DOCUMENTATION.md    # Complete API docs
```

---

## 🎓 Next Steps

### For Hardware Team
See `docs/HARDWARE_TEAM_README.md`
- Raspberry Pi setup
- IR sensor integration
- Firebase real-time sync

### For Frontend Team
See `docs/FRONTEND_TEAM_README.md`
- API integration guide
- Mobile app wireframes
- WebSocket for real-time updates

### For Testing
```powershell
# Run full test suite
python tests/test_api.py

# Test specific endpoint
curl http://localhost:5000/api/parking/reserve -X POST ...
```

---

## 📚 Documentation

- **API Documentation:** `API_DOCUMENTATION.md`
- **Masumi Setup:** `MASUMI_SETUP_GUIDE.md`
- **Team Guides:** `docs/` folder

---

## 🚀 Production Deployment

### Environment Variables
```bash
FLASK_ENV=production
PORT=5000
# ... (copy from .env)
```

### Run with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```bash
docker build -t parkngo-api .
docker run -p 5000:5000 --env-file .env parkngo-api
```

---

## ✅ Success Criteria

- ✅ All 7 agents initialized
- ✅ Masumi services healthy (4 containers)
- ✅ Firebase connected
- ✅ Gemini API responding
- ✅ Flask API running on port 5000
- ✅ Health check returns 200 OK

**You're ready to go! 🎉**

---

## 📞 Support

**Repository:** https://github.com/DhanushKenkiri/Parkngo

**Key Features:**
- Multi-agent AI system
- Gemini API integration (all agents)
- Blockchain payments (Cardano/Masumi)
- Real-time monitoring
- AI-powered dispute resolution
