#!/usr/bin/env python3
"""
Manual data update script for DTE Circulars
Run this locally to update the data and push to GitHub for Railway
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from scraper import DTECircularScraper

def update_data():
    """Update circulars data and commit to GitHub"""
    print("Starting manual data update...")
    
    try:
        # Scrape fresh data
        print("Scraping DTE website...")
        scraper = DTECircularScraper()
        circulars = scraper.scrape_circulars(limit=25)
        
        if not circulars:
            print("ERROR: No circulars found during scraping")
            return False
        
        # Add serial numbers
        for i, circular in enumerate(circulars, 1):
            circular['serial_no'] = i
        
        # Create data structure
        data = {
            'circulars': circulars,
            'count': len(circulars),
            'last_updated': datetime.now().isoformat(),
            'source': 'manual_local_update'
        }
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Write to data file
        with open('data/circulars.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"SUCCESS: Scraped {len(circulars)} circulars")
        
        # Show sample of data
        print("\nSample of updated circulars:")
        for i, circular in enumerate(circulars[:3], 1):
            subject = circular.get('subject', 'N/A')[:60]
            print(f"  {i}. {circular.get('date', 'N/A')} - {subject}...")
        
        # Git operations
        print("\nCommitting and pushing to GitHub...")
        
        # Check if there are changes
        result = subprocess.run(['git', 'diff', '--quiet', 'data/circulars.json'], 
                              capture_output=True)
        
        if result.returncode == 0:
            print("INFO: No changes detected in data")
            return True
        
        # Add and commit changes
        subprocess.run(['git', 'add', 'data/circulars.json'], check=True)
        
        commit_message = f"Update DTE circulars data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("SUCCESS: Pushed updates to GitHub")
        print("Railway will automatically deploy the new data")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Update failed: {e}")
        return False

def main():
    print("DTE Circulars Manual Data Updater")
    print("=" * 40)
    
    if update_data():
        print("\nSUCCESS: Data update completed!")
        print("\nNext steps:")
        print("1. Wait 2-3 minutes for Railway to deploy")
        print("2. Check your Railway app URL")
        print("3. You should see fresh DTE circulars!")
    else:
        print("\nERROR: Data update failed!")
        print("Check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()