# FunTime Scheduler - PowerShell Deploy Script for Aswath's Raspberry Pi
# IP: 192.168.4.50, User: aswath, Password: agk123

Write-Host "🍓 FunTime Scheduler - Deploy to Raspberry Pi" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Target: aswath@192.168.4.50" -ForegroundColor Yellow
Write-Host ""

# Deployment settings
$PI_USER = "aswath"
$PI_HOST = "192.168.4.50"
$PI_PASS = "agk123"
$REMOTE_DIR = "/home/aswath/funtime-scheduler"

# Check if we have WSL or need to use alternative method
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "📋 Using WSL to deploy files..." -ForegroundColor Cyan
    
    # Copy files using WSL and rsync
    wsl bash -c @"
        # Check if sshpass is available
        if ! command -v sshpass &> /dev/null; then
            echo "Installing sshpass..."
            sudo apt update && sudo apt install -y sshpass
        fi
        
        # Create remote directory
        sshpass -p '$PI_PASS' ssh -o StrictHostKeyChecking=no '$PI_USER@$PI_HOST' 'mkdir -p $REMOTE_DIR'
        
        # Copy files
        rsync -avz --progress \
            --exclude='.git' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='.env' \
            --exclude='data/' \
            --exclude='logs/' \
            --exclude='venv/' \
            -e "sshpass -p '$PI_PASS' ssh -o StrictHostKeyChecking=no" \
            . '$PI_USER@$PI_HOST:$REMOTE_DIR/'
"@
    
    Write-Host "⚙️ Running installation on Raspberry Pi..." -ForegroundColor Cyan
    
    # Run installation
    wsl bash -c @"
        sshpass -p '$PI_PASS' ssh -o StrictHostKeyChecking=no '$PI_USER@$PI_HOST' '
            cd $REMOTE_DIR
            chmod +x deployment/install.sh
            ./deployment/install.sh
        '
"@
    
} else {
    Write-Host "❌ WSL not found. Please install WSL or use manual deployment." -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual deployment steps:" -ForegroundColor Yellow
    Write-Host "1. Copy all files to your Raspberry Pi using SCP or WinSCP" -ForegroundColor White
    Write-Host "2. SSH into your Pi: ssh aswath@192.168.4.50" -ForegroundColor White
    Write-Host "3. Navigate to the copied directory" -ForegroundColor White
    Write-Host "4. Run: chmod +x deployment/install.sh && ./deployment/install.sh" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open http://192.168.4.50 in your browser" -ForegroundColor White
Write-Host "2. Login with: aswath / agk123" -ForegroundColor White
Write-Host "3. Start adding websites to schedule" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  ssh aswath@192.168.4.50" -ForegroundColor White
Write-Host "  sudo systemctl status funtime-scheduler" -ForegroundColor White
Write-Host "  sudo journalctl -u funtime-scheduler -f" -ForegroundColor White
