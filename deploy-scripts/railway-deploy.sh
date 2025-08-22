#!/bin/bash

# Railway Backend Deployment Script
# Run this script to deploy backend to Railway

echo "🚀 Deploying Backend to Railway..."

# Navigate to backend directory  
cd ../backend

# Create railway.json if it doesn't exist
cat > railway.json << EOF
{
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "sleepApplication": false,
    "numReplicas": 1
  }
}
EOF

# Create Procfile for Railway
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > Procfile

echo "📦 Backend prepared for Railway deployment"
echo "🔗 Deploy using Railway CLI or connect GitHub repo"
echo "⚠️ Remember to set environment variables in Railway dashboard:"
echo "   - MONGO_URL"
echo "   - DB_NAME" 
echo "   - CORS_ORIGINS"