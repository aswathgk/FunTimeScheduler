#!/usr/bin/env python3
"""
FunTime Scheduler - A Raspberry Pi web-based website scheduler
that integrates with AdGuard Home to block websites on schedule.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import signal
import sys

from services.database import DatabaseManager
from services.adguard_api import AdGuardAPI
from services.scheduler_service import SchedulerService

# Load environment variables
load_dotenv()

# Configure logging
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
log_file = os.getenv('LOG_FILE', 'logs/app.log')

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Simple User class for authentication
    class User(UserMixin):
        def __init__(self, id):
            self.id = id
    
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)
    
    # Initialize services
    db_manager = DatabaseManager()
    adguard_api = AdGuardAPI()
    scheduler_service = SchedulerService(db_manager, adguard_api)
    
    # Routes
    @app.route('/')
    @login_required
    def dashboard():
        """Main dashboard showing all scheduled website groups."""
        try:
            schedules = db_manager.get_all_schedules()
            return render_template('dashboard.html', schedules=schedules)
        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            flash('Error loading dashboard', 'error')
            return render_template('dashboard.html', websites=[])
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page and authentication."""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Simple authentication (in production, use proper password hashing)
            if (username == os.getenv('ADMIN_USERNAME', 'admin') and 
                password == os.getenv('ADMIN_PASSWORD', 'admin')):
                user = User('admin')
                login_user(user, remember=True)
                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user."""
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
    
    @app.route('/add_website', methods=['GET', 'POST'])
    @login_required
    def add_website():
        """Add a new schedule with multiple websites."""
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                websites_text = request.form.get('websites', '').strip()
                start_time = request.form.get('start_time')
                end_time = request.form.get('end_time')
                enabled = request.form.get('enabled') == 'on'
                
                if not name or not websites_text or not start_time or not end_time:
                    flash('All fields are required', 'error')
                    return render_template('add_website.html', 
                                         name=name, websites=websites_text, 
                                         start_time=start_time, end_time=end_time)
                
                # Parse websites from textarea
                websites = []
                for line in websites_text.split('\n'):
                    url = line.strip()
                    if url:
                        # Clean URL (remove protocol if present)
                        if url.startswith(('http://', 'https://')):
                            url = url.split('://', 1)[1]
                        websites.append(url)
                
                if not websites:
                    flash('At least one website is required', 'error')
                    return render_template('add_website.html', 
                                         name=name, websites=websites_text, 
                                         start_time=start_time, end_time=end_time)
                
                schedule_id = db_manager.add_schedule(name, start_time, end_time, websites, enabled)
                logger.info(f"Successfully added schedule '{name}' with ID: {schedule_id}")
                
                if enabled:
                    # Schedule all websites in this schedule
                    try:
                        schedule_data = db_manager.get_schedule(schedule_id)
                        if schedule_data and 'websites' in schedule_data:
                            for website in schedule_data['websites']:
                                try:
                                    scheduler_service.schedule_website(website['id'], website['url'], start_time, end_time)
                                    logger.info(f"Scheduled website: {website['url']}")
                                except Exception as scheduler_error:
                                    logger.error(f"Error scheduling website {website['url']}: {scheduler_error}")
                                    # Continue with other websites even if one fails
                        else:
                            logger.warning(f"Could not retrieve schedule data for ID: {schedule_id}")
                    except Exception as schedule_error:
                        logger.error(f"Error in scheduling process: {schedule_error}")
                        # Don't fail the entire operation if scheduling fails
                
                flash(f'Schedule "{name}" added successfully with {len(websites)} websites', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                logger.error(f"Error adding schedule: {e}")
                logger.error(f"Form data - name: '{name}', websites: '{websites_text}', start: '{start_time}', end: '{end_time}', enabled: {enabled}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                flash('Error adding schedule. Please check the logs for details.', 'error')
                return render_template('add_website.html', 
                                     name=name, websites=websites_text, 
                                     start_time=start_time, end_time=end_time)
        
        return render_template('add_website.html')
    
    @app.route('/edit_website/<int:website_id>', methods=['GET', 'POST'])
    @login_required
    def edit_website(website_id):
        """Edit an existing website schedule."""
        website = db_manager.get_website(website_id)
        if not website:
            flash('Website not found', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                url = request.form.get('url', '').strip()
                start_time = request.form.get('start_time')
                end_time = request.form.get('end_time')
                enabled = request.form.get('enabled') == 'on'
                
                if not url or not start_time or not end_time:
                    flash('All fields are required', 'error')
                    return render_template('edit_website.html', website=website)
                
                # Clean URL
                if url.startswith(('http://', 'https://')):
                    url = url.split('://', 1)[1]
                
                # Remove old schedule
                scheduler_service.remove_website_schedule(website_id)
                
                # Update database
                db_manager.update_website(website_id, url, start_time, end_time, enabled)
                
                # Add new schedule if enabled
                if enabled:
                    scheduler_service.schedule_website(website_id, url, start_time, end_time)
                
                flash(f'Website {url} updated successfully', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                logger.error(f"Error updating website: {e}")
                flash('Error updating website', 'error')
        
        return render_template('edit_website.html', website=website)
    
    @app.route('/delete_website/<int:website_id>', methods=['POST'])
    @login_required
    def delete_website(website_id):
        """Delete a website and its schedule."""
        try:
            website = db_manager.get_website(website_id)
            if website:
                scheduler_service.remove_website_schedule(website_id)
                db_manager.delete_website(website_id)
                flash(f'Website {website["url"]} deleted successfully', 'success')
            else:
                flash('Website not found', 'error')
        except Exception as e:
            logger.error(f"Error deleting website: {e}")
            flash('Error deleting website', 'error')
        
        return redirect(url_for('dashboard'))
    
    @app.route('/toggle_website/<int:website_id>', methods=['POST'])
    @login_required
    def toggle_website(website_id):
        """Toggle website schedule on/off."""
        try:
            website = db_manager.get_website(website_id)
            if website:
                new_enabled = not website['enabled']
                db_manager.update_website_enabled(website_id, new_enabled)
                
                if new_enabled:
                    scheduler_service.schedule_website(
                        website_id, website['url'], 
                        website['start_time'], website['end_time']
                    )
                else:
                    scheduler_service.remove_website_schedule(website_id)
                
                status = 'enabled' if new_enabled else 'disabled'
                flash(f'Website {website["url"]} {status}', 'success')
            else:
                flash('Website not found', 'error')
        except Exception as e:
            logger.error(f"Error toggling website: {e}")
            flash('Error updating website status', 'error')
        
        return redirect(url_for('dashboard'))
    
    @app.route('/history')
    @login_required
    def history():
        """Show blocking/unblocking history."""
        try:
            logs = db_manager.get_recent_logs(limit=100)
            return render_template('history.html', logs=logs)
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            flash('Error loading history', 'error')
            return render_template('history.html', logs=[])
    
    @app.route('/api/status')
    @login_required
    def api_status():
        """API endpoint for system status."""
        try:
            return jsonify({
                'status': 'running',
                'scheduler_running': scheduler_service.is_running(),
                'active_websites': len(db_manager.get_enabled_websites()),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Initialize scheduler
    scheduler_service.start()
    
    # Cleanup function
    def cleanup():
        logger.info("Shutting down scheduler...")
        scheduler_service.stop()
    
    # Register cleanup functions
    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, lambda sig, frame: cleanup())
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())
    
    return app

def main():
    """Main application entry point."""
    app = create_app()
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting FunTime Scheduler on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
