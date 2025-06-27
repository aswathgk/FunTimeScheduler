# FunTime Scheduler Setup Guide for Aswath's Raspberry Pi

## Current Status ✅

- **Raspberry Pi**: 192.168.4.50 (Reachable ✅)
- **User**: aswath
- **Password**: agk123
- **AdGuard Home**: Not detected (needs setup)

## Prerequisites Setup

### 1. Install AdGuard Home on Raspberry Pi

SSH into your Raspberry Pi and run these commands:

```bash
# SSH into your Pi
ssh aswath@192.168.4.50

# Download and install AdGuard Home
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v

# Start AdGuard Home
sudo systemctl enable AdguardHome
sudo systemctl start AdguardHome
```

### 2. Configure AdGuard Home

1. Open web browser and go to: `http://192.168.4.50:3000`
2. Follow the setup wizard:
   - **Admin Interface**: Keep port 3000
   - **DNS Server**: Keep port 53
   - **Admin Username**: `aswathg`
   - **Admin Password**: `agk12345`
3. Complete the setup

### 3. Test AdGuard Home

```bash
# Check if AdGuard is running
sudo systemctl status AdguardHome

# Test DNS resolution
nslookup google.com 192.168.4.50
```

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Run the connectivity test first:
```bash
python test_connectivity.py
```

If all tests pass, deploy using:
```bash
# For Windows (PowerShell)
.\deploy_to_pi.ps1

# For Linux/Mac/WSL
./deploy_to_pi.sh
```

### Option 2: Manual Deployment

1. **Copy files to Pi:**
```bash
# Using SCP (replace with your actual path)
scp -r . aswath@192.168.4.50:/home/aswath/funtime-scheduler
```

2. **SSH into Pi and install:**
```bash
ssh aswath@192.168.4.50
cd /home/aswath/funtime-scheduler
chmod +x deployment/install.sh
./deployment/install.sh
```

## Configuration Summary

Your configuration is already set up in the `.env` file:

```env
# Authentication
ADMIN_USERNAME=aswath
ADMIN_PASSWORD=agk123

# AdGuard Configuration  
ADGUARD_URL=http://192.168.4.50:3000
ADGUARD_USERNAME=aswathg
ADGUARD_PASSWORD=agk12345
```

## After Deployment

1. **Access Web Interface**: http://192.168.4.50
2. **Login**: aswath / agk123
3. **Add websites** to schedule blocking
4. **Set times** for blocking/unblocking

## Troubleshooting

### AdGuard Home Issues
```bash
# Check status
sudo systemctl status AdguardHome

# Restart AdGuard
sudo systemctl restart AdguardHome

# Check logs
sudo journalctl -u AdguardHome -f
```

### FunTime Scheduler Issues
```bash
# Check status
sudo systemctl status funtime-scheduler

# Restart service
sudo systemctl restart funtime-scheduler

# Check logs
sudo journalctl -u funtime-scheduler -f
```

## Quick Commands

```bash
# SSH into Pi
ssh aswath@192.168.4.50

# Check all services
sudo systemctl status AdguardHome funtime-scheduler

# View application logs
tail -f /opt/funtime-scheduler/logs/app.log

# Restart everything
sudo systemctl restart AdguardHome funtime-scheduler
```

## Next Steps

1. ✅ Set up AdGuard Home first
2. ✅ Run connectivity test
3. ✅ Deploy FunTime Scheduler
4. ✅ Access web interface
5. ✅ Start scheduling websites!
