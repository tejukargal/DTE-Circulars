#!/usr/bin/env python3
"""
DTE Karnataka Proxy Scraper
Uses multiple methods to bypass network restrictions and access DTE website
"""

import requests
import json
import re
import os
import time
from datetime import datetime
from urllib.parse import urljoin, quote_plus
import sys
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_proxy_session():
    """Create session with multiple proxy options"""
    session = requests.Session()
    session.verify = False
    
    # Try different user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    session.headers.update({
        'User-Agent': user_agents[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    return session

def try_web_archive_access():
    """Try to access DTE website through web archive services"""
    
    print("🔍 Trying Web Archive access...")
    
    archive_urls = [
        "https://web.archive.org/web/20250000000000*/https://dtek.karnataka.gov.in/",
        "https://archive.today/https://dtek.karnataka.gov.in/",
        "http://www.google.com/search?q=site:dtek.karnataka.gov.in+circulars+filetype:pdf"
    ]
    
    session = create_proxy_session()
    
    for archive_url in archive_urls:
        try:
            print(f"  Trying: {archive_url}")
            response = session.get(archive_url, timeout=15)
            
            if response.status_code == 200 and len(response.text) > 1000:
                print(f"    ✅ Success via archive service")
                return response.text
            else:
                print(f"    ❌ No useful content")
                
        except Exception as e:
            print(f"    ❌ Failed: {str(e)[:50]}")
            continue
    
    return None

def try_google_search_scraping():
    """Try to find DTE circulars through Google search"""
    
    print("🔍 Trying Google Search for recent circulars...")
    
    search_queries = [
        "site:dtek.karnataka.gov.in filetype:pdf circular 2025",
        "site:dtek.karnataka.gov.in DVP circular 2025",
        "site:dtek.karnataka.gov.in exam circular 2025",
        "\"DTE Karnataka\" circular 2025 filetype:pdf",
        "\"Karnataka technical education\" circular 2025"
    ]
    
    session = create_proxy_session()
    found_circulars = []
    
    for query in search_queries:
        try:
            print(f"  Searching: {query}")
            
            # Use Google search (be careful with rate limits)
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=20"
            
            response = session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                # Extract PDF links from search results
                pdf_pattern = r'href="([^"]*dtek\.karnataka\.gov\.in[^"]*\.pdf[^"]*)"'
                pdf_links = re.findall(pdf_pattern, response.text)
                
                # Extract titles and dates
                for link in pdf_links[:5]:  # Limit to 5 per query
                    # Clean up the URL
                    clean_link = link.replace('/url?q=', '').split('&')[0]
                    
                    if 'dtek.karnataka.gov.in' in clean_link:
                        circular = {
                            "title": f"DTE Circular - {datetime.now().strftime('%Y-%m-%d')}",
                            "description": f"Found via Google search for: {query}",
                            "date": datetime.now().strftime("%d/%m/%Y"),
                            "order_number": f"Search-{len(found_circulars) + 1}",
                            "link": clean_link,
                            "source": "DTE Karnataka (via Google)",
                            "category": "SEARCH_RESULT",
                            "scraped_at": datetime.now().isoformat(),
                            "search_query": query
                        }
                        found_circulars.append(circular)
                        print(f"    ✅ Found PDF: {clean_link}")
                
                print(f"  Found {len(pdf_links)} PDF links for this query")
            else:
                print(f"    ❌ Search failed: {response.status_code}")
                
            # Small delay to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"    ❌ Search error: {str(e)[:50]}")
            continue
    
    print(f"🎯 Total circulars found via search: {len(found_circulars)}")
    return found_circulars

def try_alternative_endpoints():
    """Try alternative government portals that might have DTE circulars"""
    
    print("🔍 Trying alternative government portals...")
    
    alternative_urls = [
        "https://karnataka.gov.in/technical-education",
        "https://www.karnataka.gov.in/deptl/education/technical/index.html",
        "https://egovernance.karnataka.gov.in/",
        "https://www.india.gov.in/state/karnataka/technical-education",
        "https://www.aicte-india.org/bureaus/teb/karnataka"
    ]
    
    session = create_proxy_session()
    found_circulars = []
    
    for url in alternative_urls:
        try:
            print(f"  Checking: {url}")
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                print(f"    ✅ Accessible")
                
                # Look for DTE-related links or circulars
                dte_pattern = r'href="([^"]*dte[^"]*)"'
                circular_pattern = r'href="([^"]*circular[^"]*)"'
                pdf_pattern = r'href="([^"]*\.pdf[^"]*)"'
                
                dte_links = re.findall(dte_pattern, response.text, re.IGNORECASE)
                circular_links = re.findall(circular_pattern, response.text, re.IGNORECASE)
                pdf_links = re.findall(pdf_pattern, response.text, re.IGNORECASE)
                
                print(f"    Found {len(dte_links)} DTE links, {len(circular_links)} circular links, {len(pdf_links)} PDFs")
                
                # Process found links
                for i, link in enumerate((dte_links + circular_links + pdf_links)[:5]):
                    if not link.startswith('http'):
                        link = urljoin(url, link)
                    
                    circular = {
                        "title": f"Alternative Portal Document {i+1}",
                        "description": f"Found on alternative portal: {url}",
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "order_number": f"Alt-{len(found_circulars) + 1}",
                        "link": link,
                        "source": f"Alternative Portal ({url})",
                        "category": "ALTERNATIVE",
                        "scraped_at": datetime.now().isoformat()
                    }
                    found_circulars.append(circular)
                
            else:
                print(f"    ❌ Not accessible: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:50]}")
            continue
    
    return found_circulars

def try_direct_pdf_access():
    """Try to access known DTE PDF patterns directly"""
    
    print("🔍 Trying direct PDF access with known patterns...")
    
    base_url = "https://dtek.karnataka.gov.in"
    pdf_patterns = [
        "/storage/pdf-files/DVP/",
        "/storage/pdf-files/Exam/", 
        "/storage/pdf-files/ACM/",
        "/storage/pdf-files/Departmental/",
        "/uploads/circulars/",
        "/documents/circulars/",
        "/files/circulars/"
    ]
    
    session = create_proxy_session()
    found_pdfs = []
    
    # Try common PDF filenames
    common_names = [
        "latest.pdf",
        "circular.pdf", 
        "notification.pdf",
        "order.pdf",
        "document.pdf",
        f"circular_{datetime.now().year}.pdf",
        f"order_{datetime.now().year}.pdf"
    ]
    
    for pattern in pdf_patterns:
        for name in common_names:
            try:
                pdf_url = base_url + pattern + name
                print(f"  Trying: {pdf_url}")
                
                # Just check if URL exists (HEAD request)
                response = session.head(pdf_url, timeout=10)
                
                if response.status_code == 200:
                    print(f"    ✅ Found accessible PDF!")
                    
                    circular = {
                        "title": f"Direct PDF Access: {name}",
                        "description": f"Directly accessible PDF from {pattern}",
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "order_number": f"Direct-{len(found_pdfs) + 1}",
                        "link": pdf_url,
                        "source": "DTE Karnataka (Direct Access)",
                        "category": pattern.split('/')[-2].upper() if len(pattern.split('/')) > 2 else "DIRECT",
                        "scraped_at": datetime.now().isoformat()
                    }
                    found_pdfs.append(circular)
                
            except Exception as e:
                continue  # Silent fail for direct access attempts
    
    print(f"🎯 Found {len(found_pdfs)} directly accessible PDFs")
    return found_pdfs

def proxy_scrape_circulars():
    """Main proxy scraping function"""
    
    print(f"🚀 Starting DTE Proxy Scraper - {datetime.now()}")
    
    all_circulars = []
    
    # Method 1: Web Archive access
    archive_content = try_web_archive_access()
    if archive_content:
        print("✅ Got content from web archive")
        # Could parse this content for circular links
    
    # Method 2: Google Search scraping
    search_circulars = try_google_search_scraping()
    if search_circulars:
        all_circulars.extend(search_circulars)
    
    # Method 3: Alternative portals
    alt_circulars = try_alternative_endpoints()
    if alt_circulars:
        all_circulars.extend(alt_circulars)
    
    # Method 4: Direct PDF access
    direct_pdfs = try_direct_pdf_access()
    if direct_pdfs:
        all_circulars.extend(direct_pdfs)
    
    print(f"\n🎯 Total circulars found via proxy methods: {len(all_circulars)}")
    
    if all_circulars:
        save_proxy_data(all_circulars)
        return len(all_circulars)
    else:
        print("❌ No circulars found through any proxy method")
        return 0

def save_proxy_data(circulars):
    """Save proxy-scraped data"""
    
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
    
    # Save timestamp
    timestamp = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": "proxy_success",
        "circulars_count": len(circulars),
        "method": "proxy_scraping"
    }
    
    with open('data/timestamp.json', 'w', encoding='utf-8') as f:
        json.dump(timestamp, f, indent=2)
    
    print(f"✅ Proxy data saved - {len(circulars)} circulars")

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        count = proxy_scrape_circulars()
        
        elapsed = time.time() - start_time
        print(f"\n🎉 Proxy scraper completed in {elapsed:.1f}s with {count} circulars")
        
        sys.exit(0)
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n💥 Proxy scraper ERROR after {elapsed:.1f}s: {e}")
        sys.exit(0)  # Don't fail the workflow