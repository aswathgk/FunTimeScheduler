#!/bin/bash

# FunTime Scheduler - Raspberry Pi Installation Script
# This script sets up the Flask application as a systemd service

set -e

echo "🍓 FunTime Scheduler - Raspberry Pi Setup"
echo "======================================="

# Configuration
APP_NAME="funtime-scheduler"
APP_DIR="/opt/${APP_NAME}"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
USER="aswath"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Run as aswath user with sudo when needed."
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-venv python3-pip git nginx supervisor curl

# Check if AdGuard Home is installed
if ! systemctl is-active --quiet AdguardHome; then
    echo "🛡️ AdGuard Home not found. Installing..."
    curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sudo sh -s -- -v
    
    echo "⚙️ Enabling AdGuard Home..."
    sudo systemctl enable AdguardHome
    sudo systemctl start AdguardHome
    
    echo "📋 AdGuard Home installed! Please configure it:"
    echo "   1. Open http://192.168.4.50:3000 in your browser"
    echo "   2. Complete the setup wizard"
    echo "   3. Use these credentials:"
    echo "      Username: aswathg"
    echo "      Password: agk12345"
    echo ""
    echo "Press Enter after configuring AdGuard Home to continue..."
    read -p ""
else
    echo "✅ AdGuard Home is already running"
fi

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files (assumes current directory contains the app)
echo "📋 Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📂 Creating data and log directories..."
mkdir -p data logs
chmod 755 data logs

# Set up environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
SECRET_KEY=your-secret-key-change-this-in-production-$(openssl rand -hex 32)
DEBUG=False
PORT=5000
HOST=0.0.0.0

# Authentication
ADMIN_USERNAME=aswath
ADMIN_PASSWORD=agk123

# AdGuard Configuration
ADGUARD_URL=http://192.168.4.50:3000
ADGUARD_USERNAME=aswathg
ADGUARD_PASSWORD=agk12345

# Database
DATABASE_PATH=data/scheduler.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOF
    
    # Generate a secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-change-this-in-production.*/your-secret-key-change-this-in-production-${SECRET_KEY}/" .env
    
    echo "🔒 Please edit .env file to configure your AdGuard credentials:"
    echo "   - ADGUARD_URL (default: http://localhost:3000)"
    echo "   - ADGUARD_USERNAME"
    echo "   - ADGUARD_PASSWORD"
    echo "   - ADMIN_PASSWORD (for web interface login)"
fi

# Set permissions
echo "🔐 Setting file permissions..."
sudo chown -R $USER:$USER $APP_DIR
chmod +x $APP_DIR/app.py

# Install systemd service
echo "⚙️ Installing systemd service..."
sudo cp deployment/funtime-scheduler.service $SERVICE_FILE
sudo systemctl daemon-reload

# Enable and start service
echo "🚀 Enabling and starting service..."
sudo systemctl enable $APP_NAME
sudo systemctl start $APP_NAME

# Check service status
echo "📊 Service Status:"
sudo systemctl status $APP_NAME --no-pager

# Setup nginx reverse proxy (optional)
echo "🌐 Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (if any)
    location /static {
        alias /opt/funtime-scheduler/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "✅ Installation Complete!"
echo "========================"
echo ""
echo "🌐 Web Interface: http://192.168.4.50"
echo "📱 Default Login: aswath / agk123"
echo ""
echo "📝 Useful Commands:"
echo "   sudo systemctl status $APP_NAME     # Check service status"
echo "   sudo systemctl restart $APP_NAME    # Restart service"
echo "   sudo journalctl -u $APP_NAME -f     # View logs"
echo "   sudo systemctl stop $APP_NAME       # Stop service"
echo ""
echo "⚙️  Configuration:"
echo "   Edit: $APP_DIR/.env"
echo "   Logs: $APP_DIR/logs/app.log"
echo "   Data: $APP_DIR/data/"
echo ""
echo "🔧 Don't forget to:"
echo "   1. AdGuard credentials are already configured for your setup"
echo "   2. Default admin login: aswath / agk123"
echo "   3. Test the AdGuard connection from the web interface"
echo ""
