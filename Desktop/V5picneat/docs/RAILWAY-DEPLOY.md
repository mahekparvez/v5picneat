# PicNEat V1 Backend - Railway Deployment

## 🚀 Quick Deploy to Railway

### Method 1: Railway CLI (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Add environment variables (use your own keys; never commit them)
railway variables set GROQ_API_KEY=your_groq_api_key_here
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_KEY=your_supabase_anon_key_here
railway variables set USDA_API_KEY=your_usda_key_or_DEMO_KEY

# 6. Get your URL
railway domain
```

### Method 2: Railway Dashboard

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Connect GitHub and select your repo
4. Railway auto-detects Python
5. Click "Deploy"
6. Add environment variables in Settings → Variables

### Method 3: Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/picneat-backend)

---

## 🔧 Environment Variables Needed

Add these in Railway Dashboard → Settings → Variables (use your own keys; never commit real keys):

```
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
USDA_API_KEY=your_usda_key_or_DEMO_KEY
```

---

## 📱 After Deployment

1. Railway gives you a URL like: `https://picneat-backend-production.up.railway.app`
2. Test it: `curl https://your-url.railway.app/health`
3. Update your iOS app to use this URL
4. You're live! 🎉

---

## 💰 Cost

Railway free tier includes:
- $5 of usage per month
- 500 hours of execution time
- Perfect for development and demos!

Your app will cost ~$0.50-2/month depending on usage.

---

## 🐛 Troubleshooting

**Build fails?**
- Check `railway logs` for errors
- Verify all files are committed to git

**API doesn't work?**
- Check environment variables are set
- View logs: `railway logs`
- Test health endpoint first

**Need help?**
- Railway docs: https://docs.railway.app
- Logs: `railway logs --follow`
