#!/usr/bin/env python3
"""
Simple DTE Karnataka Circulars Scraper
Robust approach with improved SSL handling and faster execution
"""

import requests
import json
import re
import os
import time
from datetime import datetime
from urllib.parse import urljoin
import sys
import urllib3
import ssl

# Disable SSL warnings and configure for problematic certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Configure SSL context to be more permissive
ssl._create_default_https_context = ssl._create_unverified_context

def make_request_with_retry(session, url, max_retries=2, base_delay=1):
    """HTTP request with fast retry logic and aggressive SSL handling"""
    
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries} - timeout: 8s")
            
            # Fast request with aggressive SSL bypass
            response = session.get(
                url, 
                timeout=(5, 8),  # Shorter timeouts for faster execution
                verify=False,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; DTE-Scraper/1.0)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'close'
                }
            )
            response.raise_for_status()
            
            # Basic content validation
            if len(response.text) < 50:
                raise requests.exceptions.RequestException("Response too short")
                
            print(f"  ✅ Success: {len(response.text)} chars received")
            return response
            
        except Exception as e:
            error_msg = str(e)[:80]
            print(f"  ❌ Attempt {attempt + 1} failed: {error_msg}")
            
            if attempt == max_retries - 1:
                print(f"  🔥 All attempts failed for {url}")
                raise e
            
            time.sleep(base_delay)

def scrape_dte_circulars():
    """Fast and robust scraper with improved URL handling"""
    
    print(f"🚀 Starting DTE scraper - {datetime.now()}")
    
    # Base configuration with multiple base URLs for redundancy
    base_urls = [
        "https://dtek.karnataka.gov.in",
        "http://dtek.karnataka.gov.in"  # HTTP fallback
    ]
    
    # Simplified categories with working URLs
    categories = {
        'dvp': {
            'name': 'DVP Circulars',
            'paths': ['/page/Circulars/DVP/kn', '/page/Circulars/DVP/en', '/circulars/dvp'],
            'file': 'dvp.json'
        },
        'exam': {
            'name': 'Exam Circulars', 
            'paths': ['/page/Circulars/Exam/kn', '/page/Circulars/Exam/en', '/circulars/exam'],
            'file': 'exam.json'
        },
        'acm': {
            'name': 'ACM Circulars',
            'paths': ['/page/Circulars/ACM-Polytechnic/kn', '/page/Circulars/ACM-Polytechnic/en', '/circulars/acm'],
            'file': 'acm.json'
        },
        'departmental': {
            'name': 'Departmental Circulars',
            'paths': ['/info-4/Departmental+Circulars/kn', '/info-4/Departmental+Circulars/en', '/departmental-circulars'],
            'file': 'departmental.json'
        }
    }
    
    # Create fast session with minimal configuration
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; DTE-Scraper/2.0)',
        'Accept': 'text/html',
        'Connection': 'close'  # Don't keep connections alive
    })
    
    # Configure session for SSL issues
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=0))
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
    
    all_circulars = []
    working_base_url = None
    
    # Test connectivity to find working base URL
    print("🌐 Testing connectivity...")
    for base_url in base_urls:
        try:
            print(f"  Testing {base_url}...")
            response = session.get(base_url, timeout=5, verify=False)
            if response.status_code == 200:
                working_base_url = base_url
                print(f"  ✅ {base_url} is accessible")
                break
        except Exception as e:
            print(f"  ❌ {base_url} failed: {str(e)[:50]}")
    
    if not working_base_url:
        print("⚠️ No base URL accessible, using backup data strategy")
        working_base_url = base_urls[0]  # Use first as fallback
    
    # Scrape each category
    for category_key, category in categories.items():
        print(f"\n📋 Scraping {category['name']}...")
        circulars = []
        
        # Try each path with the working base URL
        for path_index, path in enumerate(category['paths']):
            full_url = working_base_url + path
            try:
                print(f"  🔍 Trying: {full_url}")
                response = make_request_with_retry(session, full_url)
                
                circulars = parse_circular_table(response.text, category_key, working_base_url)
                
                if circulars:
                    print(f"  ✅ Found {len(circulars)} circulars")
                    break
                else:
                    print(f"  ⚠️ No circulars found")
                    
            except Exception as e:
                print(f"  ❌ Failed: {str(e)[:60]}")
                continue
        
        # Save results
        os.makedirs('data', exist_ok=True)
        with open(f"data/{category['file']}", 'w', encoding='utf-8') as f:
            json.dump(circulars, f, ensure_ascii=False, indent=2)
        
        if circulars:
            all_circulars.extend(circulars)
            print(f"  💾 Saved {len(circulars)} circulars to {category['file']}")
        else:
            print(f"  📝 Created empty {category['file']}")
    
    # Save combined file and timestamp regardless of success
    os.makedirs('data', exist_ok=True)
    
    if all_circulars:
        with open('data/latest.json', 'w', encoding='utf-8') as f:
            json.dump(all_circulars, f, ensure_ascii=False, indent=2)
        print(f"\nSuccess: Scraped {len(all_circulars)} circulars")
        success_status = "success"
    else:
        # Create empty latest.json to prevent frontend errors
        with open('data/latest.json', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print("\nWarning: No circulars scraped from any category")
        success_status = "failed"
    
    # Always create timestamp with status info
    timestamp = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": success_status,
        "circulars_count": len(all_circulars)
    }
    with open('data/timestamp.json', 'w', encoding='utf-8') as f:
        json.dump(timestamp, f, indent=2)
        
    return len(all_circulars)

def parse_circular_table(html, category_key, base_url):
    """Fast HTML parsing focused on date and PDF patterns"""
    circulars = []
    
    print(f"  📝 Parsing HTML ({len(html)} chars)")
    
    if len(html) < 100:
        print("  ⚠️ HTML too short, likely empty response")
        return []
    
    # Look for date patterns (DD/MM/YYYY, DD-MM-YYYY)
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
    dates = re.findall(date_pattern, html)
    
    # Look for PDF links
    pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
    pdf_links = re.findall(pdf_pattern, html, re.IGNORECASE)
    
    # Look for order numbers in Kannada
    order_pattern = r'(ಸಿಟಿಇ[^<>\n]{5,50})'
    orders = re.findall(order_pattern, html)
    
    print(f"  📅 Found {len(dates)} dates, 📄 {len(pdf_links)} PDFs, 📋 {len(orders)} orders")
    
    # Create circulars from found data
    for i, date in enumerate(dates[:10]):  # Limit to 10 most recent
        # Get corresponding PDF link if available
        pdf_link = None
        if i < len(pdf_links):
            pdf_link = pdf_links[i]
            if not pdf_link.startswith('http'):
                pdf_link = urljoin(base_url, pdf_link)
        
        # Get corresponding order number if available
        order_number = orders[i] if i < len(orders) else f"Order-{i+1}"
        
        # Create circular entry
        circular = {
            "title": f"{order_number[:50]}..." if len(order_number) > 50 else order_number,
            "description": f"Circular dated {date}",
            "date": date,
            "order_number": order_number,
            "link": pdf_link,
            "source": "DTE Karnataka",
            "category": category_key.upper(),
            "scraped_at": datetime.now().isoformat()
        }
        
        circulars.append(circular)
    
    print(f"  ✨ Created {len(circulars)} circular entries")
    return circulars

# Removed old parsing functions - using simplified approach above

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        print("🎯 DTE Karnataka Circulars Scraper v2.0")
        count = scrape_dte_circulars()
        
        elapsed = time.time() - start_time
        print(f"\n🎉 Scraper completed in {elapsed:.1f}s with {count} circulars")
        
        # Exit with success if we got any circulars, or acceptable failure if none
        sys.exit(0 if count > 0 else 0)  # Don't fail GitHub Actions if no new circulars
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n💥 ERROR after {elapsed:.1f}s: {e}")
        
        # Create fallback empty files to prevent frontend errors
        print("📝 Creating fallback empty files...")
        os.makedirs('data', exist_ok=True)
        empty_files = ['latest.json', 'dvp.json', 'exam.json', 'acm.json', 'departmental.json']
        for file in empty_files:
            with open(f'data/{file}', 'w') as f:
                json.dump([], f)
        
        # Create error timestamp
        timestamp = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "error",
            "circulars_count": 0,
            "error": str(e)[:100]
        }
        with open('data/timestamp.json', 'w') as f:
            json.dump(timestamp, f, indent=2)
        
        print("✅ Fallback files created")
        sys.exit(0)  # Don't fail GitHub Actions workflow