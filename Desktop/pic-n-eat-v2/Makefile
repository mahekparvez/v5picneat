# Pic N Eat V2 - Makefile

.PHONY: help setup dev test clean deploy

help:
	@echo "🍎 Pic N Eat V2 - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "  make setup       - Initial project setup"
	@echo "  make dev         - Start development servers"
	@echo "  make test        - Run all tests"
	@echo "  make lint        - Run linters"
	@echo "  make clean       - Clean up temp files"
	@echo "  make docker      - Start with Docker"
	@echo "  make deploy      - Deploy to production"
	@echo "  make model       - Train ML model"
	@echo ""

setup:
	@echo "Setting up Pic N Eat V2..."
	@chmod +x setup.sh
	@./setup.sh

dev:
	@echo "Starting development server..."
	@cd backend && source venv/bin/activate && uvicorn app.main:app --reload

test:
	@echo "Running tests..."
	@cd backend && source venv/bin/activate && pytest

lint:
	@echo "Running linters..."
	@cd backend && source venv/bin/activate && black app/ && flake8 app/

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

docker:
	@echo "Starting with Docker..."
	@docker-compose up

deploy:
	@echo "Deploying to production..."
	@cd backend && railway up

model:
	@echo "Training ML model..."
	@cd ml-pipeline && python scripts/preprocess_dataset.py && python scripts/train.py

install-deps:
	@echo "Installing all dependencies..."
	@cd backend && pip install -r requirements.txt
	@cd ml-pipeline && pip install -r requirements.txt

migrate:
	@echo "Running database migrations..."
	@cd backend && alembic upgrade head

init-db:
	@echo "Initializing database..."
	@cd backend && python -c "from app.db.base import init_db; init_db()"
