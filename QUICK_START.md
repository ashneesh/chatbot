# Quick Start - Deploy Frontend & Backend

## 🚀 Fastest Way to Deploy

### Step 1: Deploy Backend to Railway (5 minutes)

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Select** this repository
5. **Wait** for deployment (Railway auto-detects `railway.json`)
6. **Copy** your Railway URL: `https://your-app.railway.app`

### Step 2: Deploy Frontend to Vercel (3 minutes)

1. **Update your backend URL** in `frontend/vercel.json`:

   ```json
   "build": {
     "env": {
       "VITE_API_URL": "https://your-app.railway.app",
       "VITE_WS_URL": "wss://your-app.railway.app"
     }
   }
   ```

2. **Go to Vercel**: https://vercel.com
3. **Import** this repository
4. **Configure**:
   - Root Directory: `frontend`
   - Framework: Vite
   - Environment Variables:
     - `VITE_API_URL` = `https://your-app.railway.app`
     - `VITE_WS_URL` = `wss://your-app.railway.app`
5. **Deploy!**

### Step 3: Test Connection

Visit your Vercel URL and try sending a message in the chat!

---

## 🐳 Local Testing with Docker

```bash
# Start everything
docker-compose -f docker/docker-compose.prod.yml up --build

# Access:
# - Frontend: http://localhost
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## 🔧 Manual Build & Deploy

### Build Frontend Locally

```bash
cd frontend

# Set your backend URL
export VITE_API_URL=https://your-backend.railway.app
export VITE_WS_URL=wss://your-backend.railway.app

# Build
npm install
npm run build

# Deploy the 'dist' folder to any static host
```

---

## 📝 Quick Commands

```bash
# Run deployment helper script
./scripts/deploy.sh

# Build frontend only
cd frontend && npm run build

# Test backend locally
cd backend && uvicorn app.main:app --reload

# Test frontend locally
cd frontend && npm run dev

# Docker compose (all services)
docker-compose -f docker/docker-compose.prod.yml up

# View backend logs (Railway)
railway logs

# View frontend logs (Vercel)
vercel logs
```

---

## ✅ Verify Deployment

### Test Backend

```bash
curl https://your-backend.railway.app/health
```

Should return:

```json
{
  "status": "healthy",
  "services": {
    "api": "healthy",
    "websocket": "healthy",
    "rasa": "healthy"
  }
}
```

### Test Chat

```bash
curl -X POST https://your-backend.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"test"}'
```

### Test Frontend

1. Open your Vercel URL
2. Open DevTools (F12) → Console
3. Send a test message
4. Check Network tab for API calls

---

## 🐛 Common Issues

### CORS Error

**Problem**: "Access to fetch blocked by CORS policy"

**Fix**: Update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",  # Add your domain
    ],
    # ...
)
```

### WebSocket Connection Failed

**Problem**: "WebSocket connection to 'ws://...' failed"

**Fix**: Make sure you're using `wss://` (not `ws://`) for HTTPS backends

### Rasa Not Responding

**Problem**: Backend returns "Rasa unavailable"

**Fix**: Wait 30-60 seconds after deployment for Rasa to initialize. Check Railway logs.

---

## 📚 More Details

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for comprehensive documentation.

---

## 💡 Tips

- **Development**: Use Docker Compose locally
- **Production**: Railway (backend) + Vercel (frontend)
- **Free tier**: Railway ($5/month credit) + Vercel (unlimited)
- **Monitoring**: Check Railway & Vercel dashboards for logs
- **Scaling**: Vercel auto-scales globally, Railway scales on demand

---

## 🆘 Need Help?

1. Check logs in Railway/Vercel dashboards
2. Test `/health` endpoint on backend
3. Check browser console for errors
4. Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

**Current Architecture**:

```
Frontend (Vercel) → HTTPS → Backend (Railway) → Rasa
```

All communication happens over HTTPS/WSS automatically! 🎉
