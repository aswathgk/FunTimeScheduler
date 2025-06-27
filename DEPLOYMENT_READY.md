# 🍓 FunTime Scheduler - Ready for Deployment!

## Your Configuration

**Raspberry Pi Details:**
- IP Address: `192.168.4.50`
- Username: `aswath`
- Password: `agk123`

**AdGuard Home Settings:**
- URL: `http://192.168.4.50:3000`
- Username: `aswathg`
- Password: `agk12345`

**Web Interface Login:**
- URL: `http://192.168.4.50`
- Username: `aswath`
- Password: `agk123`

## Quick Start 🚀

### Step 1: Test Connectivity
```bash
python test_connectivity.py
```

### Step 2: Deploy to Raspberry Pi

**Windows (PowerShell):**
```powershell
.\deploy_to_pi.ps1
```

**Linux/Mac/WSL:**
```bash
chmod +x deploy_to_pi.sh
./deploy_to_pi.sh
```

### Step 3: Access Your Scheduler
Open browser: http://192.168.4.50
Login: `aswath` / `agk123`

## What You Get 📋

✅ **Automatic AdGuard Home installation** (if not present)
✅ **Flask web application** with responsive UI
✅ **Daily scheduling** for website blocking
✅ **Systemd service** for auto-start on boot
✅ **Activity logging** with history view
✅ **Nginx reverse proxy** for better performance
✅ **Production-ready** Gunicorn WSGI server

## File Structure 📁

```
FunTimeScheduler/
├── app.py                    # Main Flask application
├── .env                      # Your custom configuration
├── requirements.txt          # Python dependencies
├── services/                 # Core services
│   ├── database.py          # SQLite database manager
│   ├── adguard_api.py       # AdGuard Home API client
│   └── scheduler_service.py # APScheduler integration
├── templates/               # HTML templates
├── deployment/              # Production deployment files
├── test_connectivity.py     # Connection testing
├── deploy_to_pi.ps1        # Windows deployment script
├── deploy_to_pi.sh         # Linux/Mac deployment script
└── SETUP_GUIDE.md          # Detailed setup instructions
```

## Usage Examples 📝

### Block YouTube during work hours:
- Website: `youtube.com`
- Start: `09:00` (9 AM)
- End: `17:00` (5 PM)

### Block social media at night:
- Website: `facebook.com`
- Start: `22:00` (10 PM)  
- End: `07:00` (7 AM)

### Block gaming sites for kids:
- Website: `roblox.com`
- Start: `08:00` (8 AM)
- End: `15:00` (3 PM)

## Monitoring 📊

**Service Status:**
```bash
ssh aswath@192.168.4.50
sudo systemctl status funtime-scheduler
```

**View Logs:**
```bash
sudo journalctl -u funtime-scheduler -f
tail -f /opt/funtime-scheduler/logs/app.log
```

**Restart Service:**
```bash
sudo systemctl restart funtime-scheduler
```

## Features 🌟

- **Web Dashboard**: Add, edit, delete website schedules
- **Time Picker**: Visual interface for setting block times
- **Enable/Disable**: Toggle schedules without deleting
- **Activity History**: View all blocking/unblocking events
- **Mobile Friendly**: Works on phones and tablets
- **Secure Login**: Password-protected interface
- **Auto-Start**: Runs automatically on Pi boot
- **Lightweight**: Optimized for Raspberry Pi performance

## Troubleshooting 🔧

**If AdGuard Home isn't working:**
1. Check if it's running: `sudo systemctl status AdguardHome`
2. Restart it: `sudo systemctl restart AdguardHome`
3. Access web interface: http://192.168.4.50:3000

**If websites aren't blocking:**
1. Check AdGuard user rules in web interface
2. Verify DNS settings point to your Pi
3. Check application logs for errors

**If web interface won't load:**
1. Check service status: `sudo systemctl status funtime-scheduler`
2. Check logs: `sudo journalctl -u funtime-scheduler -f`
3. Restart service: `sudo systemctl restart funtime-scheduler`

## Support 💬

Your FunTime Scheduler is fully configured and ready to deploy! The installation script will automatically set up everything needed on your Raspberry Pi.

Happy scheduling! 🎉
