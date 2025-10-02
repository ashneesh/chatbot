# Healthcare Chatbot Deployment Guide

This guide covers deploying your healthcare chatbot frontend and backend with proper API connection.

## Architecture Overview

- **Frontend**: React + TypeScript + Vite (deployed on Vercel or via Docker)
- **Backend**: FastAPI (deployed on Railway or via Docker)
- **Rasa**: NLU/Dialog Management (deployed with backend)

## Option 1: Docker Compose Deployment (Recommended for Testing)

### Prerequisites

- Docker and Docker Compose installed
- All services run in containers with internal networking

### Steps

1. **Build and start all services**:

   ```bash
   cd /path/to/healthcare-chatbot-4
   docker-compose -f docker/docker-compose.prod.yml up --build
   ```

2. **Access the application**:

   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Rasa: http://localhost:5005

3. **The nginx proxy handles routing**:
   - `/api/*` → Backend (port 8000)
   - `/ws/*` → WebSocket connections
   - All other routes → Frontend

### Configuration

No environment variables needed - services communicate via Docker network names:

- Frontend connects to `http://backend:8000`
- Backend connects to `http://rasa-core:5005`

---

## Option 2: Separate Cloud Deployment (Production)

### A. Deploy Backend to Railway

1. **Prerequisites**:

   - GitHub account
   - Railway account (https://railway.app)
   - Push your code to GitHub

2. **Setup Railway Project**:

   ```bash
   # Install Railway CLI (optional)
   npm install -g @railway/cli
   railway login
   ```

3. **Create New Project**:

   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your healthcare-chatbot repository
   - Railway will detect `railway.json` configuration

4. **Configure Environment Variables** in Railway Dashboard:

   ```env
   PORT=8000
   RASA_SERVER_URL=http://localhost:5005
   DEBUG=false
   ```

5. **Get your Railway URL**:

   - After deployment, Railway provides a URL like: `https://your-app.railway.app`
   - Save this URL - you'll need it for frontend configuration

6. **Test Backend**:
   ```bash
   curl https://your-app.railway.app/health
   ```

### B. Deploy Frontend to Vercel

1. **Prerequisites**:

   - Vercel account (https://vercel.com)
   - Vercel CLI (optional)

2. **Update `vercel.json`** with your backend URL:

   ```json
   {
     "build": {
       "env": {
         "VITE_API_URL": "https://your-backend-url.railway.app",
         "VITE_WS_URL": "wss://your-backend-url.railway.app"
       }
     }
   }
   ```

3. **Deploy via Vercel Dashboard**:

   - Go to https://vercel.com
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
   - Add Environment Variables:
     - `VITE_API_URL`: `https://your-backend-url.railway.app`
     - `VITE_WS_URL`: `wss://your-backend-url.railway.app`
   - Click "Deploy"

4. **Deploy via CLI** (Alternative):

   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Navigate to frontend directory
   cd frontend

   # Set environment variables
   export VITE_API_URL=https://your-backend-url.railway.app
   export VITE_WS_URL=wss://your-backend-url.railway.app

   # Deploy
   vercel --prod
   ```

### C. Update CORS Settings

Update your backend's CORS to allow your Vercel domain:

**File**: `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "http://localhost",
        "https://your-frontend.vercel.app",  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## Option 3: Build and Deploy Frontend Manually

### Build Frontend Locally

```bash
cd frontend

# Set environment variables for production
export VITE_API_URL=https://your-backend-url.railway.app
export VITE_WS_URL=wss://your-backend-url.railway.app

# Install dependencies
npm install

# Build for production
npm run build

# Output will be in the 'dist' folder
```

### Deploy to Any Static Host

The `dist` folder can be deployed to:

- **Netlify**: Drag and drop the `dist` folder
- **AWS S3 + CloudFront**: Upload to S3 bucket
- **GitHub Pages**: Push dist folder to gh-pages branch
- **Nginx/Apache**: Copy dist folder to web server

---

## Environment Variables Reference

### Frontend (.env or build-time variables)

```env
VITE_API_URL=http://localhost:8000              # Backend API base URL
VITE_WS_URL=ws://localhost:8000                  # WebSocket URL
```

### Backend

```env
PORT=8000                                        # Server port
RASA_SERVER_URL=http://localhost:5005           # Rasa server URL
RASA_ACTION_SERVER_URL=http://localhost:5055    # Rasa actions server
DEBUG=false                                      # Debug mode
DATABASE_URL=postgresql://...                    # Optional: Database connection
```

---

## Testing the Connection

### 1. Test Backend Health

```bash
curl https://your-backend-url.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-10-02T...",
  "services": {
    "api": "healthy",
    "websocket": "healthy",
    "rasa": "healthy"
  }
}
```

### 2. Test Chat Endpoint

```bash
curl -X POST https://your-backend-url.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test123"}'
```

### 3. Test Frontend Connection

1. Open your deployed frontend URL
2. Open browser DevTools (F12) → Console
3. Send a test message in the chat
4. Check Network tab for API calls to your backend

---

## Troubleshooting

### Frontend Can't Connect to Backend

**Problem**: CORS errors in browser console

**Solution**:

1. Check CORS settings in `backend/app/main.py`
2. Add your frontend domain to `allow_origins`
3. Redeploy backend

### WebSocket Connection Fails

**Problem**: WebSocket upgrades fail

**Solution**:

1. Ensure you're using `wss://` (not `ws://`) for HTTPS backends
2. Check proxy/load balancer WebSocket support
3. Railway supports WebSockets by default

### Backend Can't Find Rasa

**Problem**: Backend returns "Rasa unavailable"

**Solution**:

1. Check Rasa service is running: `docker ps` or Railway logs
2. Verify `RASA_SERVER_URL` environment variable
3. In production, Rasa might take 30-60s to start

### Build Fails on Vercel

**Problem**: TypeScript or Vite build errors

**Solution**:

1. Check Node version (should be 18+)
2. Ensure all dependencies are in `package.json`
3. Check build logs for specific errors

---

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured correctly
- [ ] CORS configured with frontend domain
- [ ] Health checks passing
- [ ] WebSocket connections working
- [ ] Database connected (if using)
- [ ] SSL/HTTPS enabled (handled by Railway/Vercel)
- [ ] API rate limiting configured (optional)
- [ ] Monitoring/logging setup (optional)

---

## Architecture Diagram

```
┌─────────────────┐
│   Vercel        │
│   (Frontend)    │
│   React + Vite  │
└────────┬────────┘
         │ HTTPS/WSS
         │
┌────────▼────────────────────────┐
│   Railway                       │
│   ┌──────────────────────────┐  │
│   │  FastAPI Backend         │  │
│   │  Port 8000               │  │
│   └──────────┬───────────────┘  │
│              │                   │
│   ┌──────────▼───────────────┐  │
│   │  Rasa Server             │  │
│   │  Port 5005               │  │
│   └──────────┬───────────────┘  │
│              │                   │
│   ┌──────────▼───────────────┐  │
│   │  Rasa Actions            │  │
│   │  Port 5055               │  │
│   └──────────────────────────┘  │
└─────────────────────────────────┘
```

---

## Monitoring Your Deployment

### Railway

- View logs: Railway Dashboard → Your Project → Deployments
- Monitor metrics: CPU, Memory, Network usage
- Check health endpoint: `/health`

### Vercel

- View logs: Vercel Dashboard → Your Project → Deployments
- Monitor performance: Vercel Analytics
- Check build logs for any issues

---

## Cost Considerations

### Free Tier Limits:

- **Railway**: $5 free credit/month (enough for small apps)
- **Vercel**: Unlimited bandwidth for personal projects
- **Railway + Vercel**: Best combination for hobby projects

### Scaling:

- Backend (Railway): Scales based on your plan
- Frontend (Vercel): Auto-scales globally on CDN
- Consider separating Rasa service if resource-intensive

---

## Next Steps

1. **Deploy backend to Railway**
2. **Get backend URL**
3. **Update frontend environment variables**
4. **Deploy frontend to Vercel**
5. **Test the connection**
6. **Monitor and iterate**

Need help? Check the logs in Railway/Vercel dashboards for detailed error messages.
