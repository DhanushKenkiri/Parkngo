# ParknGo Multi-Agent Parking Payment System

**Professional blockchain-powered parking marketplace using Masumi Network**

## 🎯 What We're Building

A smart parking payment system where 7 AI agents coordinate through Masumi Network (Cardano blockchain) to handle reservations, dynamic pricing, route optimization, payment verification, security monitoring, and dispute resolution.

**Simple Pitch:** "Reserve parking spots with guaranteed availability. If the spot isn't available, you get an automatic blockchain refund + penalty - no arguing with parking attendants."

## 🏗️ System Architecture

```
Hardware Layer (Raspberry Pi + IR Sensors)
    ↓ (Firebase Realtime Database)
Backend Layer (7 AI Agents + Flask API)
    ↓ (Masumi Network - Blockchain Payments)
Frontend Layer (Mobile/Web App)
```

## 🤖 AI Agents

1. **Orchestrator** - Master coordinator (earns 0.4 ADA)
2. **Spot Finder** - Scans 30 spots via Firebase (earns 0.3 ADA)
3. **Pricing Agent** - Gemini AI dynamic pricing (earns 0.4 ADA)
4. **Route Optimizer** - Walking routes (earns 0.2 ADA)
5. **Payment Verifier** - Blockfrost blockchain verification (earns 0.2 ADA)
6. **Security Guard** - Violation monitoring (earns 20% of fines)
7. **Dispute Resolver** - Gemini AI arbitration (earns $2 per dispute)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Firebase project setup
- Blockfrost API key
- Gemini API key

### Installation

1. **Clone and setup:**
```bash
git clone <repo-url>
cd Project-ParknGo
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Setup Masumi Network:**
```bash
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git masumi
cd masumi
cp .env.example .env
# Add Blockfrost API key to masumi/.env
docker compose up -d
```

4. **Seed Firebase:**
```bash
python scripts/seed-firebase.py
```

5. **Start backend:**
```bash
python app.py
```

## 📡 API Endpoints

- `POST /api/v1/parking/reserve` - Create reservation
- `GET /api/v1/parking/reservation/<id>` - Get reservation
- `POST /api/v1/disputes/create` - Create dispute
- `GET /api/v1/agents/earnings` - Agent earnings dashboard
- `GET /health` - Health check

Full API docs: http://localhost:5000/docs

## 🔧 Configuration

### Firebase Setup

1. Create Firebase project: `parkngo-ai`
2. Download service account JSON → `secrets/parkngo-firebase-adminsdk.json`
3. Import `firebase-seed-data.json` via Firebase Console

### Masumi Network

1. Services run on Docker:
   - Registry: http://localhost:3000
   - Payment: http://localhost:3001
2. Register agents: `python scripts/register-agents.py`

### Gemini AI

- Model: `gemini-1.5-flash` (fast, cost-effective)
- Usage: Pricing, dispute resolution, fraud detection
- Rate limit: 15 req/min (free tier)

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/test_reservation_flow.py

# Load testing
python tests/load_test.py --requests 100
```

## 📊 Tech Stack

- **Backend:** Python 3.11, Flask
- **Database:** Firebase Realtime Database
- **AI:** Google Gemini 1.5 Flash
- **Blockchain:** Cardano Preprod (via Masumi Network)
- **API:** Blockfrost
- **Deployment:** Docker, Gunicorn

## 🔐 Security

- Never commit `.env` or `secrets/` folder
- Cardano wallet keys stored securely
- Firebase service account credentials protected
- API rate limiting enabled

## 📖 Documentation

- [Hardware Team Guide](HARDWARE_TEAM_README.md) - Raspberry Pi setup
- [Backend Team Guide](BACKEND_TEAM_README.md) - Agent implementation
- [Frontend Team Guide](FRONTEND_TEAM_README.md) - Mobile/web app
- [Masumi Docs](https://docs.masumi.network)

## 🤝 Team Structure

- **Hardware:** Raspberry Pi + IR sensors → Firebase
- **Backend:** 7 AI agents + Masumi payments (You)
- **Frontend:** Mobile/web app → Customer interface

## 📜 License

MIT

## 🆘 Support

- Masumi Network: https://docs.masumi.network
- Firebase: https://firebase.google.com/docs
- Gemini AI: https://ai.google.dev/docs
