#!/usr/bin/env python3
"""
Test script for FunTime Scheduler components
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.database import DatabaseManager
from services.adguard_api import AdGuardAPI
from services.scheduler_service import SchedulerService

def test_database():
    """Test database operations."""
    print("🗄️  Testing Database...")
    
    try:
        db = DatabaseManager('test_scheduler.db')
        
        # Test adding a website
        website_id = db.add_website('example.com', '09:00', '17:00', True)
        print(f"   ✅ Added website with ID: {website_id}")
        
        # Test getting website
        website = db.get_website(website_id)
        print(f"   ✅ Retrieved website: {website['url']}")
        
        # Test logging
        db.log_action(website_id, 'example.com', 'block', True)
        print("   ✅ Logged action")
        
        # Clean up
        os.remove('test_scheduler.db')
        print("   ✅ Database test completed")
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")

def test_adguard_api():
    """Test AdGuard API connection."""
    print("🛡️  Testing AdGuard API...")
    
    try:
        api = AdGuardAPI()
        
        # Test connection
        if api.test_connection():
            print("   ✅ AdGuard connection successful")
            
            # Test getting status
            status = api.get_filtering_status()
            if status:
                print(f"   ✅ Got filtering status: {status.get('enabled', 'Unknown')}")
            
        else:
            print("   ⚠️  AdGuard connection failed (configure credentials in .env)")
            
    except Exception as e:
        print(f"   ❌ AdGuard API test failed: {e}")

def test_scheduler():
    """Test scheduler service."""
    print("⏰ Testing Scheduler Service...")
    
    try:
        db = DatabaseManager('test_scheduler.db')
        api = AdGuardAPI()
        scheduler = SchedulerService(db, api)
        
        # Test starting scheduler
        scheduler.start()
        print("   ✅ Scheduler started")
        
        # Test is running
        if scheduler.is_running():
            print("   ✅ Scheduler is running")
        
        # Test stopping scheduler
        scheduler.stop()
        print("   ✅ Scheduler stopped")
        
        # Clean up
        if os.path.exists('test_scheduler.db'):
            os.remove('test_scheduler.db')
        
        print("   ✅ Scheduler test completed")
        
    except Exception as e:
        print(f"   ❌ Scheduler test failed: {e}")

def main():
    """Run all tests."""
    print("🧪 FunTime Scheduler - Component Tests")
    print("=" * 40)
    
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    test_database()
    print()
    test_adguard_api()
    print()
    test_scheduler()
    print()
    print("🎉 All tests completed!")

if __name__ == '__main__':
    main()
