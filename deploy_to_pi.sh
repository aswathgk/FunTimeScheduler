#!/bin/bash

# FunTime Scheduler - Quick Deploy Script for Aswath's Raspberry Pi
# IP: 192.168.4.50, User: aswath, Password: agk123

echo "🍓 FunTime Scheduler - Quick Deploy to Raspberry Pi"
echo "=================================================="
echo "Target: aswath@192.168.4.50"
echo ""

# Check if we have sshpass for automated deployment
if ! command -v sshpass &> /dev/null; then
    echo "📦 Installing sshpass for automated deployment..."
    sudo apt update && sudo apt install -y sshpass
fi

# Deployment settings
PI_USER="aswath"
PI_HOST="192.168.4.50"
PI_PASS="agk123"
REMOTE_DIR="/home/aswath/funtime-scheduler"

echo "📋 Copying files to Raspberry Pi..."

# Create remote directory and copy files
sshpass -p "$PI_PASS" ssh -o StrictHostKeyChecking=no "$PI_USER@$PI_HOST" "mkdir -p $REMOTE_DIR"

# Copy all files except .git and __pycache__
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='data/' \
    --exclude='logs/' \
    --exclude='venv/' \
    -e "sshpass -p $PI_PASS ssh -o StrictHostKeyChecking=no" \
    ./ "$PI_USER@$PI_HOST:$REMOTE_DIR/"

echo "⚙️ Running installation on Raspberry Pi..."

# Run installation script on remote Pi
sshpass -p "$PI_PASS" ssh -o StrictHostKeyChecking=no "$PI_USER@$PI_HOST" << 'EOF'
cd /home/aswath/funtime-scheduler

# Make install script executable
chmod +x deployment/install.sh

# Run installation
./deployment/install.sh

echo ""
echo "✅ Installation completed on Raspberry Pi!"
echo "🌐 Access the web interface at: http://192.168.4.50"
echo "🔐 Login: aswath / agk123"
EOF

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Open http://192.168.4.50 in your browser"
echo "2. Login with: aswath / agk123"
echo "3. Start adding websites to schedule"
echo ""
echo "Useful commands to run on the Pi:"
echo "  ssh aswath@192.168.4.50"
echo "  sudo systemctl status funtime-scheduler"
echo "  sudo journalctl -u funtime-scheduler -f"
