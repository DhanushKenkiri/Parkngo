# 🐳 ParknGo Docker Deployment Guide

This guide covers running the entire ParknGo Multi-Agent Parking System in Docker with Masumi Network integration.

## 🎯 What Gets Deployed

When you run `docker compose up`, you get **5 containerized services**:

1. **parkngo-api** - Flask API server with all 7 AI agents
2. **masumi-payment-service** - Masumi payment processing (port 3001)
3. **masumi-registry-service** - Masumi agent registry (port 3000)
4. **masumi-postgres-payment** - PostgreSQL database for payments
5. **masumi-postgres-registry** - PostgreSQL database for registry

All services are connected via a Docker bridge network for seamless communication.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Firebase credentials in `secrets/parkngo-firebase-adminsdk.json`
- `.env` file configured (see below)

### Option 1: Automated Script (Recommended)

```powershell
.\docker-start.ps1
```

This script will:
- Stop any existing Masumi containers
- Verify configuration files
- Build and start all 5 services
- Wait for health checks
- Display service URLs

### Option 2: Manual Deployment

```bash
# Stop existing Masumi containers (if running separately)
cd masumi
docker compose down
cd ..

# Build and start everything
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f parkngo-api
```

## ⚙️ Configuration

### Required Environment Variables (.env)

```env
# Firebase
FIREBASE_DATABASE_URL=https://your-project.firebasedatabase.app
FIREBASE_CREDENTIALS_PATH=./secrets/parkngo-firebase-adminsdk.json

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# Blockfrost (Cardano)
BLOCKFROST_PROJECT_ID=preprod_your_project_id

# Masumi (automatically configured in Docker)
MASUMI_PAYMENT_SERVICE_URL=http://masumi-payment-service:3001
MASUMI_REGISTRY_SERVICE_URL=http://masumi-registry-service:3000
MASUMI_ENCRYPTION_KEY=parkngo_super_secure_encryption_key_32chars_minimum_required
MASUMI_ADMIN_KEY=parkngo_admin_key_secure_15chars_min
```

### Network Configuration

All services communicate via Docker's internal network:

- **External Access**: Services accessible from host via localhost
- **Internal Access**: Services use container names (e.g., `http://masumi-payment-service:3001`)

## 📊 Service Details

### ParknGo API (Port 5000)

**Container:** `parkngo-api`  
**Image:** Built from local Dockerfile  
**Depends on:** masumi-payment-service, masumi-registry-service  

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Key Features:**
- All 7 AI agents initialized
- Connects to Masumi services via Docker network
- Firebase Realtime Database integration
- Gemini AI for all intelligent features

### Masumi Payment Service (Port 3001)

**Container:** `masumi-payment-service`  
**Image:** `ghcr.io/masumi-network/masumi-payment-service:0.22.0`  
**Database:** masumi-postgres-payment (port 5433)

**Health Check:**
```bash
curl http://localhost:3001/api/v1/health
```

**Responsibilities:**
- Payment processing
- Transaction verification
- Blockchain integration
- Automatic payment batching

### Masumi Registry Service (Port 3000)

**Container:** `masumi-registry-service`  
**Image:** `ghcr.io/masumi-network/masumi-registry-service:0.22.0`  
**Database:** masumi-postgres-registry (port 5432)

**Health Check:**
```bash
curl http://localhost:3000/api/v1/health
```

**Responsibilities:**
- Agent registration
- Service discovery
- Agent metadata management

### PostgreSQL Databases

**Payment Database:**
- Container: `masumi-postgres-payment`
- Port: 5433 (mapped from 5432)
- Volume: `parkngo_masumi_payment_data`

**Registry Database:**
- Container: `masumi-postgres-registry`
- Port: 5432
- Volume: `parkngo_masumi_registry_data`

## 🔧 Common Operations

### Start Services

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f parkngo-api
docker compose logs -f masumi-payment-service
docker compose logs -f masumi-registry-service
```

### Restart Service

```bash
docker compose restart parkngo-api
```

### Rebuild After Code Changes

```bash
docker compose up -d --build parkngo-api
```

### Clean Everything (including volumes)

```bash
docker compose down -v
```

**⚠️ Warning:** This deletes all database data!

## 🧪 Testing the Deployment

### 1. Health Checks

```bash
# ParknGo API
curl http://localhost:5000/api/health

# Masumi Payment
curl http://localhost:3001/api/v1/health

# Masumi Registry
curl http://localhost:3000/api/v1/health
```

### 2. Get Parking Spots

```bash
curl http://localhost:5000/api/parking/spots
```

### 3. System Statistics

```bash
curl http://localhost:5000/api/stats
```

### 4. Create Reservation (Full AI Orchestration)

```bash
curl -X POST http://localhost:5000/api/parking/reserve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "user_location": {"lat": 40.7128, "lng": -74.0060},
    "vehicle_type": "sedan",
    "desired_features": ["covered"],
    "duration_hours": 2.0,
    "wallet_address": "addr1qy..."
  }'
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check container status
docker compose ps

# View detailed logs
docker compose logs parkngo-api

# Inspect specific container
docker inspect parkngo-api
```

### Database Connection Issues

```bash
# Check if databases are healthy
docker compose ps | grep postgres

# Access database directly
docker exec -it masumi-postgres-payment psql -U postgres
```

### Masumi Services Not Connecting

```bash
# Check network
docker network inspect parkngo_parkngo-network

# Verify service discovery
docker compose exec parkngo-api ping masumi-payment-service
```

### Reset Everything

```bash
# Stop all containers
docker compose down

# Remove volumes
docker volume rm parkngo_masumi_payment_data parkngo_masumi_registry_data

# Rebuild from scratch
docker compose up -d --build
```

## 📈 Scaling

### Run Multiple API Instances

```bash
docker compose up -d --scale parkngo-api=3
```

Add a load balancer (Nginx) for production use.

### Monitor Resources

```bash
# Resource usage
docker stats

# Specific container
docker stats parkngo-api
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` with real credentials
2. **Secrets Management**: Use Docker secrets in production:
   ```bash
   docker secret create firebase_creds ./secrets/parkngo-firebase-adminsdk.json
   ```
3. **Network Isolation**: Services only expose necessary ports
4. **Database Access**: PostgreSQL not exposed externally in production

## 🚀 Production Deployment

### Using Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml parkngo
```

### Using Kubernetes

See `DEPLOYMENT.md` for Kubernetes manifests.

### Environment-Specific Configs

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 📊 Monitoring

### Health Endpoint

```bash
watch -n 5 curl -s http://localhost:5000/api/health | jq
```

### Container Metrics

```bash
docker compose stats
```

### Log Aggregation

```bash
# Export to file
docker compose logs > deployment.log

# Follow all services
docker compose logs -f --tail=100
```

## 🎯 Success Criteria

✅ All 5 containers running  
✅ Health checks passing  
✅ ParknGo API responding on port 5000  
✅ Masumi services responding on ports 3000/3001  
✅ All 7 AI agents initialized  
✅ Database migrations complete  

## 📞 Support

- **Issues**: Check container logs first
- **Performance**: Monitor with `docker stats`
- **Updates**: Rebuild with `docker compose up -d --build`

---

**Built with ❤️ using Docker, Masumi Network, and AI**
