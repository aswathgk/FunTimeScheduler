# Manual Deployment Steps for FunTime Scheduler

## Step 1: Connect to your Raspberry Pi

Open a new PowerShell window and connect:
```powershell
ssh aswath@192.168.4.50
# Enter password: agk123
```

## Step 2: Prepare the Pi (run these commands on the Pi)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-venv python3-pip git nginx supervisor curl

# Create application directory
sudo mkdir -p /opt/funtime-scheduler
sudo chown aswath:aswath /opt/funtime-scheduler
```

## Step 3: Install AdGuard Home (if not already installed)

```bash
# Download and install AdGuard Home
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sudo sh -s -- -v

# Enable and start AdGuard Home
sudo systemctl enable AdguardHome
sudo systemctl start AdguardHome

# Check status
sudo systemctl status AdguardHome
```

## Step 4: Configure AdGuard Home

1. Open browser: http://192.168.4.50:3000
2. Complete setup wizard:
   - Admin Interface: Port 3000
   - DNS Server: Port 53
   - Username: `aswathg`
   - Password: `agk12345`

## Step 5: Copy files to Pi

From your Windows machine, open a new PowerShell window and run:

```powershell
# Navigate to project directory
cd "C:\Users\Aswath\Documents\Coding Projects\FunTimeScheduler"

# Copy files using SCP (you'll need to enter password for each file)
scp -r . aswath@192.168.4.50:/opt/funtime-scheduler/

# Or use SFTP if you prefer
```

## Step 6: Install Python application (on the Pi)

```bash
# Go to application directory
cd /opt/funtime-scheduler

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p data logs
chmod 755 data logs

# Set up environment file (already configured)
ls -la .env  # Should show your custom configuration
```

## Step 7: Install systemd service (on the Pi)

```bash
# Copy service file
sudo cp deployment/funtime-scheduler.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable funtime-scheduler
sudo systemctl start funtime-scheduler

# Check status
sudo systemctl status funtime-scheduler
```

## Step 8: Setup Nginx reverse proxy (on the Pi)

```bash
# Create Nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/funtime-scheduler

# Enable site
sudo ln -sf /etc/nginx/sites-available/funtime-scheduler /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Step 9: Test the installation

```bash
# Check all services
sudo systemctl status funtime-scheduler AdguardHome nginx

# Check logs
sudo journalctl -u funtime-scheduler -n 20

# Test web interface
curl -I http://localhost:5000
```

## Step 10: Access the web interface

Open browser: http://192.168.4.50
Login: aswath / agk123

## Troubleshooting Commands

```bash
# View logs
sudo journalctl -u funtime-scheduler -f
tail -f /opt/funtime-scheduler/logs/app.log

# Restart services
sudo systemctl restart funtime-scheduler
sudo systemctl restart AdguardHome

# Check file permissions
ls -la /opt/funtime-scheduler/
sudo chown -R aswath:aswath /opt/funtime-scheduler/
```
