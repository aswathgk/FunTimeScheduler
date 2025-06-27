@echo off
echo 🍓 FunTime Scheduler - Windows Deployment Helper
echo ================================================

echo.
echo Step 1: Creating directory on Raspberry Pi...
ssh aswath@192.168.4.50 "mkdir -p /home/aswath/funtime-scheduler"

echo.
echo Step 2: Copying application files...
scp -r app.py requirements.txt .env services templates deployment aswath@192.168.4.50:/home/aswath/funtime-scheduler/

echo.
echo Step 3: Running installation on Pi...
ssh aswath@192.168.4.50 "cd /home/aswath/funtime-scheduler && chmod +x deployment/install.sh && ./deployment/install.sh"

echo.
echo ✅ Deployment completed!
echo 🌐 Access your scheduler at: http://192.168.4.50
echo 🔐 Login: aswath / agk123

pause
