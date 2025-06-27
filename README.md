# FunTime Scheduler 🍓

A lightweight Flask web application for Raspberry Pi that schedules website blocking through AdGuard Home integration. Perfect for managing family screen time or productivity periods.

## Features

- 🌐 **Web-based Interface**: Clean, responsive UI for managing website schedules
- ⏰ **Daily Scheduling**: Set daily recurring block/unblock times for websites
- � **Multi-Website Schedules**: Create schedules that block multiple websites at once
- �🛡️ **AdGuard Integration**: Seamlessly integrates with AdGuard Home DNS filtering
- 📊 **Activity Logging**: Track all blocking/unblocking actions with timestamps
- 🔐 **Secure Authentication**: Login protection for the web interface
- 🚀 **Auto-start**: Runs automatically on Raspberry Pi boot via systemd
- 📱 **Mobile Friendly**: Responsive design works on all devices
- 🔄 **Database Migration**: Automatic schema updates for new features

## Requirements

### Hardware
- Raspberry Pi (3B+ or newer recommended)
- MicroSD card (16GB+ recommended)
- Network connection

### Software
- Raspberry Pi OS (Bullseye or newer)
- Python 3.9+
- AdGuard Home (running on the same Pi or network)

## Quick Installation

### 1. Prerequisites

Make sure your Raspberry Pi has AdGuard Home installed and running:
```bash
# If AdGuard Home is not installed, install it first:
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
```

### 2. Download and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/funtime-scheduler.git
cd funtime-scheduler

# Run the installation script
chmod +x deployment/install.sh
./deployment/install.sh
```

### 3. Configuration

Edit the configuration file:
```bash
sudo nano /opt/funtime-scheduler/.env
```

Update these important settings:
```env
# AdGuard Configuration
ADGUARD_URL=http://192.168.4.50:3000    # Your AdGuard Home URL
ADGUARD_USERNAME=aswathg                 # Your AdGuard admin username
ADGUARD_PASSWORD=agk12345                # Your AdGuard admin password

# Web Interface Authentication
ADMIN_USERNAME=aswath                    # Web interface username
ADMIN_PASSWORD=agk123                    # Web interface password
```

### 4. Start the Service

```bash
sudo systemctl restart funtime-scheduler
sudo systemctl status funtime-scheduler
```

## Manual Installation

If you prefer to install manually:

### 1. System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx
```

### 2. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/funtime-scheduler
sudo chown aswath:aswath /opt/funtime-scheduler

# Clone and setup
git clone https://github.com/yourusername/funtime-scheduler.git /opt/funtime-scheduler
cd /opt/funtime-scheduler

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data logs
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit configuration
```

### 4. Install Systemd Service

```bash
sudo cp deployment/funtime-scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable funtime-scheduler
sudo systemctl start funtime-scheduler
```

## Usage

### Web Interface

1. Open your browser and navigate to `http://192.168.4.50`
2. Login with credentials: **aswath** / **agk123**
3. Add websites to schedule
4. Set blocking times for each website
5. Monitor activity in the History page

### Managing Websites

- **Add Website**: Click "Add Website" and enter one or more domains (one per line)
- **Multi-Website Schedules**: Create schedules that block multiple websites simultaneously
- **Set Schedule**: Choose start and end times for blocking (24-hour format)
- **Enable/Disable**: Toggle schedules on/off without deleting them
- **Edit/Delete**: Update existing schedules or remove them entirely

### Example Schedules

**Single Website:**
- **Website**: `youtube.com`
- **Block Time**: `09:00` (9:00 AM)
- **Unblock Time**: `17:00` (5:00 PM)
- **Result**: YouTube will be blocked every day from 9 AM to 5 PM

**Multiple Websites:**
- **Schedule Name**: "Social Media Block"
- **Websites**: 
  ```
  facebook.com
  instagram.com
  twitter.com
  tiktok.com
  ```
- **Block Time**: `08:00` (8:00 AM)
- **Unblock Time**: `18:00` (6:00 PM)
- **Result**: All social media sites blocked during work hours

## Service Management

### Systemd Commands

```bash
# Check status
sudo systemctl status funtime-scheduler

# Start/Stop/Restart
sudo systemctl start funtime-scheduler
sudo systemctl stop funtime-scheduler
sudo systemctl restart funtime-scheduler

# Enable/Disable auto-start
sudo systemctl enable funtime-scheduler
sudo systemctl disable funtime-scheduler

# View logs
sudo journalctl -u funtime-scheduler -f
```

### Log Files

- **Application Logs**: `/opt/funtime-scheduler/logs/app.log`
- **Access Logs**: `/opt/funtime-scheduler/logs/access.log`
- **Error Logs**: `/opt/funtime-scheduler/logs/error.log`
- **System Logs**: `sudo journalctl -u funtime-scheduler`

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Generated | Flask secret key for sessions |
| `DEBUG` | `False` | Enable debug mode (development only) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5000` | Server port |
| `ADMIN_USERNAME` | `aswath` | Web interface username |
| `ADMIN_PASSWORD` | `agk123` | Web interface password |
| `ADGUARD_URL` | `http://192.168.4.50:3000` | AdGuard Home URL |
| `ADGUARD_USERNAME` | `aswathg` | AdGuard admin username |
| `ADGUARD_PASSWORD` | `agk12345` | AdGuard admin password |
| `DATABASE_PATH` | `data/scheduler.db` | SQLite database location |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `logs/app.log` | Application log file |

### AdGuard Home Integration

The application integrates with AdGuard Home using its REST API:

- **Blocking**: Adds domains to AdGuard's user rules as `||domain.com^`
- **Unblocking**: Removes domains from user rules
- **Authentication**: Uses HTTP Basic Authentication
- **Connection**: Configurable URL (local or remote AdGuard instance)

## Development

### Running in Development

```bash
# Clone repository
git clone https://github.com/yourusername/funtime-scheduler.git
cd funtime-scheduler

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Run development server
python app.py
```

### Project Structure

```
funtime-scheduler/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment configuration
├── services/             # Service modules
│   ├── database.py       # Database operations
│   ├── adguard_api.py    # AdGuard Home API client
│   └── scheduler_service.py # Scheduling logic
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── add_website.html  # Add website form
│   ├── edit_website.html # Edit website form
│   └── history.html      # Activity history
├── deployment/           # Production deployment files
│   ├── install.sh        # Installation script
│   ├── funtime-scheduler.service # Systemd service
│   ├── gunicorn.conf.py  # Gunicorn configuration
│   └── start_production.sh # Production startup script
├── data/                 # Database files (created at runtime)
├── logs/                 # Log files (created at runtime)
└── README.md            # This file
```

## Troubleshooting

### Common Issues

**1. Service won't start**
```bash
# Check service status
sudo systemctl status funtime-scheduler

# Check logs
sudo journalctl -u funtime-scheduler -n 50
```

**2. AdGuard connection failed**
- Verify AdGuard Home is running: `http://your-pi-ip:3000`
- Check AdGuard credentials in `.env` file
- Ensure network connectivity between services

**3. Website not blocking**
- Check AdGuard Home user rules in the web interface
- Verify DNS settings on client devices point to the Pi
- Check application logs for API errors

**4. Permission errors**
```bash
# Fix file permissions
sudo chown -R aswath:aswath /opt/funtime-scheduler
sudo chmod +x /opt/funtime-scheduler/app.py
```

### Debug Mode

Enable debug mode for development:
```bash
# Edit .env file
DEBUG=True

# Restart service
sudo systemctl restart funtime-scheduler
```

## Security Notes

- Change default passwords before production use
- Use HTTPS in production (consider setting up Let's Encrypt)
- Regularly update the system and application dependencies
- Monitor logs for suspicious activity
- Backup your database and configuration files

## Performance

### Raspberry Pi Optimization

The application is optimized for Raspberry Pi:
- **Lightweight**: Minimal memory footprint (< 50MB)
- **Efficient**: Uses SQLite for fast local database operations
- **Low CPU**: Background scheduler uses minimal resources
- **Network**: Optimized HTTP requests to AdGuard API

### Scaling

For larger deployments:
- Increase Gunicorn workers in the systemd service
- Use external database (PostgreSQL) instead of SQLite
- Deploy behind a proper reverse proxy (nginx is included)
- Consider using Redis for session storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the wiki for additional guides

## Changelog

### v2.0.0 (June 2025)
- ✨ **New Feature**: Multi-website scheduling support
- 🗄️ **Database Migration**: Added schedules table for better organization
- 🎨 **UI Enhancement**: Improved interface for adding multiple websites
- 📊 **Dashboard Update**: Grouped display of schedules with multiple websites
- 🔧 **Backend Improvements**: Enhanced database methods and API endpoints
- 🐛 **Bug Fixes**: Fixed AdGuard Home API integration issues
- 📚 **Documentation**: Updated setup guides and deployment instructions

### v1.0.0 (June 2025)
- 🎉 **Initial Release**: Basic website scheduling functionality
- 🛡️ **AdGuard Integration**: DNS-based website blocking
- 🌐 **Web Interface**: User-friendly dashboard
- ⏰ **Daily Schedules**: Recurring block/unblock times
- 🔐 **Authentication**: Secure login system
- 🚀 **Auto-deployment**: Systemd service integration
