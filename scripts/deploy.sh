#!/bin/bash

# Healthcare Chatbot Deployment Helper Script

set -e

echo "🏥 Healthcare Chatbot Deployment Helper"
echo "========================================"
echo ""

# Function to display menu
show_menu() {
    echo "Select deployment option:"
    echo "1) Build frontend locally"
    echo "2) Test with Docker Compose"
    echo "3) Setup environment variables"
    echo "4) Deploy to Railway (backend)"
    echo "5) Deploy to Vercel (frontend)"
    echo "6) Exit"
    echo ""
}

# Function to build frontend
build_frontend() {
    echo "📦 Building frontend..."
    cd frontend
    
    read -p "Enter backend API URL (e.g., https://chatbot-gome.onrender.com): " api_url
    read -p "Enter WebSocket URL (e.g., wss://chatbot-gome.onrender.com): " ws_url
    
    export VITE_API_URL=$api_url
    export VITE_WS_URL=$ws_url
    
    echo "Installing dependencies..."
    npm install
    
    echo "Building..."
    npm run build
    
    echo "✅ Build complete! Output is in frontend/dist/"
    cd ..
}

# Function to test with Docker Compose
test_docker() {
    echo "🐳 Starting Docker Compose..."
    docker-compose -f docker/docker-compose.prod.yml up --build
}

# Function to setup environment variables
setup_env() {
    echo "⚙️  Environment Variable Setup"
    echo ""
    
    # Frontend
    if [ ! -f "frontend/.env.local" ]; then
        echo "Creating frontend/.env.local..."
        cat > frontend/.env.local << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
        echo "✅ Created frontend/.env.local with default values"
    else
        echo "ℹ️  frontend/.env.local already exists"
    fi
    
    # Backend
    if [ ! -f "backend/.env" ]; then
        echo "Creating backend/.env..."
        cat > backend/.env << EOF
PORT=8000
DEBUG=false
RASA_SERVER_URL=http://localhost:5005
RASA_ACTION_SERVER_URL=http://localhost:5055
LOG_LEVEL=INFO
EOF
        echo "✅ Created backend/.env with default values"
    else
        echo "ℹ️  backend/.env already exists"
    fi
    
    echo ""
    echo "📝 Edit these files to customize your configuration"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Railway Deployment"
    echo ""
    
    if ! command -v railway &> /dev/null; then
        echo "Railway CLI not found. Install it first:"
        echo "npm install -g @railway/cli"
        echo ""
        read -p "Would you like to install it now? (y/n): " install_cli
        if [ "$install_cli" = "y" ]; then
            npm install -g @railway/cli
        else
            echo "Please install Railway CLI manually and try again"
            return
        fi
    fi
    
    echo "Linking to Railway project..."
    railway login
    railway link
    
    echo "Deploying..."
    railway up
    
    echo "✅ Deployment initiated!"
    echo "Check status at: https://railway.app"
}

# Function to deploy to Vercel
deploy_vercel() {
    echo "▲ Vercel Deployment"
    echo ""
    
    if ! command -v vercel &> /dev/null; then
        echo "Vercel CLI not found. Install it first:"
        echo "npm install -g vercel"
        echo ""
        read -p "Would you like to install it now? (y/n): " install_cli
        if [ "$install_cli" = "y" ]; then
            npm install -g vercel
        else
            echo "Please install Vercel CLI manually and try again"
            return
        fi
    fi
    
    cd frontend
    
    echo "Deploying to Vercel..."
    vercel --prod
    
    cd ..
    
    echo "✅ Deployment complete!"
    echo "Your frontend is now live on Vercel"
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice [1-6]: " choice
    
    case $choice in
        1)
            build_frontend
            ;;
        2)
            test_docker
            ;;
        3)
            setup_env
            ;;
        4)
            deploy_railway
            ;;
        5)
            deploy_vercel
            ;;
        6)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done

