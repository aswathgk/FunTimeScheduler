#!/usr/bin/env python3
"""
Quick test to reproduce the add_website error locally.
Run this from the project directory.
"""

import os
import sys
import tempfile
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_database():
    """Create a temporary test database with the correct schema."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_websites.db')
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create websites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                url TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE
            )
        ''')
        
        # Create legacy websites table for backward compatibility
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legacy_websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    return db_path

def test_database_operations():
    """Test the database operations with sample data."""
    print("Creating test database...")
    db_path = create_test_database()
    print(f"Test database created at: {db_path}")
    
    # Temporarily set the database path
    original_path = os.environ.get('DATABASE_PATH')
    os.environ['DATABASE_PATH'] = db_path
    
    try:
        from services.database import DatabaseManager
        
        print("Initializing DatabaseManager...")
        db_manager = DatabaseManager(db_path)
        
        # Test adding a schedule
        test_name = "Test Social Media Block"
        test_websites = ["facebook.com", "instagram.com", "twitter.com"]
        test_start = "09:00"
        test_end = "17:00"
        test_enabled = True
        
        print(f"Adding schedule: {test_name}")
        print(f"Websites: {test_websites}")
        print(f"Time: {test_start} - {test_end}")
        
        schedule_id = db_manager.add_schedule(
            test_name, test_start, test_end, test_websites, test_enabled
        )
        
        print(f"✓ Schedule added successfully with ID: {schedule_id}")
        
        # Retrieve the schedule
        schedule = db_manager.get_schedule(schedule_id)
        print(f"✓ Schedule retrieved: {schedule}")
        
        # Test getting all schedules
        all_schedules = db_manager.get_all_schedules()
        print(f"✓ Total schedules: {len(all_schedules)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Restore original path
        if original_path:
            os.environ['DATABASE_PATH'] = original_path
        elif 'DATABASE_PATH' in os.environ:
            del os.environ['DATABASE_PATH']

def simulate_form_submission():
    """Simulate the exact form submission that's failing."""
    print("\nSimulating form submission...")
    
    # Mock form data
    form_data = {
        'name': 'Kid TV Block',
        'websites': 'youtube.com\ntiktok.com\nnetflix.com',
        'start_time': '08:00',
        'end_time': '18:00',
        'enabled': 'on'
    }
    
    print(f"Form data: {form_data}")
    
    try:
        # Process the form data like the Flask app does
        name = form_data.get('name', '').strip()
        websites_text = form_data.get('websites', '').strip()
        start_time = form_data.get('start_time')
        end_time = form_data.get('end_time')
        enabled = form_data.get('enabled') == 'on'
        
        print(f"Processed name: '{name}'")
        print(f"Processed websites_text: '{websites_text}'")
        print(f"Processed start_time: '{start_time}'")
        print(f"Processed end_time: '{end_time}'")
        print(f"Processed enabled: {enabled}")
        
        # Parse websites
        websites = []
        for line in websites_text.split('\n'):
            url = line.strip()
            if url:
                if url.startswith(('http://', 'https://')):
                    url = url.split('://', 1)[1]
                websites.append(url)
        
        print(f"Parsed websites: {websites}")
        
        # Validation
        if not name or not websites_text or not start_time or not end_time:
            print("✗ Validation failed: Missing required fields")
            return False
        
        if not websites:
            print("✗ Validation failed: No websites parsed")
            return False
        
        print("✓ Form data validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Error in form processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== FunTime Scheduler Local Debug Test ===")
    print(f"Current time: {datetime.now()}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Test 1: Form data processing
    form_ok = simulate_form_submission()
    print()
    
    # Test 2: Database operations
    db_ok = test_database_operations()
    print()
    
    print("=== Test Summary ===")
    print(f"Form processing: {'✓ PASS' if form_ok else '✗ FAIL'}")
    print(f"Database operations: {'✓ PASS' if db_ok else '✗ FAIL'}")
    
    if form_ok and db_ok:
        print("\n✓ Local tests passed. The issue might be on the Pi.")
        print("Please run the debug script on the Pi to check the actual environment.")
    else:
        print("\n✗ Local tests failed. Check the error messages above.")
