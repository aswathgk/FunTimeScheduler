@echo off
REM Update files on the Pi from Windows

echo Updating FunTime Scheduler files on Pi...

echo Copying app.py...
scp app.py pi@192.168.4.50:/opt/funtime-scheduler/

echo Copying add_website.html...
scp templates/add_website.html pi@192.168.4.50:/opt/funtime-scheduler/templates/

echo Fixing permissions...
ssh pi@192.168.4.50 "sudo chown -R pi:pi /opt/funtime-scheduler/app.py /opt/funtime-scheduler/templates/add_website.html"

echo Restarting service...
ssh pi@192.168.4.50 "sudo systemctl restart funtime-scheduler"

echo Checking service status...
ssh pi@192.168.4.50 "sudo systemctl status funtime-scheduler --no-pager -l"

echo Update complete!
pause
