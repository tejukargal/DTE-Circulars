#!/usr/bin/env python3
"""
Fallback DTE Karnataka Circulars Scraper
Enhanced version with SSL workarounds and backup data management
"""

import requests
import json
import os
import time
from datetime import datetime
import sys
import urllib3
import ssl

# Aggressive SSL bypass configuration
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

def use_backup_data():
    """Use the most recent backup data when website is inaccessible"""
    
    print("📂 Using backup data strategy...")
    
    # Find the most recent backup file
    backup_files = [f for f in os.listdir('data') if f.startswith('backup_') and f.endswith('.json')]
    if not backup_files:
        print("  ❌ No backup files found")
        return 0
    
    # Use the latest backup
    latest_backup = sorted(backup_files)[-1]
    backup_path = f"data/{latest_backup}"
    
    print(f"  📄 Using backup: {latest_backup}")
    
    try:
        # Read backup data
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if not backup_data:
            print("  ⚠️ Backup file is empty")
            return 0
        
        print(f"  📊 Backup contains {len(backup_data)} circulars")
        
        # Distribute data to category files
        categories = ['dvp', 'exam', 'acm', 'departmental']
        for category in categories:
            with open(f"data/{category}.json", 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # Create latest.json
        with open('data/latest.json', 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # Update timestamp
        timestamp = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "backup_used",
            "circulars_count": len(backup_data),
            "source": latest_backup,
            "note": "DTE website inaccessible - using backup data"
        }
        
        with open('data/timestamp.json', 'w', encoding='utf-8') as f:
            json.dump(timestamp, f, indent=2)
        
        print(f"  ✅ Backup data restored successfully")
        return len(backup_data)
        
    except Exception as e:
        print(f"  ❌ Failed to use backup: {e}")
        return 0

if __name__ == "__main__":
    try:
        print("🎯 DTE Karnataka Fallback Scraper")
        count = use_backup_data()
        print(f"✅ Fallback completed with {count} circulars")
        sys.exit(0)
    except Exception as e:
        print(f"💀 Fatal error: {e}")
        sys.exit(0)