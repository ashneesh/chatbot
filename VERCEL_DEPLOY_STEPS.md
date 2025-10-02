# Vercel Deployment - Connect Frontend to Backend

## ✅ Your Backend is Ready!

Your backend is live at: `https://chatbot-gome.onrender.com`

Health check confirmed:

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

---

## 🔧 Configuration Fixed

I've updated the environment variable in `App.tsx` to match `vercel.json`:

- ✅ Changed `VITE_WS_BASE_URL` → `VITE_WS_URL`
- ✅ Your `vercel.json` already has the correct backend URL

---

## 🚀 Deploy to Vercel

### Option 1: Redeploy via Vercel Dashboard (Recommended)

1. **Go to your Vercel dashboard**: https://vercel.com/dashboard
2. **Find your project**
3. **Click "Settings"**
4. **Go to "Environment Variables"**
5. **Add/Update these variables**:
   ```
   VITE_API_URL = https://chatbot-gome.onrender.com
   VITE_WS_URL = wss://chatbot-gome.onrender.com
   ```
6. **Go to "Deployments"** tab
7. **Click the 3 dots (⋮)** on the latest deployment
8. **Click "Redeploy"**
9. **Check "Use existing Build Cache" = OFF** (to ensure fresh build)
10. **Click "Redeploy"**

### Option 2: Push to Git (Auto-deploy)

If you have auto-deploy enabled:

```bash
# Commit the changes
git add .
git commit -m "Fix WebSocket connection for Vercel deployment"
git push origin main

# Vercel will automatically redeploy
```

### Option 3: Deploy via CLI

```bash
# Navigate to frontend directory
cd frontend

# Deploy to production
vercel --prod

# When prompted, confirm environment variables
```

---

## 🧪 Test the Connection

After deployment:

1. **Open your Vercel URL** (e.g., `https://your-app.vercel.app`)
2. **Open Browser DevTools** (F12)
3. **Check Console** - you should see:
   ```
   WebSocket connected
   wss://chatbot-gome.onrender.com/ws/chat/session_... url
   ```
4. **Check Connection Status** - should show "Connected" (green dot)
5. **Send a test message** - "Hello"
6. **Verify response** from the bot

---

## 🐛 If Still Not Connecting

### Check 1: Verify Environment Variables in Vercel

```bash
# Using Vercel CLI
vercel env ls

# Should show:
# VITE_API_URL    Production    https://chatbot-gome.onrender.com
# VITE_WS_URL     Production    wss://chatbot-gome.onrender.com
```

### Check 2: View Build Logs

1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on the latest deployment
3. Check "Build Logs" for any errors
4. Look for: "Building for production..." message

### Check 3: Check Browser Console

Open DevTools and look for:

- ✅ `WebSocket connected` - Good!
- ❌ `WebSocket error: ...` - Check URL
- ❌ `Failed to connect` - Check backend status

### Check 4: Test WebSocket Directly

In browser console on your Vercel site:

```javascript
const ws = new WebSocket("wss://chatbot-gome.onrender.com/ws/chat/test123");
ws.onopen = () => console.log("Connected!");
ws.onerror = (e) => console.error("Error:", e);
ws.onmessage = (e) => console.log("Message:", e.data);
```

---

## 📋 Checklist

- [ ] Backend is running at `https://chatbot-gome.onrender.com` ✅ (Already confirmed)
- [ ] `/health` endpoint returns healthy status ✅ (Already confirmed)
- [ ] Updated `App.tsx` to use `VITE_WS_URL` ✅ (Just fixed)
- [ ] `vercel.json` has correct backend URL ✅ (Already set)
- [ ] Environment variables set in Vercel Dashboard
- [ ] Redeployed frontend on Vercel
- [ ] Tested connection in browser
- [ ] WebSocket shows "Connected"
- [ ] Can send and receive messages

---

## 🎯 Expected Behavior

When everything works:

1. **Page loads**: Shows "Welcome to Healthcare Assistant"
2. **Status indicator**: Green dot + "Connected"
3. **Can type**: Input field is enabled
4. **Send message**: Bot responds within 1-2 seconds
5. **Console logs**:
   ```
   wss://chatbot-gome.onrender.com/ws/chat/session_... url
   WebSocket connected
   Received message: {type: "system", message: "Connected to healthcare chatbot..."}
   ```

---

## 🔗 URLs Reference

- **Backend API**: https://chatbot-gome.onrender.com
- **Backend Health**: https://chatbot-gome.onrender.com/health
- **Backend Docs**: https://chatbot-gome.onrender.com/docs
- **WebSocket**: wss://chatbot-gome.onrender.com/ws/chat/{session_id}
- **Frontend**: (Your Vercel URL)

---

## 💡 Pro Tips

1. **Clear Browser Cache**: Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
2. **Check Render Status**: Your backend might spin down after inactivity (free tier)
3. **First Request Slow**: Render free tier has cold starts (~30s)
4. **WebSocket Timeouts**: Backend has 30s timeout, then auto-reconnect
5. **Monitor Logs**:
   - Backend: Check Render dashboard
   - Frontend: Check Vercel dashboard

---

## 🆘 Still Having Issues?

Run these diagnostic commands:

```bash
# Test backend health
curl https://chatbot-gome.onrender.com/health

# Test chat endpoint
curl -X POST https://chatbot-gome.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"test123"}'

# Test WebSocket (using wscat)
npm install -g wscat
wscat -c wss://chatbot-gome.onrender.com/ws/chat/test123
```

Share the output if you need help debugging!
