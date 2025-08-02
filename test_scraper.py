#!/usr/bin/env python3
"""
Test script for DTE Karnataka Circulars Scraper
Run this locally to test the scraper functionality
"""

import requests
import urllib3
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_connectivity():
    """Test basic connectivity to DTE website"""
    print("🔗 Testing connectivity to DTE website...")
    
    base_url = "https://dtek.karnataka.gov.in"
    
    try:
        session = requests.Session()
        session.verify = False
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(base_url, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Successfully connected to {base_url}")
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.text)} characters")
        
        # Test one circular page
        test_url = f"{base_url}/page/Circulars/DVP/kn"
        print(f"\n🔗 Testing circular page: {test_url}")
        
        response = session.get(test_url, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Successfully connected to circular page")
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.text)} characters")
        
        # Check for expected content
        if "ಸಿಟಿಇ" in response.text or "CTE" in response.text:
            print("✅ Found expected Kannada/English content")
        else:
            print("⚠️ No expected content patterns found")
            
        return True
        
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def test_scraper():
    """Test the actual scraper functionality"""
    print("\n🐍 Testing scraper functionality...")
    
    try:
        # Import and run the scraper
        from simple_scraper import scrape_dte_circulars
        
        print("✅ Scraper module imported successfully")
        
        # Run the scraper
        count = scrape_dte_circulars()
        
        print(f"✅ Scraper completed successfully with {count} circulars")
        
        # Check if data files were created
        data_files = ['latest.json', 'dvp.json', 'exam.json', 'acm.json', 'departmental.json', 'timestamp.json']
        
        print("\n📁 Checking generated data files:")
        for file in data_files:
            file_path = f"data/{file}"
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file}: {size} bytes")
            else:
                print(f"   ❌ {file}: Missing")
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 DTE Karnataka Circulars Scraper Test Suite")
    print("=" * 50)
    
    # Test connectivity first
    connectivity_ok = test_connectivity()
    
    if not connectivity_ok:
        print("\n❌ Connectivity test failed. Check your internet connection and try again.")
        sys.exit(1)
    
    # Test scraper functionality
    scraper_ok = test_scraper()
    
    print("\n" + "=" * 50)
    if scraper_ok:
        print("✅ All tests passed! Scraper is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()