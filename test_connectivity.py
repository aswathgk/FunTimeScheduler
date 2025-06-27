#!/usr/bin/env python3
"""
Connection test script for FunTime Scheduler
Tests connectivity to Raspberry Pi and AdGuard Home
"""

import requests
import socket
import sys
import os
from datetime import datetime

def test_pi_connection():
    """Test SSH connection to Raspberry Pi."""
    print("🍓 Testing Raspberry Pi Connection...")
    
    try:
        # Test if Pi is reachable
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('192.168.4.50', 22))
        sock.close()
        
        if result == 0:
            print("   ✅ Raspberry Pi is reachable on SSH (port 22)")
            return True
        else:
            print("   ❌ Raspberry Pi is not reachable on SSH")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing Pi connection: {e}")
        return False

def test_adguard_connection():
    """Test connection to AdGuard Home."""
    print("🛡️  Testing AdGuard Home Connection...")
    
    adguard_url = "http://192.168.4.50:3000"
    
    try:
        # Test if AdGuard web interface is accessible
        response = requests.get(f"{adguard_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ AdGuard Home web interface is accessible")
            
            # Test API endpoint
            api_response = requests.get(
                f"{adguard_url}/control/status",
                auth=('aswathg', 'agk12345'),
                timeout=10
            )
            
            if api_response.status_code == 200:
                print("   ✅ AdGuard Home API is accessible with credentials")
                status = api_response.json()
                print(f"   ℹ️  AdGuard Version: {status.get('version', 'Unknown')}")
                print(f"   ℹ️  DNS Protection: {status.get('protection_enabled', 'Unknown')}")
                return True
            else:
                print(f"   ⚠️  AdGuard API returned status: {api_response.status_code}")
                print("   🔐 Check username/password: aswathg/agk12345")
                return False
                
        else:
            print(f"   ❌ AdGuard web interface returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("   ❌ Connection timeout to AdGuard Home")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to AdGuard Home")
        return False
    except Exception as e:
        print(f"   ❌ Error testing AdGuard connection: {e}")
        return False

def test_webapp_connection():
    """Test connection to the Flask web app (if running)."""
    print("🌐 Testing FunTime Scheduler Web App...")
    
    try:
        response = requests.get("http://192.168.4.50:5000", timeout=10)
        if response.status_code == 200:
            print("   ✅ FunTime Scheduler web app is running")
            return True
        else:
            print(f"   ⚠️  Web app returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("   ❌ Connection timeout to web app")
        return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Web app is not running (this is OK if not deployed yet)")
        return False
    except Exception as e:
        print(f"   ❌ Error testing web app: {e}")
        return False

def main():
    """Run all connectivity tests."""
    print("🧪 FunTime Scheduler - Connectivity Tests")
    print("=" * 45)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Run tests
    pi_ok = test_pi_connection()
    print()
    adguard_ok = test_adguard_connection()
    print()
    webapp_ok = test_webapp_connection()
    print()
    
    # Summary
    print("📋 Test Summary:")
    print(f"   Raspberry Pi: {'✅ OK' if pi_ok else '❌ FAIL'}")
    print(f"   AdGuard Home: {'✅ OK' if adguard_ok else '❌ FAIL'}")
    print(f"   Web App: {'✅ OK' if webapp_ok else '⚠️  Not Running'}")
    print()
    
    if pi_ok and adguard_ok:
        print("🎉 Ready for deployment!")
        print("   Run deploy_to_pi.sh (Linux/Mac) or deploy_to_pi.ps1 (Windows)")
    else:
        print("❌ Fix connectivity issues before deployment")
        if not pi_ok:
            print("   - Check if Raspberry Pi is powered on and connected")
        if not adguard_ok:
            print("   - Check if AdGuard Home is installed and running")
            print("   - Verify AdGuard credentials: aswathg/agk12345")
    
    return 0 if (pi_ok and adguard_ok) else 1

if __name__ == '__main__':
    sys.exit(main())
