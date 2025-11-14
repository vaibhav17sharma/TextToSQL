#!/bin/bash

# Text to SQL Deployment Script
set -e

echo "🚀 Text to SQL Deployment Script"
echo "================================="

# Create logs directory
mkdir -p logs

# Function to deploy with Docker
deploy_docker() {
    echo "📦 Deploying with Docker..."
    
    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml up --build -d
    
    echo "✅ Docker deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 View logs: docker-compose -f docker-compose.prod.yml logs -f"
}

# Function to deploy with PM2
deploy_pm2() {
    echo "⚡ Deploying with PM2..."
    
    # Check if PM2 is installed
    if ! command -v pm2 &> /dev/null; then
        echo "Installing PM2..."
        npm install -g pm2
    fi
    
    # Check if serve is installed
    if ! command -v serve &> /dev/null; then
        echo "Installing serve..."
        npm install -g serve
    fi
    
    # Install backend dependencies
    echo "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    python install_llama.py
    cd ..
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    npm install -g pnpm
    pnpm install
    pnpm build
    cd ..
    
    # Start services with PM2
    pm2 delete ecosystem.config.js 2>/dev/null || true
    pm2 start ecosystem.config.js
    
    echo "✅ PM2 deployment complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 View logs: pm2 logs"
    echo "🔄 Manage: pm2 status | pm2 restart all | pm2 stop all"
}

# Function to deploy manually
deploy_manual() {
    echo "🔧 Manual deployment setup..."
    
    # Install backend dependencies
    echo "Setting up backend..."
    cd backend
    pip install -r requirements.txt
    python install_llama.py
    cd ..
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    npm install -g pnpm
    pnpm install
    pnpm build
    cd ..
    
    # Setup proxy server
    echo "Setting up proxy server..."
    npm install
    
    echo "✅ Manual setup complete!"
    echo ""
    echo "To start the services manually:"
    echo "1. Start PostgreSQL database"
    echo "2. Backend: cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo "3. Frontend with proxy: npm start (recommended)"
    echo "   OR separate: cd frontend && serve -s dist -l 3000"
}

# Main menu
echo "Choose deployment method:"
echo "1) Docker (Recommended)"
echo "2) PM2"
echo "3) Manual setup"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        deploy_docker
        ;;
    2)
        deploy_pm2
        ;;
    3)
        deploy_manual
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed successfully!"