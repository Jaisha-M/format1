#!/bin/bash

# Vercel Frontend Deployment Script
# Run this script to deploy frontend to Vercel

echo "🚀 Deploying Bruwrite ATS Resume Checker to Vercel..."

# Navigate to frontend directory
cd ../frontend

# Install dependencies
echo "📦 Installing dependencies..."
yarn install

# Build for production
echo "🏗️ Building production bundle..."
yarn build

# Deploy to Vercel
echo "☁️ Deploying to Vercel..."
npx vercel --prod

echo "✅ Deployment complete! Check Vercel dashboard for URL."
echo "🔗 Don't forget to update REACT_APP_BACKEND_URL in environment variables!"