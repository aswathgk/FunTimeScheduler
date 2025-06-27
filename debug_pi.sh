#!/bin/bash
# Debug script for FunTime Scheduler - run this on the Pi

echo "=== FunTime Scheduler Debug Script ==="
echo "Date: $(date)"
echo

# Check if the service is running
echo "1. Service Status:"
sudo systemctl status funtime-scheduler --no-pager -l
echo

# Check recent logs
echo "2. Recent Logs:"
sudo journalctl -u funtime-scheduler --since "5 minutes ago" --no-pager
echo

# Check database permissions
echo "3. Database File Permissions:"
ls -la /opt/funtime-scheduler/data/
echo

# Check Python environment
echo "4. Python Environment Test:"
cd /opt/funtime-scheduler
source venv/bin/activate
python3 -c "
import sys
print(f'Python: {sys.version}')
try:
    from services.database import DatabaseManager
    print('✓ DatabaseManager import successful')
    
    db = DatabaseManager()
    print('✓ DatabaseManager initialization successful')
    
    # Test database connection
    schedules = db.get_schedules()
    print(f'✓ Database connection successful, {len(schedules)} schedules found')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
"
echo

# Check app logs if they exist
echo "5. Application Logs (if any):"
if [ -f /opt/funtime-scheduler/logs/app.log ]; then
    tail -20 /opt/funtime-scheduler/logs/app.log
else
    echo "No app.log file found"
fi
echo

echo "=== Debug Complete ==="
