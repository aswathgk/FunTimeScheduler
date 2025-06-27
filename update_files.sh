#!/bin/bash
# Copy updated files and restart service

echo "Copying updated files..."
sudo cp /tmp/database.py /opt/funtime-scheduler/services/
sudo cp /tmp/add_website.html /opt/funtime-scheduler/templates/
sudo cp /tmp/dashboard.html /opt/funtime-scheduler/templates/
sudo cp /tmp/app.py /opt/funtime-scheduler/

echo "Setting permissions..."
sudo chown -R www-data:www-data /opt/funtime-scheduler/

echo "Restarting service..."
sudo systemctl restart funtime-scheduler

echo "Checking service status..."
sudo systemctl status funtime-scheduler --no-pager -l

echo "Done!"
