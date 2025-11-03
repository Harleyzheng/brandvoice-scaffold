# BrandVoice Studio - Deployment Guide

## Overview

This guide covers deploying the BrandVoice Studio web application with both frontend and backend components.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Browser   │ ───▶ │  React App   │ ───▶ │  FastAPI Backend│
│  (Client)   │      │ (Port 3000)  │      │   (Port 8000)   │
└─────────────┘      └──────────────┘      └─────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Python Modules  │
                                            │ (Processing)    │
                                            └─────────────────┘
```

## Local Development Setup

### Prerequisites

- Node.js 16+
- Python 3.11+
- npm or yarn
- pip

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd brandvoice-scaffold

# Install Python dependencies
pip install -r requirements.txt
pip install -r api/requirements.txt

# Install frontend dependencies
cd web
npm install
cd ..
```

### Step 2: Environment Configuration

Create a `.env` file in the project root:

```bash
OPUSCLIP_API_KEY=your_opusclip_key
OPENAI_API_KEY=your_openai_key
```

### Step 3: Run Development Servers

**Terminal 1 - Backend:**
```bash
python api/server.py
```

**Terminal 2 - Frontend:**
```bash
cd web
npm start
```

Access the application at `http://localhost:3000`

---

## Production Deployment

### Option 1: Docker Deployment (Recommended)

Create `Dockerfile` in project root:

```dockerfile
# Multi-stage build

# Stage 1: Build React app
FROM node:18-alpine AS frontend-build
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r api/requirements.txt

# Copy Python code
COPY . .

# Copy built frontend
COPY --from=frontend-build /app/web/build /app/web/build

# Install playwright
RUN playwright install

# Expose ports
EXPOSE 8000

# Start backend (serves both API and frontend)
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  brandvoice:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPUSCLIP_API_KEY=${OPUSCLIP_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./output:/app/output
      - ./training_data:/app/training_data
      - ./uploads:/app/uploads
    restart: unless-stopped
```

Deploy:

```bash
docker-compose up -d
```

### Option 2: Traditional Server Deployment

#### Backend Deployment (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r api/requirements.txt
playwright install

# Create systemd service
sudo nano /etc/systemd/system/brandvoice-api.service
```

Service file content:

```ini
[Unit]
Description=BrandVoice API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/brandvoice
Environment="PATH=/var/www/brandvoice/venv/bin"
ExecStart=/var/www/brandvoice/venv/bin/uvicorn api.server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl enable brandvoice-api
sudo systemctl start brandvoice-api
```

#### Frontend Deployment

```bash
# Build React app
cd web
npm install
npm run build

# Copy to nginx
sudo cp -r build/* /var/www/html/brandvoice/
```

Configure nginx (`/etc/nginx/sites-available/brandvoice`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/html/brandvoice;
        try_files $uri /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/brandvoice /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Cloud Platform Deployment

#### Vercel (Frontend) + Render (Backend)

**Frontend (Vercel):**

1. Push code to GitHub
2. Import project in Vercel
3. Configure:
   - Framework: Create React App
   - Root Directory: `web`
   - Build Command: `npm run build`
   - Output Directory: `build`

**Backend (Render):**

1. Create new Web Service
2. Configure:
   - Build Command: `pip install -r requirements.txt && pip install -r api/requirements.txt`
   - Start Command: `uvicorn api.server:app --host 0.0.0.0 --port $PORT`
3. Add environment variables

Update CORS in `api/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],
    # ... rest of config
)
```

---

## Environment Variables

Required environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPUSCLIP_API_KEY` | OpusClip API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key for AI analysis | Optional |
| `PORT` | Server port (default: 8000) | No |

---

## Monitoring & Maintenance

### Logs

**Development:**
```bash
# Backend logs
tail -f api.log

# Frontend logs
# Check browser console
```

**Production:**
```bash
# System service logs
sudo journalctl -u brandvoice-api -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Health Check

Add to `api/server.py`:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### Backups

Backup important directories:

```bash
# Backup output and training data
tar -czf backup-$(date +%Y%m%d).tar.gz output/ training_data/
```

---

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure appropriate origins in production
3. **File Upload**: Implement file size limits and validation
4. **Rate Limiting**: Add rate limiting to API endpoints
5. **HTTPS**: Always use HTTPS in production
6. **Authentication**: Consider adding user authentication for production

---

## Scaling

### Horizontal Scaling

Use a load balancer (nginx/HAProxy) with multiple backend instances:

```yaml
# docker-compose.yml
services:
  brandvoice-1:
    build: .
    # ... config

  brandvoice-2:
    build: .
    # ... config

  load-balancer:
    image: nginx
    # ... load balancer config
```

### Database Integration

For production, replace in-memory storage with a database:

```python
# Use PostgreSQL or MongoDB for job storage
# Example with SQLAlchemy:
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/brandvoice')
```

---

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version`
- Verify dependencies: `pip list`
- Check port availability: `lsof -i :8000`

**Frontend build fails:**
- Clear cache: `npm cache clean --force`
- Remove node_modules: `rm -rf node_modules && npm install`

**CORS errors:**
- Verify backend CORS configuration
- Check frontend API endpoint URLs

---

## Support

For issues and questions, please refer to:
- Project README
- API documentation at `/docs` (FastAPI auto-generated)
- GitHub issues

---

**Last Updated:** November 2025


