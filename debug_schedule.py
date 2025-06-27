#!/usr/bin/env python3
"""
Debug script for FunTime Scheduler add_website functionality.
This script helps debug the "Error adding schedule" issue.
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_schema():
    """Check if the database has the correct schema."""
    db_path = "/opt/funtime-scheduler/data/websites.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if schedules table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schedules'")
            schedules_table = cursor.fetchone()
            
            # Check if websites table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='websites'")
            websites_table = cursor.fetchone()
            
            print(f"Schedules table exists: {schedules_table is not None}")
            print(f"Websites table exists: {websites_table is not None}")
            
            if schedules_table:
                cursor.execute("PRAGMA table_info(schedules)")
                schedules_info = cursor.fetchall()
                print("\nSchedules table schema:")
                for col in schedules_info:
                    print(f"  {col[1]} ({col[2]})")
            
            if websites_table:
                cursor.execute("PRAGMA table_info(websites)")
                websites_info = cursor.fetchall()
                print("\nWebsites table schema:")
                for col in websites_info:
                    print(f"  {col[1]} ({col[2]})")
                    
            # Check if old websites table has any data
            if websites_table:
                cursor.execute("SELECT COUNT(*) FROM websites")
                count = cursor.fetchone()[0]
                print(f"\nWebsites table has {count} records")
                
                if count > 0:
                    cursor.execute("SELECT * FROM websites LIMIT 5")
                    websites = cursor.fetchall()
                    print("Sample records:")
                    for website in websites:
                        print(f"  {website}")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def test_add_schedule():
    """Test adding a schedule with sample data."""
    try:
        from services.database import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Test data
        name = "Test Schedule"
        websites = ["facebook.com", "youtube.com"]
        start_time = "09:00"
        end_time = "17:00"
        enabled = True
        
        print(f"Testing add_schedule with:")
        print(f"  Name: {name}")
        print(f"  Websites: {websites}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        print(f"  Enabled: {enabled}")
        
        schedule_id = db_manager.add_schedule(name, start_time, end_time, websites, enabled)
        print(f"Success! Schedule ID: {schedule_id}")
        
        # Retrieve and display the schedule
        schedule = db_manager.get_schedule(schedule_id)
        print(f"Retrieved schedule: {schedule}")
        
    except Exception as e:
        print(f"Error in test_add_schedule: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== FunTime Scheduler Debug Tool ===")
    print(f"Current time: {datetime.now()}")
    print()
    
    print("1. Checking database schema...")
    check_database_schema()
    print()
    
    print("2. Testing add_schedule function...")
    test_add_schedule()
