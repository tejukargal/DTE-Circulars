#!/usr/bin/env python3
"""
Demo script to test DTE Circulars scraper functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import DTECircularScraper

def demo_scraper():
    print("=" * 60)
    print("DTE CIRCULARS SCRAPER DEMO")
    print("=" * 60)
    
    scraper = DTECircularScraper()
    
    try:
        print("Fetching latest 5 circulars from DTE Karnataka...")
        print(f"Source URL: {scraper.circulars_url}")
        print("-" * 60)
        
        circulars = scraper.scrape_circulars(limit=5)
        
        if circulars:
            print(f"✅ Successfully fetched {len(circulars)} circulars:\n")
            
            for i, circular in enumerate(circulars, 1):
                print(f"{i}. Date: {circular['date']}")
                print(f"   Order No: {circular['order_no']}")
                print(f"   Subject: {circular['subject'][:80]}{'...' if len(circular['subject']) > 80 else ''}")
                print(f"   PDF Link: {'✅ Available' if circular['pdf_link'] else '❌ Not available'}")
                print()
        else:
            print("❌ No circulars found")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("\nThis might be due to:")
        print("- SSL certificate issues (handled by the app)")
        print("- Network connectivity problems")
        print("- Website structure changes")
    
    print("=" * 60)
    print("Demo completed. Run 'python app.py' to start the web application.")
    print("=" * 60)

if __name__ == "__main__":
    demo_scraper()