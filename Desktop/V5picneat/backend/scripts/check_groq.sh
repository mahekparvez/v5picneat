#!/bin/bash
# Run from backend/: ./scripts/check_groq.sh
# Or: bash scripts/check_groq.sh
# Verifies GROQ_API_KEY works (backend must be running with new code).

set -e
BASE="${1:-http://localhost:8000}"
echo "Checking Groq key via $BASE/check-groq ..."
curl -s "$BASE/check-groq" | python3 -m json.tool
echo ""
