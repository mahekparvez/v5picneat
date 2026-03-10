# ⚡ 5-Minute Quick Start

## Prerequisites
- Docker installed
- USDA FDC API key: https://fdc.nal.usda.gov/api-key-signup.html
- AWS account with S3 bucket

## Step 1: Configure (2 min)

```bash
cd backend
cp .env.template .env
```

Edit `.env` and add:
```bash
USDA_FDC_API_KEY=your-usda-key-here
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

## Step 2: Start (1 min)

```bash
docker-compose up -d
docker-compose exec backend python -c "from app.core.database import create_tables; create_tables()"
```

## Step 3: Test (2 min)

Visit: http://localhost:8000/docs

Click "Try it out" on:
1. `POST /auth/register` - Create account
2. `POST /auth/login` - Get token
3. `POST /food/upload` - Upload food image

## ✅ Done!

Your backend is running with:
- ✅ User authentication
- ✅ Food upload & recognition
- ✅ USDA nutrition data
- ✅ Points & gamification
- ✅ S3 storage

## Next: Train Your Model

```bash
cd ../ml_model
pip install -r requirements.txt
python prepare_dataset.py  # Follow instructions
python train_model.py       # Train (2-4 hours)
cp checkpoints/best_model.pth ../backend/models/
docker-compose restart backend
```

## Deploy to Production

**Railway** (easiest):
```bash
railway init
railway add --database postgres
railway variables set USDA_FDC_API_KEY=your-key
railway variables set AWS_ACCESS_KEY_ID=your-key
railway variables set AWS_SECRET_ACCESS_KEY=your-secret
railway up
```

**Your API is live!** 🚀

See full README.md for detailed docs.
