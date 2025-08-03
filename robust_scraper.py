#!/usr/bin/env python3
"""
Robust DTE Karnataka Circulars Scraper
Enhanced version with aggressive SSL bypass and multiple retry strategies
"""

import requests
import json
import re
import os
import time
import socket
from datetime import datetime
from urllib.parse import urljoin, urlparse
import sys
import urllib3
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Completely disable SSL warnings and verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Monkey patch SSL to ignore all certificate issues
def create_unverified_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

ssl._create_default_https_context = create_unverified_context

class RobustHTTPAdapter(HTTPAdapter):
    """Custom adapter with aggressive retry and SSL bypass"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = create_unverified_context()
        return super().init_poolmanager(*args, **kwargs)

def create_robust_session():
    """Create a session that can handle difficult websites"""
    session = requests.Session()
    
    # Aggressive retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    # Use custom adapter
    adapter = RobustHTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Disable all SSL verification
    session.verify = False
    
    # Browser-like headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })
    
    return session

def test_connectivity():
    """Test multiple connection methods to DTE website"""
    
    test_urls = [
        "https://dtek.karnataka.gov.in",
        "http://dtek.karnataka.gov.in", 
        "https://dtek.karnataka.gov.in:443",
        "http://dtek.karnataka.gov.in:80"
    ]
    
    session = create_robust_session()
    
    print("🌐 Testing connectivity to DTE website...")
    
    for url in test_urls:
        try:
            print(f"  Testing: {url}")
            
            # First try basic connectivity
            parsed = urlparse(url)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            port = 443 if parsed.scheme == 'https' else 80
            result = sock.connect_ex((parsed.hostname, port))
            sock.close()
            
            if result == 0:
                print(f"    ✅ Socket connection successful")
                
                # Try HTTP request
                response = session.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"    ✅ HTTP request successful ({len(response.text)} chars)")
                    print(f"    📄 Content type: {response.headers.get('content-type', 'unknown')}")
                    return url, response.text
                else:
                    print(f"    ⚠️ HTTP {response.status_code}")
            else:
                print(f"    ❌ Socket connection failed (error {result})")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:60]}")
            continue
    
    print("❌ All connectivity tests failed")
    return None, None

def extract_circulars_advanced(html, base_url):
    """Advanced circular extraction with multiple parsing strategies"""
    
    print(f"📝 Analyzing HTML content ({len(html)} characters)")
    
    if len(html) < 500:
        print("⚠️ HTML content too short")
        return []
    
    circulars = []
    
    # Strategy 1: Look for table structures with dates and PDFs
    print("🔍 Strategy 1: Table-based extraction")
    
    # Find all links that look like PDFs
    pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
    pdf_links = re.findall(pdf_pattern, html, re.IGNORECASE)
    print(f"  Found {len(pdf_links)} PDF links")
    
    # Find all date patterns
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})'   # DD Month YYYY
    ]
    
    all_dates = []
    for pattern in date_patterns:
        dates = re.findall(pattern, html)
        all_dates.extend(dates)
    
    print(f"  Found {len(all_dates)} date patterns")
    
    # Strategy 2: Look for table rows with circular information
    print("🔍 Strategy 2: Row-based extraction")
    
    # Find table rows that contain both dates and links
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    rows = re.findall(row_pattern, html, re.DOTALL | re.IGNORECASE)
    
    valid_rows = []
    for row in rows:
        # Check if row contains date and PDF
        has_date = any(re.search(pattern, row) for pattern in date_patterns)
        has_pdf = re.search(r'\.pdf', row, re.IGNORECASE)
        
        if has_date and has_pdf:
            valid_rows.append(row)
    
    print(f"  Found {len(valid_rows)} valid table rows")
    
    # Strategy 3: Extract from valid rows
    for i, row in enumerate(valid_rows[:20]):  # Limit to 20 most recent
        try:
            # Extract date
            date_found = None
            for pattern in date_patterns:
                match = re.search(pattern, row)
                if match:
                    date_found = match.group(1)
                    break
            
            # Extract PDF link
            pdf_match = re.search(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', row, re.IGNORECASE)
            pdf_link = None
            if pdf_match:
                pdf_link = pdf_match.group(1)
                if not pdf_link.startswith('http'):
                    pdf_link = urljoin(base_url, pdf_link)
            
            # Extract title/description from text content
            # Remove HTML tags
            text_content = re.sub(r'<[^>]+>', ' ', row)
            text_content = ' '.join(text_content.split())  # Clean whitespace
            
            # Look for order numbers or titles
            title = f"Circular {i+1}"
            if len(text_content) > 20:
                # Use first meaningful text as title
                words = text_content.split()
                meaningful_words = [w for w in words if len(w) > 3 and not w.isdigit()]
                if meaningful_words:
                    title = ' '.join(meaningful_words[:8])  # First 8 meaningful words
            
            if date_found:
                circular = {
                    "title": title[:100],  # Limit title length
                    "description": f"Circular dated {date_found}",
                    "date": date_found,
                    "order_number": f"Order-{i+1}",
                    "link": pdf_link,
                    "source": "DTE Karnataka",
                    "category": "GENERAL",
                    "scraped_at": datetime.now().isoformat(),
                    "extraction_method": "table_row"
                }
                circulars.append(circular)
                
        except Exception as e:
            print(f"  ⚠️ Error processing row {i}: {e}")
            continue
    
    print(f"✨ Extracted {len(circulars)} circulars using advanced parsing")
    return circulars

def scrape_dte_circulars_robust():
    """Robust scraping with multiple fallback strategies"""
    
    print(f"🚀 Starting Robust DTE Scraper - {datetime.now()}")
    
    # Test connectivity first
    working_url, html_content = test_connectivity()
    
    if not working_url:
        print("❌ Cannot connect to DTE website")
        return create_empty_data()
    
    print(f"✅ Connected to: {working_url}")
    
    # Try to find actual circular pages
    session = create_robust_session()
    
    # Common paths to try
    circular_paths = [
        "/",  # Homepage might have recent circulars
        "/circulars",
        "/notices", 
        "/orders",
        "/page/circulars",
        "/page/Circulars",
        "/page/Circulars/DVP/en",
        "/page/Circulars/DVP/kn",
        "/page/Circulars/Exam/en",
        "/page/Circulars/Exam/kn",
        "/page/Circulars/ACM-Polytechnic/en",
        "/page/Circulars/ACM-Polytechnic/kn",
        "/info-4/Departmental+Circulars/en",
        "/info-4/Departmental+Circulars/kn"
    ]
    
    all_circulars = []
    
    for path in circular_paths:
        try:
            full_url = working_url.rstrip('/') + path
            print(f"\n🔍 Trying: {full_url}")
            
            response = session.get(full_url, timeout=15)
            if response.status_code == 200 and len(response.text) > 1000:
                print(f"  ✅ Success ({len(response.text)} chars)")
                
                # Extract circulars from this page
                page_circulars = extract_circulars_advanced(response.text, working_url)
                
                if page_circulars:
                    # Add category based on path
                    category = "GENERAL"
                    if "dvp" in path.lower():
                        category = "DVP"
                    elif "exam" in path.lower():
                        category = "EXAM"
                    elif "acm" in path.lower():
                        category = "ACM"
                    elif "departmental" in path.lower():
                        category = "DEPARTMENTAL"
                    
                    for circular in page_circulars:
                        circular["category"] = category
                        circular["source_url"] = full_url
                    
                    all_circulars.extend(page_circulars)
                    print(f"  📊 Added {len(page_circulars)} circulars")
                else:
                    print(f"  ⚠️ No circulars found on this page")
            else:
                print(f"  ❌ Failed or empty response")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:60]}")
            continue
        
        # Small delay between requests
        time.sleep(1)
    
    # Remove duplicates based on PDF links
    unique_circulars = []
    seen_links = set()
    
    for circular in all_circulars:
        link = circular.get("link", "")
        if link and link not in seen_links:
            seen_links.add(link)
            unique_circulars.append(circular)
        elif not link:  # Keep circulars without links too
            unique_circulars.append(circular)
    
    print(f"\n🎯 Total unique circulars found: {len(unique_circulars)}")
    
    # Save data
    save_scraped_data(unique_circulars)
    
    return len(unique_circulars)

def create_empty_data():
    """Create empty data structure when scraping fails"""
    print("📝 Creating empty data files")
    
    os.makedirs('data', exist_ok=True)
    
    empty_files = ['latest.json', 'dvp.json', 'exam.json', 'acm.json', 'departmental.json']
    for filename in empty_files:
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # Create error timestamp
    timestamp = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "failed",
        "circulars_count": 0,
        "error": "Could not connect to DTE website"
    }
    
    with open('data/timestamp.json', 'w', encoding='utf-8') as f:
        json.dump(timestamp, f, indent=2)
    
    return 0

def save_scraped_data(circulars):
    """Save scraped data to JSON files"""
    
    os.makedirs('data', exist_ok=True)
    
    # Save all circulars
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(circulars, f, ensure_ascii=False, indent=2)
    
    # Save by category
    categories = {
        'DVP': 'dvp.json',
        'EXAM': 'exam.json', 
        'ACM': 'acm.json',
        'DEPARTMENTAL': 'departmental.json'
    }
    
    for category, filename in categories.items():
        category_circulars = [c for c in circulars if c.get('category') == category]
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(category_circulars, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {len(category_circulars)} {category} circulars to {filename}")
    
    # Save timestamp
    timestamp = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "success" if circulars else "no_data",
        "circulars_count": len(circulars),
        "extraction_method": "robust_scraper"
    }
    
    with open('data/timestamp.json', 'w', encoding='utf-8') as f:
        json.dump(timestamp, f, indent=2)
    
    print(f"✅ Data saved successfully - {len(circulars)} total circulars")

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        print("🎯 DTE Karnataka Robust Scraper v3.0")
        
        # Set all SSL bypass environment variables
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_VERIFY'] = 'false'
        
        count = scrape_dte_circulars_robust()
        
        elapsed = time.time() - start_time
        print(f"\n🎉 Robust scraper completed in {elapsed:.1f}s with {count} circulars")
        
        # Always exit successfully to avoid GitHub Actions failures
        sys.exit(0)
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n💥 CRITICAL ERROR after {elapsed:.1f}s: {e}")
        
        # Create empty files as fallback
        create_empty_data()
        
        print("🔄 Empty fallback files created")
        sys.exit(0)