# ParknGo Multi-Agent Parking System - Production Deployment Guide

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

**Full stack deployment with all services:**

```bash
# 1. Build and start all services
docker-compose up -d --build

# 2. Check service status
docker-compose ps

# 3. View logs
docker-compose logs -f parkngo-api

# 4. Stop all services
docker-compose down
```

**Services included:**
- ParknGo API (port 5000)
- Masumi Payment Service (port 3001)
- Masumi Registry Service (port 3000)
- PostgreSQL databases (2x)

---

### Option 2: Manual Deployment

**1. Install Dependencies**
```bash
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

**2. Set Environment Variables**
```bash
export FLASK_ENV=production
export PORT=5000
# Copy all from .env
```

**3. Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**4. Run with uWSGI**
```bash
pip install uwsgi
uwsgi --ini uwsgi.ini
```

---

### Option 3: Windows Service

**Using NSSM (Non-Sucking Service Manager):**

```powershell
# 1. Download NSSM from nssm.cc
# 2. Install as service
nssm install ParknGo "C:\Python311\python.exe" "C:\path\to\app.py"

# 3. Start service
nssm start ParknGo

# 4. Check status
nssm status ParknGo
```

---

## 🌐 Nginx Reverse Proxy (Production)

**Install Nginx:**
```bash
# Ubuntu/Debian
sudo apt install nginx

# Windows
# Download from nginx.org
```

**Nginx Configuration:** `/etc/nginx/sites-available/parkngo`

```nginx
server {
    listen 80;
    server_name parkngo.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (for future real-time features)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/parkngo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 SSL/HTTPS (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d parkngo.yourdomain.com

# Auto-renewal is configured automatically
```

---

## 🐳 Docker Production Build

**Build optimized image:**
```bash
docker build -t parkngo-api:latest .
```

**Run container:**
```bash
docker run -d \
  --name parkngo-api \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/secrets:/app/secrets:ro \
  --restart unless-stopped \
  parkngo-api:latest
```

**Push to registry:**
```bash
# Tag for registry
docker tag parkngo-api:latest yourusername/parkngo-api:latest

# Push
docker push yourusername/parkngo-api:latest
```

---

## ☁️ Cloud Deployment

### AWS Elastic Beanstalk

**1. Install EB CLI:**
```bash
pip install awsebcli
```

**2. Initialize:**
```bash
eb init -p python-3.11 parkngo-api
```

**3. Create environment:**
```bash
eb create parkngo-production
```

**4. Deploy:**
```bash
eb deploy
```

---

### Google Cloud Run

**1. Build container:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/parkngo-api
```

**2. Deploy:**
```bash
gcloud run deploy parkngo-api \
  --image gcr.io/PROJECT_ID/parkngo-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

### Heroku

**1. Create app:**
```bash
heroku create parkngo-api
```

**2. Add buildpack:**
```bash
heroku buildpacks:set heroku/python
```

**3. Set config vars:**
```bash
heroku config:set GEMINI_API_KEY=your_key
heroku config:set FIREBASE_DATABASE_URL=your_url
# ... (all environment variables)
```

**4. Deploy:**
```bash
git push heroku main
```

---

## 📊 Monitoring & Logging

### Application Monitoring

**Add New Relic:**
```bash
pip install newrelic
newrelic-admin generate-config LICENSE_KEY newrelic.ini
newrelic-admin run-program gunicorn app:app
```

**Add Sentry:**
```bash
pip install sentry-sdk[flask]
```

```python
# In app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Logging

**Production logging configuration:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/parkngo.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

---

## 🔐 Security Checklist

- [ ] Change default SECRET_KEY in production
- [ ] Use HTTPS only (SSL certificate)
- [ ] Enable CORS only for trusted domains
- [ ] Add rate limiting (nginx or Flask-Limiter)
- [ ] Implement JWT authentication
- [ ] Validate all user inputs
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Implement API key rotation

---

## 🧪 Testing in Production

**Health check:**
```bash
curl https://parkngo.yourdomain.com/api/health
```

**Load testing with Apache Bench:**
```bash
ab -n 1000 -c 10 https://parkngo.yourdomain.com/api/stats
```

**Load testing with wrk:**
```bash
wrk -t4 -c100 -d30s https://parkngo.yourdomain.com/api/health
```

---

## 📈 Scaling

### Horizontal Scaling

**Docker Swarm:**
```bash
docker swarm init
docker stack deploy -c docker-compose.yml parkngo
docker service scale parkngo_parkngo-api=5
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: parkngo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: parkngo-api
  template:
    metadata:
      labels:
        app: parkngo-api
    spec:
      containers:
      - name: parkngo-api
        image: parkngo-api:latest
        ports:
        - containerPort: 5000
```

### Vertical Scaling

**Increase workers:**
```bash
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

**Increase resources (Docker):**
```yaml
services:
  parkngo-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

**`.github/workflows/deploy.yml`:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t parkngo-api:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push parkngo-api:${{ github.sha }}
      
      - name: Deploy to server
        run: |
          ssh user@server "docker pull parkngo-api:${{ github.sha }} && docker-compose up -d"
```

---

## 📱 Production Startup Script

**Use the provided start script:**
```powershell
# Windows
.\start.ps1

# Linux/Mac
chmod +x start.sh
./start.sh
```

---

## 🆘 Troubleshooting Production Issues

**Check logs:**
```bash
# Docker
docker logs parkngo-api -f

# System service
journalctl -u parkngo -f

# Application logs
tail -f logs/parkngo.log
```

**Restart services:**
```bash
# Docker Compose
docker-compose restart parkngo-api

# System service
sudo systemctl restart parkngo
```

**Database connection issues:**
```bash
# Check Firebase connectivity
python -c "from services import firebase_service; print(firebase_service.db)"

# Check Masumi services
curl http://localhost:3001/docs
curl http://localhost:3000/docs
```

---

## 📞 Support & Maintenance

**Regular tasks:**
- Monitor error logs daily
- Check disk space weekly
- Update dependencies monthly
- Review security advisories
- Backup Firebase data
- Test disaster recovery

**Emergency contacts:**
- Repository: https://github.com/DhanushKenkiri/Parkngo
- Issues: Create GitHub issue
- Gemini API: https://ai.google.dev/support
- Masumi Network: https://github.com/MasumiNetwork
