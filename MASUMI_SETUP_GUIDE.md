# Masumi Network Setup Guide for ParknGo

This guide walks you through setting up Masumi Network services using Docker Compose for the ParknGo multi-agent parking payment system.

## 📋 Prerequisites

- Docker Desktop installed and running
- Blockfrost API key: `preprod90EY0ncWFPdpvU1G5VS4LUye0mlZL2tJ`
- Git installed

## 🚀 Step-by-Step Setup

### Step 1: Clone Masumi Quickstart Repository

```powershell
# Navigate to project directory
cd C:\Users\dhwin\Project-ParknGo

# Clone Masumi quickstart repo
git clone https://github.com/masumi-network/masumi-services-dev-quickstart.git masumi

# Navigate to masumi folder
cd masumi
```

### Step 2: Configure Environment Variables

```powershell
# Copy environment template
cp .env.example .env

# Open .env file for editing
notepad .env
```

**Edit `.env` file with these values:**

```bash
# ============================================
# CARDANO NETWORK
# ============================================
CARDANO_NETWORK=preprod

# ============================================
# BLOCKFROST API
# ============================================
BLOCKFROST_PROJECT_ID=preprod90EY0ncWFPdpvU1G5VS4LUye0mlZL2tJ
BLOCKFROST_BASE_URL=https://cardano-preprod.blockfrost.io/api/v0

# ============================================
# DATABASE CONFIGURATION
# ============================================
# Payment Service Database
PAYMENT_DB_HOST=masumi-postgres-payment
PAYMENT_DB_PORT=5432
PAYMENT_DB_NAME=masumi_payments
PAYMENT_DB_USER=postgres
PAYMENT_DB_PASSWORD=postgres_password_change_in_production

# Registry Service Database
REGISTRY_DB_HOST=masumi-postgres-registry
REGISTRY_DB_PORT=5432
REGISTRY_DB_NAME=masumi_registry
REGISTRY_DB_USER=postgres
REGISTRY_DB_PASSWORD=postgres_password_change_in_production

# ============================================
# SERVICE PORTS
# ============================================
PAYMENT_SERVICE_PORT=3001
REGISTRY_SERVICE_PORT=3000
PAYMENT_DB_EXTERNAL_PORT=5433
REGISTRY_DB_EXTERNAL_PORT=5432

# ============================================
# OPTIONAL: ADVANCED SETTINGS
# ============================================
# Log Level
LOG_LEVEL=info

# Enable API documentation
ENABLE_OPENAPI_DOCS=true
```

### Step 3: Start Masumi Services

```powershell
# Ensure Docker Desktop is running
# You can verify by running:
docker --version

# Start all services in detached mode
docker compose up -d

# Check if services are running
docker compose ps
```

**Expected Output:**
```
NAME                              STATUS
masumi-payment-service            Up (healthy)
masumi-registry-service           Up (healthy)
masumi-postgres-payment           Up
masumi-postgres-registry          Up
```

### Step 4: Verify Services

**Check Payment Service:**
```powershell
# Test health endpoint
curl http://localhost:3001/health

# Access admin dashboard
start http://localhost:3001/admin

# Access OpenAPI docs
start http://localhost:3001/docs
```

**Check Registry Service:**
```powershell
# Test health endpoint
curl http://localhost:3000/health

# Access OpenAPI docs
start http://localhost:3000/docs
```

### Step 5: View Logs (Optional)

```powershell
# View all service logs
docker compose logs -f

# View specific service logs
docker compose logs -f masumi-payment-service
docker compose logs -f masumi-registry-service
```

## 🎯 Service URLs

Once running, access these endpoints:

| Service | URL | Purpose |
|---------|-----|---------|
| **Payment Service API** | http://localhost:3001/docs | Create payments, submit results |
| **Payment Admin Dashboard** | http://localhost:3001/admin | Monitor payments |
| **Registry Service API** | http://localhost:3000/docs | Register agents |
| **PostgreSQL (Payments)** | localhost:5433 | Payment database |
| **PostgreSQL (Registry)** | localhost:5432 | Registry database |

## 🔧 Troubleshooting

### Issue: Docker compose up fails

**Solution:**
```powershell
# Check if Docker Desktop is running
docker info

# If not running, start Docker Desktop app
```

### Issue: Port already in use

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :3001
netstat -ano | findstr :3000

# Kill the process or change ports in .env
```

### Issue: Database connection errors

**Solution:**
```powershell
# Restart services
docker compose down
docker compose up -d

# Check database logs
docker compose logs masumi-postgres-payment
```

### Issue: Services unhealthy

**Solution:**
```powershell
# Recreate services
docker compose down -v
docker compose up -d --force-recreate
```

## 🧪 Test Masumi Integration

**Create a test file: `test_masumi.py`**

```python
import requests

# Test Payment Service
response = requests.get('http://localhost:3001/health')
print(f"Payment Service: {'✅ UP' if response.status_code == 200 else '❌ DOWN'}")

# Test Registry Service
response = requests.get('http://localhost:3000/health')
print(f"Registry Service: {'✅ UP' if response.status_code == 200 else '❌ DOWN'}")
```

**Run test:**
```powershell
cd C:\Users\dhwin\Project-ParknGo
python test_masumi.py
```

## 📦 Docker Commands Reference

```powershell
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View running containers
docker compose ps

# View logs
docker compose logs -f

# Remove all data (CAUTION!)
docker compose down -v

# Update services
docker compose pull
docker compose up -d
```

## 🔐 Security Notes

1. **Change default passwords** in production
2. **Never commit `.env`** to version control
3. **Use Blockfrost rate limits** appropriately
4. **Monitor database access** logs

## ✅ Next Steps

Once Masumi services are running:

1. **Register ParknGo agents** using `scripts/register-agents.py`
2. **Generate Cardano wallet** for agent payments
3. **Fund wallet** with test ADA from faucet
4. **Test payment creation** from Python backend

## 📖 Resources

- [Masumi Documentation](https://docs.masumi.network)
- [Masumi GitHub](https://github.com/masumi-network)
- [Blockfrost Docs](https://docs.blockfrost.io)
- [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnet/tools/faucet/)

## 🆘 Support

If you encounter issues:
1. Check Masumi Discord/community
2. Review Docker logs
3. Verify Blockfrost API key is valid
4. Ensure ports 3000, 3001, 5432, 5433 are available
