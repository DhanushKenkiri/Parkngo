# 🅿️ ParknGo - Multi-Agent AI Parking System

**Intelligent parking management powered by 7 AI agents, blockchain payments, and real-time monitoring**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/)
[![Cardano](https://img.shields.io/badge/Cardano-Blockchain-blue.svg)](https://cardano.org/)

---

## 🎯 Overview

ParknGo is a revolutionary parking management system that uses **7 specialized AI agents** working together to provide:
- 🤖 **Intelligent Spot Recommendations** - Gemini AI ranks spots by user preferences
- 💰 **Dynamic Pricing** - AI-powered demand forecasting and fair pricing
- 🚶 **Smart Navigation** - AI-generated walking directions to your spot
- 🔐 **Blockchain Payments** - Secure Cardano/Masumi Network transactions
- 👮 **Automated Security** - AI detects violations and anomalies
- ⚖️ **AI Arbitration** - Gemini AI resolves disputes fairly

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                       │
│              (Master Coordinator + Gemini AI)               │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬───────────────┐
    │             │             │             │               │
┌───▼────┐  ┌────▼────┐  ┌─────▼────┐  ┌────▼─────┐  ┌──────▼──────┐
│ Spot   │  │ Pricing │  │  Route   │  │ Payment  │  │  Security   │
│ Finder │  │ Agent   │  │Optimizer │  │ Verifier │  │   Guard     │
│(Gemini)│  │(Gemini) │  │ (Gemini) │  │ (Gemini) │  │  (Gemini)   │
└────────┘  └─────────┘  └──────────┘  └──────────┘  └─────────────┘
                                                            │
                                                       ┌────▼────────┐
                                                       │  Dispute    │
                                                       │  Resolver   │
                                                       │  (Gemini)   │
                                                       └─────────────┘
```

### Technology Stack

- **AI/ML**: Google Gemini 1.5 Flash (all agents)
- **Backend**: Flask REST API (Python 3.10+)
- **Database**: Firebase Realtime Database
- **Blockchain**: Cardano (Preprod) via Masumi Network
- **Hardware**: Raspberry Pi + IR sensors
- **Deployment**: Docker Compose

---

## ✨ Key Features

### 🧠 AI-Powered Intelligence

**All 7 agents use Google Gemini AI:**

1. **Orchestrator** - Coordinates all agents, aggregates results intelligently
2. **SpotFinder** - Ranks parking spots (0-100 confidence scoring)
3. **PricingAgent** - Forecasts demand, calculates 5-factor dynamic pricing
4. **RouteOptimizer** - Generates walking directions and route tips
5. **PaymentVerifier** - Detects fraud (0-100 risk scores)
6. **SecurityGuard** - Monitors sessions, detects anomalies every 30s
7. **DisputeResolver** - AI arbitration with bilateral escrow

### 💳 Blockchain Payments

- **Masumi Network** integration for multi-agent payments
- **Cardano blockchain** verification via Blockfrost API
- **Smart contracts** for escrow and dispute resolution
- Payment distribution: 30% SpotFinder, 25% Pricing, 25% Route, 20% PaymentVerifier

### 📊 Real-Time Monitoring

- Live session tracking with Firebase
- Automated violation detection
- Overstay monitoring with grace periods
- Anomaly detection via Gemini AI

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Firebase account + credentials
- Google Gemini API key
- Blockfrost API key (Cardano preprod)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/DhanushKenkiri/Parkngo.git
cd Parkngo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Add Firebase credentials
# Place parkngo-firebase-adminsdk.json in secrets/

# 5. Start Masumi services
cd masumi
docker compose up -d
cd ..

# 6. Start API server
python app.py
```

**Or use the automated startup script:**
```powershell
# Windows
.\start.ps1

# Linux/Mac
chmod +x start.sh && ./start.sh
```

### Verify Installation

```bash
# Check health
curl http://localhost:5000/api/health

# Get available spots
curl http://localhost:5000/api/parking/spots

# View statistics
curl http://localhost:5000/api/stats
```

---

## 📡 API Endpoints

### Parking Operations
- `POST /api/parking/reserve` - Create reservation (Orchestrator + all agents)
- `GET /api/parking/spots` - Get available spots
- `POST /api/parking/price` - Calculate dynamic price (Gemini AI)

### Payments
- `POST /api/payment/verify` - Verify blockchain payment (Gemini fraud detection)
- `GET /api/payment/status/{id}` - Check payment status

### Disputes
- `POST /api/disputes/create` - Create dispute (Gemini investigation)
- `GET /api/disputes/{id}` - Get dispute status
- `POST /api/disputes/{id}/resolve` - AI arbitration

### Monitoring
- `GET /api/monitoring/sessions` - Security Guard monitoring
- `GET /api/agents/earnings` - Agent payment distribution

### System
- `GET /api/health` - Health check
- `GET /api/stats` - System statistics

**Full API documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Step-by-step setup
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment
- **[Hardware Team Guide](docs/HARDWARE_TEAM_README.md)** - Raspberry Pi setup
- **[Backend Team Guide](docs/BACKEND_TEAM_README.md)** - Agent architecture
- **[Frontend Team Guide](docs/FRONTEND_TEAM_README.md)** - Mobile/web integration
- **[Masumi Setup](MASUMI_SETUP_GUIDE.md)** - Blockchain services

---

## 🧪 Testing

```bash
# Run full test suite
python tests/test_api.py

# Test specific endpoint
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

## 🏭 Production Deployment

### Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f parkngo-api
```

### Manual Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment (AWS, GCP, Heroku), scaling, and monitoring.

---

## 📊 Project Statistics

- **Total Lines of Code**: ~5,600+
- **AI Agents**: 7 (all using Gemini API)
- **API Endpoints**: 12
- **Service Modules**: 3 (Firebase, Gemini, Masumi)
- **Test Coverage**: 10+ integration tests
- **Documentation Pages**: 7

---

## 🤝 Team Structure

This project is designed for 3 teams:

### Hardware Team
- Raspberry Pi setup with IR sensors
- Real-time Firebase sync
- GPIO pin management
- See: [HARDWARE_TEAM_README.md](docs/HARDWARE_TEAM_README.md)

### Backend Team
- AI agent development
- API endpoint implementation
- Blockchain integration
- See: [BACKEND_TEAM_README.md](docs/BACKEND_TEAM_README.md)

### Frontend Team
- Mobile app (React Native)
- Web dashboard (React)
- Real-time updates
- See: [FRONTEND_TEAM_README.md](docs/FRONTEND_TEAM_README.md)

---

## 🔧 Configuration

### Environment Variables

```bash
# Firebase
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Blockchain
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id

# Masumi Network
MASUMI_PAYMENT_SERVICE_URL=http://localhost:3001
MASUMI_REGISTRY_SERVICE_URL=http://localhost:3000
```

---

## 🛠️ Development

### Project Structure

```
ParknGo/
├── agents/              # 7 AI agents
│   ├── orchestrator.py
│   ├── spot_finder.py
│   ├── pricing_agent.py
│   ├── route_optimizer.py
│   ├── payment_verifier.py
│   ├── security_guard.py
│   └── dispute_resolver.py
├── services/            # Core services
│   ├── firebase_service.py
│   ├── gemini_service.py
│   └── masumi_service.py
├── tests/               # Test suite
│   └── test_api.py
├── docs/                # Team documentation
├── masumi/              # Blockchain services
├── app.py               # Flask API server
└── requirements.txt     # Python dependencies
```

### Adding New Features

1. Create new agent in `agents/`
2. Add to `agents/__init__.py`
3. Integrate in `app.py`
4. Add tests in `tests/`
5. Update documentation

---

## 🐛 Troubleshooting

**Masumi services not running:**
```bash
cd masumi
docker compose down
docker compose up -d
```

**Firebase connection error:**
- Check `secrets/parkngo-firebase-adminsdk.json` exists
- Verify FIREBASE_DATABASE_URL in `.env`

**Gemini API errors:**
- Verify GEMINI_API_KEY in `.env`
- Check quota limits at https://ai.google.dev/

**Port conflicts:**
```bash
# Change port
export PORT=5001
python app.py
```

---

## 🙏 Acknowledgments

- **Google Gemini** - AI capabilities across all agents
- **Masumi Network** - Blockchain payment infrastructure
- **Cardano** - Secure blockchain platform
- **Firebase** - Real-time database
- **Flask** - Web framework

---

## 📞 Support

- **Repository**: https://github.com/DhanushKenkiri/Parkngo
- **Issues**: [Create a GitHub issue](https://github.com/DhanushKenkiri/Parkngo/issues)
- **Documentation**: See `docs/` folder

---

## 🎯 Roadmap

- [x] Multi-agent system with Gemini AI
- [x] Blockchain payment integration
- [x] REST API with 12 endpoints
- [x] Real-time monitoring
- [ ] Mobile app (React Native)
- [ ] Web dashboard (React)
- [ ] Machine learning for demand prediction
- [ ] License plate recognition
- [ ] Multi-language support
- [ ] Analytics dashboard

---

**Built with ❤️ using AI, Blockchain, and IoT**
