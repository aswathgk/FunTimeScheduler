"""
Database manager for FunTime Scheduler.
Handles SQLite database operations for websites, schedules, and logs.
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager."""
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'data/scheduler.db')
        
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create schedules table for grouping websites
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create websites table linked to schedules
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS websites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        schedule_id INTEGER,
                        url TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE
                    )
                ''')
                
                # Migrate existing data if old structure exists
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='websites'")
                    if cursor.fetchone():
                        # Check if old structure exists (url as unique constraint)
                        cursor.execute("PRAGMA table_info(websites)")
                        columns = [column[1] for column in cursor.fetchall()]
                        if 'schedule_id' not in columns:
                            # Old structure exists, migrate data
                            logger.info("Migrating old database structure...")
                            
                            # Get old websites
                            cursor.execute("SELECT * FROM websites")
                            old_websites = cursor.fetchall()
                            
                            # Drop old table
                            conn.execute("DROP TABLE websites")
                            
                            # Recreate with new structure
                            conn.execute('''
                                CREATE TABLE websites (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    schedule_id INTEGER,
                                    url TEXT NOT NULL,
                                    enabled BOOLEAN DEFAULT 1,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE
                                )
                            ''')
                            
                            # Migrate old data
                            for old_site in old_websites:
                                # Create a schedule for each old website
                                conn.execute('''
                                    INSERT INTO schedules (name, start_time, end_time, enabled, created_at)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (f"Schedule for {old_site[1]}", old_site[2], old_site[3], old_site[4], old_site[5]))
                                
                                schedule_id = cursor.lastrowid
                                
                                # Add website to the new structure
                                conn.execute('''
                                    INSERT INTO websites (schedule_id, url, enabled, created_at)
                                    VALUES (?, ?, ?, ?)
                                ''', (schedule_id, old_site[1], old_site[4], old_site[5]))
                                
                            logger.info(f"Migrated {len(old_websites)} websites to new structure")
                except sqlite3.Error as e:
                    logger.info("No migration needed or migration failed: " + str(e))
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        website_id INTEGER,
                        website_url TEXT NOT NULL,
                        action TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT 1,
                        error_message TEXT,
                        FOREIGN KEY (website_id) REFERENCES websites (id)
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_websites_schedule ON websites(schedule_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_schedules_enabled ON schedules(enabled)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _dict_factory(self, cursor, row):
        """Convert sqlite3.Row to dictionary."""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    
    def add_schedule(self, name: str, start_time: str, end_time: str, websites: List[str], enabled: bool = True) -> int:
        """Add a new schedule with multiple websites."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add schedule
                cursor.execute('''
                    INSERT INTO schedules (name, start_time, end_time, enabled)
                    VALUES (?, ?, ?, ?)
                ''', (name, start_time, end_time, enabled))
                
                schedule_id = cursor.lastrowid
                
                # Add websites to the schedule
                for url in websites:
                    url = url.strip()
                    if url:  # Skip empty URLs
                        cursor.execute('''
                            INSERT INTO websites (schedule_id, url, enabled)
                            VALUES (?, ?, ?)
                        ''', (schedule_id, url, enabled))
                
                conn.commit()
                
                logger.info(f"Added schedule: {name} with {len(websites)} websites (ID: {schedule_id})")
                return schedule_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding schedule {name}: {e}")
            raise

    def add_website(self, url: str, start_time: str, end_time: str, enabled: bool = True) -> int:
        """Add a single website (creates a schedule with one website for backward compatibility)."""
        schedule_name = f"Schedule for {url}"
        return self.add_schedule(schedule_name, start_time, end_time, [url], enabled)
    
    def get_schedule(self, schedule_id: int) -> Optional[Dict[str, Any]]:
        """Get a schedule by ID with its websites."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                
                # Get schedule
                cursor.execute('SELECT * FROM schedules WHERE id = ?', (schedule_id,))
                schedule = cursor.fetchone()
                
                if schedule:
                    # Get associated websites
                    cursor.execute('SELECT * FROM websites WHERE schedule_id = ? ORDER BY url', (schedule_id,))
                    websites = cursor.fetchall()
                    schedule['websites'] = websites
                
                return schedule
                
        except sqlite3.Error as e:
            logger.error(f"Error getting schedule {schedule_id}: {e}")
            return None

    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Get all schedules with their websites."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                
                # Get all schedules
                cursor.execute('SELECT * FROM schedules ORDER BY created_at DESC')
                schedules = cursor.fetchall()
                
                # Get websites for each schedule
                for schedule in schedules:
                    cursor.execute('SELECT * FROM websites WHERE schedule_id = ? ORDER BY url', (schedule['id'],))
                    schedule['websites'] = cursor.fetchall()
                
                return schedules
                
        except sqlite3.Error as e:
            logger.error(f"Error getting all schedules: {e}")
            return []

    def get_enabled_schedules(self) -> List[Dict[str, Any]]:
        """Get all enabled schedules with their websites."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                
                # Get enabled schedules
                cursor.execute('SELECT * FROM schedules WHERE enabled = 1 ORDER BY created_at DESC')
                schedules = cursor.fetchall()
                
                # Get websites for each schedule
                for schedule in schedules:
                    cursor.execute('SELECT * FROM websites WHERE schedule_id = ? AND enabled = 1 ORDER BY url', (schedule['id'],))
                    schedule['websites'] = cursor.fetchall()
                
                return schedules
                
        except sqlite3.Error as e:
            logger.error(f"Error getting enabled schedules: {e}")
            return []

    def get_website(self, website_id: int) -> Optional[Dict[str, Any]]:
        """Get a website by ID (legacy method for backward compatibility)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                
                # Get website with schedule info
                cursor.execute('''
                    SELECT w.*, s.name as schedule_name, s.start_time, s.end_time, s.enabled as schedule_enabled
                    FROM websites w
                    JOIN schedules s ON w.schedule_id = s.id
                    WHERE w.id = ?
                ''', (website_id,))
                
                website = cursor.fetchone()
                if website:
                    # Add backward compatibility fields
                    website['url'] = website['url']
                    website['enabled'] = website['schedule_enabled']
                
                return website
                
        except sqlite3.Error as e:
            logger.error(f"Error getting website {website_id}: {e}")
            return None
    
    def get_all_websites(self) -> List[Dict[str, Any]]:
        """Get all websites (legacy method - now returns websites with schedule info)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT w.*, s.name as schedule_name, s.start_time, s.end_time, s.enabled as schedule_enabled
                    FROM websites w
                    JOIN schedules s ON w.schedule_id = s.id
                    ORDER BY s.created_at DESC
                ''')
                
                websites = cursor.fetchall()
                # Add backward compatibility fields
                for website in websites:
                    website['enabled'] = website['schedule_enabled']
                
                return websites
                
        except sqlite3.Error as e:
            logger.error(f"Error getting all websites: {e}")
            return []

    def get_enabled_websites(self) -> List[Dict[str, Any]]:
        """Get all enabled websites (legacy method)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT w.*, s.name as schedule_name, s.start_time, s.end_time, s.enabled as schedule_enabled
                    FROM websites w
                    JOIN schedules s ON w.schedule_id = s.id
                    WHERE s.enabled = 1 AND w.enabled = 1
                    ORDER BY s.created_at DESC
                ''')
                
                websites = cursor.fetchall()
                # Add backward compatibility fields
                for website in websites:
                    website['enabled'] = website['schedule_enabled']
                
                return websites
                
        except sqlite3.Error as e:
            logger.error(f"Error getting enabled websites: {e}")
            return []
    
    def update_website(self, website_id: int, url: str, start_time: str, end_time: str, enabled: bool):
        """Update a website."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE websites 
                    SET url = ?, start_time = ?, end_time = ?, enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (url, start_time, end_time, enabled, website_id))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Website with ID {website_id} not found")
                
                conn.commit()
                logger.info(f"Updated website ID {website_id}: {url}")
                
        except sqlite3.Error as e:
            logger.error(f"Error updating website {website_id}: {e}")
            raise
    
    def update_website_enabled(self, website_id: int, enabled: bool):
        """Update website enabled status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE websites 
                    SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (enabled, website_id))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Website with ID {website_id} not found")
                
                conn.commit()
                logger.info(f"Updated website ID {website_id} enabled status: {enabled}")
                
        except sqlite3.Error as e:
            logger.error(f"Error updating website enabled status {website_id}: {e}")
            raise
    
    def delete_website(self, website_id: int):
        """Delete a website."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM websites WHERE id = ?', (website_id,))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Website with ID {website_id} not found")
                
                conn.commit()
                logger.info(f"Deleted website ID {website_id}")
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting website {website_id}: {e}")
            raise
    
    def log_action(self, website_id: int, website_url: str, action: str, 
                   success: bool = True, error_message: str = None):
        """Log a blocking/unblocking action."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs (website_id, website_url, action, success, error_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (website_id, website_url, action, success, error_message))
                
                conn.commit()
                logger.info(f"Logged action: {action} for {website_url} (success: {success})")
                
        except sqlite3.Error as e:
            logger.error(f"Error logging action: {e}")
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent logs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = self._dict_factory
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up logs older than specified days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM logs 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old log entries")
                
        except sqlite3.Error as e:
            logger.error(f"Error cleaning up old logs: {e}")
