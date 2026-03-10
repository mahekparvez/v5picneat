#!/bin/bash

# Pic N Eat V2 - Quick Setup Script

echo "=============================================="
echo "🍎 Pic N Eat V2 - Quick Setup"
echo "=============================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if PostgreSQL is running
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL found"
else
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL 15+"
    echo "   macOS: brew install postgresql@15"
    echo "   Ubuntu: sudo apt install postgresql-15"
    exit 1
fi

echo ""
echo "Setting up backend..."
echo "----------------------------------------------"

cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --quiet -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    secret_key=$(openssl rand -hex 32)
    sed -i.bak "s/your-secret-key-here-generate-with-openssl-rand-hex-32/$secret_key/" .env
    
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - DATABASE_URL (PostgreSQL connection string)"
    echo "   - USDA_API_KEY (get from https://fdc.nal.usda.gov/api-key-signup.html)"
    echo "   - S3 credentials (CloudFlare R2 or AWS S3)"
    echo ""
    echo "Press Enter when you've updated .env..."
    read -r
fi

# Create database
echo "Setting up database..."
python3 -c "from app.db.base import init_db; init_db()" 2>/dev/null && echo "✓ Database initialized" || echo "⚠️  Database initialization failed - check DATABASE_URL in .env"

echo ""
echo "=============================================="
echo "✅ Backend Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Train ML model:"
echo "   cd ../ml-pipeline"
echo "   python scripts/preprocess_dataset.py"
echo "   python scripts/train.py"
echo "   cp models/food_classifier.pth ../backend/models/"
echo ""
echo "2. Start backend:"
echo "   cd ../backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Access API:"
echo "   http://localhost:8000/docs"
echo ""
echo "4. Or use Docker:"
echo "   cd .."
echo "   docker-compose up"
echo ""
