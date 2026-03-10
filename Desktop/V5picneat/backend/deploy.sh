#!/bin/bash
# PicNEat Railway Deploy Script
# Reads API keys from backend/.env (never put real keys in this file).
# Copy backend/.env.example to backend/.env and fill in your keys.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
ENV_FILE="$BACKEND_DIR/.env"

echo "🚂 PicNEat - Railway Deployment Script"
echo "======================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI ready"
echo ""

# Load env from backend/.env (optional; keys can also be set in Railway dashboard)
if [ -f "$ENV_FILE" ]; then
    echo "🔐 Loading variables from $ENV_FILE ..."
    set -a
    # shellcheck source=/dev/null
    source "$ENV_FILE"
    set +a
    echo "   GROQ_API_KEY: set"
    echo "   SUPABASE_URL: set"
    echo "   SUPABASE_KEY: set"
    echo "   USDA_API_KEY: set"
else
    echo "⚠️  No $ENV_FILE found. Copy .env.example to .env and add your keys, or set variables in Railway dashboard."
    echo "   Continuing; you can set variables manually in Railway after deploy."
fi

# Login
echo ""
echo "🔐 Logging in to Railway..."
railway login

# Initialize project (if not already)
echo "🎯 Initializing project..."
railway init

# Set environment variables from env (only if set)
echo "🔧 Setting environment variables on Railway..."
[ -n "$GROQ_API_KEY" ]    && railway variables set GROQ_API_KEY="$GROQ_API_KEY"
[ -n "$SUPABASE_URL" ]    && railway variables set SUPABASE_URL="$SUPABASE_URL"
[ -n "$SUPABASE_KEY" ]    && railway variables set SUPABASE_KEY="$SUPABASE_KEY"
[ -n "$USDA_API_KEY" ]    && railway variables set USDA_API_KEY="$USDA_API_KEY"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get the URL
echo ""
echo "🎉 Deployment complete!"
echo "📍 Getting your URL..."
railway domain

echo ""
echo "✅ Your PicNEat backend is now live!"
echo "🧪 Test it with:"
echo "   curl https://YOUR_URL/health"
echo ""
