# 🚀 PicNEat v5 - Complete Production Stack

> **Snap a photo → Get accurate calories → Earn FUEL → Stay motivated!**

PicNEat is a nutrition tracking app for Purdue students that uses AI vision to identify food and estimate calories instantly. The unique gamification system (Neil the astronaut, streaks, badges) keeps users engaged daily.

---

## ✨ What's New in V5

- ✅ **Complete FastAPI backend** with Groq Vision AI
- ✅ **Supabase database** with 6 production tables
- ✅ **Purdue dining menu** priority matching
- ✅ **USDA nutrition data** integration
- ✅ **Production-ready** deployment configs
- ✅ **iOS integration code** ready to use

---

## 🏗️ Architecture

### **Backend** (FastAPI + Python)
- **Food Detection**: Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct)
- **Database**: Supabase PostgreSQL
- **Nutrition Data**: Purdue menu → USDA FDC API fallback
- **Hosting**: Railway (auto-scaling, HTTPS)

### **iOS** (SwiftUI + Swift)
- **UI**: Neil-themed gamification
- **Camera**: Native PhotosPicker
- **API**: URLSession with async/await
- **State**: SwiftUI + Combine

### **Database Schema**
```sql
users           # User accounts
meal_logs       # Food detection history
purdue_menu     # Campus dining data (17 items)
user_progress   # Fuel, streaks, badges
food_corrections # V2 training data
nutrition_cache # API response cache
```

---

## 🚀 Quick Start

### **1. Backend Setup** (5 minutes)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
# Server at http://localhost:8000
```

### **2. iOS Setup** (2 minutes)

```bash
cd ios

# Open in Xcode
open PicNEat.xcodeproj

# Update API URL in PicNEatAPI.swift:
let baseURL = "http://localhost:8000"  # For testing
# Or: "https://your-app.railway.app"   # Production
```

### **3. Test End-to-End**

1. Start backend: `python main.py`
2. Run iOS app in Simulator
3. Take photo of food
4. See instant calorie analysis! 🎉

---

## 📱 Features

### **V1 (Current)**
- ✅ AI food detection (Groq Vision)
- ✅ Portion estimation (grams)
- ✅ Purdue dining menu matching
- ✅ Calorie + macro tracking
- ✅ Streak system
- ✅ Fuel currency
- ✅ Badge progression
- ✅ Leaderboards

### **V2 (Planned)**
- 🔄 Custom CoreML model (trained on Purdue photos)
- 🔄 Barcode scanning
- 🔄 Apple Watch widget
- 🔄 Social challenges

---

## 🎯 API Endpoints

### **POST /analyze-meal**
Upload food image, get nutrition analysis.

**Request:**
```bash
curl -X POST http://localhost:8000/analyze-meal \
  -F 'file=@pizza.jpg'
```

**Response:**
```json
{
  "foods": [{
    "name": "pizza, cheese, regular crust",
    "portion_grams": 125.3,
    "calories": 285,
    "protein": 15.0,
    "carbs": 45.1,
    "fats": 12.5,
    "confidence": 0.91,
    "source": "purdue"
  }],
  "total_calories": 285,
  "analysis_time_ms": 2847
}
```

### **GET /health**
Health check endpoint.

---

## 🔧 Environment Variables

### **Backend (.env)**
Copy `backend/.env.example` to `backend/.env` and add your real keys (never commit `.env`):

```bash
# Groq API
GROQ_API_KEY=your_groq_api_key_here

# Supabase - PicNEat Project
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# USDA FDC API
USDA_API_KEY=your_usda_api_key_here
```

### **iOS (PicNEatAPI.swift)**
```swift
private let baseURL = "https://your-app.railway.app"
```

---

## 🚂 Deployment

### **Backend to Railway**
```bash
cd backend

# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables (use values from your backend/.env; never commit keys)
railway variables set GROQ_API_KEY=your_groq_api_key_here
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_KEY=your_supabase_anon_key_here
railway variables set USDA_API_KEY=your_usda_key_or_DEMO_KEY

# Get your live URL
railway domain
```

### **iOS to TestFlight**
1. Update `baseURL` to Railway production URL
2. Archive in Xcode (Product → Archive)
3. Upload to App Store Connect
4. Submit for TestFlight review
5. Invite beta testers!

---

## 📊 Tech Stack

**Backend:**
- FastAPI 0.109.0
- Supabase (PostgreSQL)
- Groq Vision API
- USDA FDC API
- Railway hosting

**iOS:**
- SwiftUI
- Combine
- URLSession
- PhotosPicker
- CoreLocation

**Database:**
- PostgreSQL 17 (Supabase)
- 6 tables with indexes
- Row Level Security enabled

---

## 📁 Project Structure

```
v5picneat/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   ├── Procfile            # Railway config
│   └── railway.json        # Railway build config
│
├── ios/
│   ├── PicNEat/
│   │   ├── Views/          # SwiftUI screens
│   │   ├── Models/         # Data models
│   │   ├── Services/       # API client
│   │   └── Assets/         # Images, Neil animations
│   └── PicNEat.xcodeproj
│
└── docs/
    ├── SETUP-COMPLETE.md    # Complete setup guide
    ├── RAILWAY-DEPLOY.md    # Deployment guide
    ├── IOS-INTEGRATION.md   # iOS integration
    └── PicNEat_PRD.pdf     # Product requirements
```

---

## 🧪 Testing

### **Backend**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test food detection
curl -X POST http://localhost:8000/analyze-meal \
  -F 'file=@test-pizza.jpg'
```

### **iOS**
```swift
// In Xcode
let api = PicNEatAPI()
let result = try await api.analyzeMeal(image: testImage)
print("Detected: \(result.foods[0].name)")
```

---

## 💰 Costs

- **Groq API**: FREE (unlimited during beta)
- **Supabase**: FREE (up to 500MB database)
- **USDA API**: FREE (1000 requests/hour)
- **Railway**: $5/month free credits (~500 requests)

**Total: $0-2/month** for development and testing!

---

## 🎓 For StarkHacks

**What to Demo:**
1. ✅ Take photo of dining hall food
2. ✅ Show instant AI detection
3. ✅ Highlight Purdue menu match
4. ✅ Display calorie breakdown
5. ✅ Show Neil celebration animation
6. ✅ Demonstrate streak tracking

**Key Talking Points:**
- "Uses Groq Vision AI for Cal AI-level accuracy"
- "Prioritizes Purdue dining menu for campus accuracy"
- "Gamification keeps users engaged daily"
- "Built in 3 days using modern stack"

---

## 👥 Team

**Mahek Parvez**
- Backend: FastAPI + Groq Vision
- Database: Supabase schema design
- iOS: SwiftUI integration
- Deployment: Railway production setup

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- Groq for Vision API access
- Supabase for database hosting
- USDA for FoodData Central
- Purdue Dining for menu data
- Claude for development assistance

---

## 🔗 Links

- **GitHub**: https://github.com/mahekparvez/v5picneat
- **Railway**: [Your Railway URL]
- **Supabase**: https://supabase.com/dashboard/project/rqkfivmphtutghokudgh
- **Groq**: https://console.groq.com

---

## 📞 Support

Questions? Found a bug?
- Open an issue on GitHub
- Email: mahek@purdue.edu (update this)

---

Made with ❤️ at Purdue University
