#!/usr/bin/env python3
"""
Simple DTE Karnataka Circulars Scraper
Direct HTML table parsing approach with robust error handling
"""

import requests
import json
import re
import os
import time
import threading
from datetime import datetime
from urllib.parse import urljoin
import sys
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cross-platform timeout handler
class TimeoutException(Exception):
    pass

def timeout_handler():
    raise TimeoutException("Script execution timed out after 150 seconds")

# Set script-wide timeout of 150 seconds (cross-platform)
timeout_timer = threading.Timer(150.0, timeout_handler)
timeout_timer.start()

def make_request_with_retry(session, url, max_retries=3, base_delay=2):
    """HTTP request with improved retry logic and better error handling"""
    
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries} - timeout: 15s")
            
            # Improved request with better headers and timeout
            response = session.get(
                url, 
                timeout=(10, 15),  # (connect timeout, read timeout)
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check if we got actual content
            if len(response.text) < 100:
                raise requests.exceptions.RequestException("Response too short, might be empty")
                
            return response
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"  Final attempt failed: {str(e)[:100]}")
                raise e
            
            wait_time = base_delay * (attempt + 1)
            print(f"  Request failed, retrying in {wait_time}s... Error: {str(e)[:50]}")
            time.sleep(wait_time)

def scrape_dte_circulars():
    """Simple scraper that works with the actual DTE website structure"""
    
    # Base configuration
    base_url = "https://dtek.karnataka.gov.in"
    
    # Categories with their actual working URLs and fallbacks
    categories = {
        'dvp': {
            'name': 'DVP Circulars',
            'url': f'{base_url}/page/Circulars/DVP/kn',
            'fallback_urls': [
                f'{base_url}/page/Circulars/DVP/en',
                f'{base_url}/circulars/dvp',
                f'{base_url}/page/circulars/dvp/kn'
            ],
            'file': 'dvp.json'
        },
        'exam': {
            'name': 'Exam Circulars', 
            'url': f'{base_url}/page/Circulars/Exam/kn',
            'fallback_urls': [
                f'{base_url}/page/Circulars/Exam/en',
                f'{base_url}/circulars/exam',
                f'{base_url}/page/circulars/exam/kn'
            ],
            'file': 'exam.json'
        },
        'acm': {
            'name': 'ACM Circulars',
            'url': f'{base_url}/page/Circulars/ACM-Polytechnic/kn',
            'fallback_urls': [
                f'{base_url}/page/Circulars/ACM-Polytechnic/en',
                f'{base_url}/circulars/acm',
                f'{base_url}/page/circulars/acm/kn'
            ],
            'file': 'acm.json'
        },
        'departmental': {
            'name': 'Departmental Circulars',
            'url': f'{base_url}/info-4/Departmental+Circulars/kn',
            'fallback_urls': [
                f'{base_url}/info-4/Departmental+Circulars/en',
                f'{base_url}/departmental-circulars',
                f'{base_url}/page/departmental/kn'
            ],
            'file': 'departmental.json'
        }
    }
    
    # Create robust session with better headers
    session = requests.Session()
    session.verify = False  # Skip SSL verification for self-signed certs
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    })
    
    all_circulars = []
    
    print(f"Starting simple DTE scraper - {datetime.now()}")
    
    for category_key, category in categories.items():
        print(f"\nScraping {category['name']}...")
        
        # Try primary URL first, then fallbacks
        urls_to_try = [category['url']] + category.get('fallback_urls', [])
        circulars = []
        
        for url_index, url in enumerate(urls_to_try):
            try:
                if url_index == 0:
                    print(f"  Trying primary URL: {url}")
                else:
                    print(f"  Trying fallback URL {url_index}: {url}")
                
                # Get the page with retry logic
                response = make_request_with_retry(session, url, max_retries=2)
                
                html = response.text
                circulars = parse_circular_table(html, category_key, base_url)
                
                if circulars:
                    print(f"  SUCCESS: Found {len(circulars)} circulars from {'primary' if url_index == 0 else 'fallback'} URL")
                    break
                else:
                    print(f"  WARNING: No circulars found at this URL")
                    
            except Exception as e:
                print(f"  FAILED: {str(e)[:100]}...")
                if url_index == len(urls_to_try) - 1:
                    print(f"  All URLs failed for {category['name']}")
        
        if circulars:
            # Save category file
            os.makedirs('data', exist_ok=True)
            with open(f"data/{category['file']}", 'w', encoding='utf-8') as f:
                json.dump(circulars, f, ensure_ascii=False, indent=2)
            
            all_circulars.extend(circulars)
        else:
            print(f"No circulars found in {category['name']} from any URL")
            
            # Create empty file to prevent frontend errors
            os.makedirs('data', exist_ok=True)
            empty_data = []
            with open(f"data/{category['file']}", 'w', encoding='utf-8') as f:
                json.dump(empty_data, f, ensure_ascii=False, indent=2)
            
            print(f"  Created empty {category['file']} to prevent frontend errors")
    
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
    """Parse the HTML table structure from DTE website with improved logic"""
    circulars = []
    
    print(f"  Parsing HTML content ({len(html)} characters)")
    
    # Multiple parsing strategies for better success rate
    strategies = [
        parse_table_strategy,
        parse_div_strategy, 
        parse_list_strategy
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            print(f"  Trying parsing strategy {i+1}")
            result = strategy(html, category_key, base_url)
            if result:
                print(f"  Strategy {i+1} found {len(result)} circulars")
                return result[:50]  # Limit to 50 most recent
        except Exception as e:
            print(f"  Strategy {i+1} failed: {str(e)[:50]}")
            continue
    
    print(f"  All parsing strategies failed for {category_key}")
    return []

def parse_table_strategy(html, category_key, base_url):
    """Original table parsing strategy"""
    circulars = []
    
    # Extract table rows more aggressively
    table_patterns = [
        r'<table[^>]*>.*?</table>',
        r'<tbody[^>]*>.*?</tbody>',
        r'<tr[^>]*>.*?</tr>'
    ]
    
    table_content = ""
    for pattern in table_patterns:
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        if matches:
            table_content = '\n'.join(matches)
            break
    
    if not table_content:
        table_content = html  # Use full HTML as fallback
    
    # Date format patterns (DD/MM/YYYY, DD-MM-YYYY, etc.)
    date_patterns = [
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}-\d{1,2}-\d{4})',
        r'(\d{1,2}\.\d{1,2}\.\d{4})'
    ]
    
    # Split by table rows
    rows = re.split(r'<tr[^>]*>|<\/tr>', table_content)
    
    for row in rows:
        if not row.strip() or len(row) < 20:
            continue
            
        # Look for date pattern in row
        date = None
        for date_pattern in date_patterns:
            date_match = re.search(date_pattern, row)
            if date_match:
                date = date_match.group(1)
                break
        
        if not date:
            continue
        
        # Extract order number with more patterns
        order_patterns = [
            r'(ಸಿಟಿಇ[^<]+(?:ಡಿವಿಪಿ|ಎಸಿಎಂ|ಪರೀಕ್ಷಾ)[^<]*)',
            r'(CTE[^<]+(?:DVP|ACM|EXAM)[^<]*)',
            r'([A-Za-z0-9/\-\(\)]{10,})',  # Generic order pattern
        ]
        
        order_number = ""
        for pattern in order_patterns:
            order_match = re.search(pattern, row, re.IGNORECASE)
            if order_match:
                order_number = order_match.group(1).strip()
                break
        
        if not order_number:
            order_number = f"Order-{len(circulars)+1}"
        
        # Extract description with multiple strategies
        description = extract_description(row)
        
        # Find PDF link in this row
        pdf_link = extract_pdf_link(row, base_url)
        
        # Only add if we have meaningful data
        if date and (order_number or description):
            circular = {
                "title": f"{order_number}: {description[:100]}..." if description else order_number,
                "description": description or "No description available",
                "date": date,
                "order_number": order_number,
                "link": pdf_link,
                "source": "DTE Karnataka",
                "category": category_key.upper(),
                "scraped_at": datetime.now().isoformat()
            }
            
            circulars.append(circular)
    
    return circulars

def parse_div_strategy(html, category_key, base_url):
    """Alternative parsing strategy using div elements"""
    circulars = []
    
    # Look for div-based content structures
    div_patterns = [
        r'<div[^>]*class[^>]*circular[^>]*>.*?</div>',
        r'<div[^>]*class[^>]*item[^>]*>.*?</div>',
        r'<div[^>]*class[^>]*row[^>]*>.*?</div>'
    ]
    
    for pattern in div_patterns:
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        for match in matches:
            # Extract similar data from div content
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', match)
            if date_match:
                date = date_match.group(1)
                description = extract_description(match)
                pdf_link = extract_pdf_link(match, base_url)
                
                circular = {
                    "title": f"Circular-{len(circulars)+1}: {description[:100]}..." if description else f"Circular-{len(circulars)+1}",
                    "description": description or "No description available",
                    "date": date,
                    "order_number": f"DIV-{len(circulars)+1}",
                    "link": pdf_link,
                    "source": "DTE Karnataka",
                    "category": category_key.upper(),
                    "scraped_at": datetime.now().isoformat()
                }
                
                circulars.append(circular)
    
    return circulars

def parse_list_strategy(html, category_key, base_url):
    """Alternative parsing strategy using list elements"""
    circulars = []
    
    # Look for list-based content
    list_patterns = [
        r'<li[^>]*>.*?</li>',
        r'<ul[^>]*>.*?</ul>',
        r'<ol[^>]*>.*?</ol>'
    ]
    
    for pattern in list_patterns:
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        for match in matches:
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', match)
            if date_match:
                date = date_match.group(1)
                description = extract_description(match)
                pdf_link = extract_pdf_link(match, base_url)
                
                circular = {
                    "title": f"List-{len(circulars)+1}: {description[:100]}..." if description else f"List-{len(circulars)+1}",
                    "description": description or "No description available",
                    "date": date,
                    "order_number": f"LIST-{len(circulars)+1}",
                    "link": pdf_link,
                    "source": "DTE Karnataka",
                    "category": category_key.upper(),
                    "scraped_at": datetime.now().isoformat()
                }
                
                circulars.append(circular)
    
    return circulars

def extract_description(text):
    """Extract description from HTML text using multiple patterns"""
    # Remove HTML tags for cleaner text extraction
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Multiple description patterns
    desc_patterns = [
        r'<p[^>]*>([^<]+)</p>',
        r'<td[^>]*>([^<]{20,})</td>',
        r'<span[^>]*>([^<]{20,})</span>',
        r'<div[^>]*>([^<]{20,})</div>'
    ]
    
    for pattern in desc_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            desc = match.strip()
            if len(desc) > 20 and not re.match(r'^\d+[/\-\.]\d+[/\-\.]\d+$', desc):
                return desc
    
    # Fallback: use clean text if it's meaningful
    if len(clean_text) > 20 and len(clean_text) < 500:
        return clean_text
    
    return ""

def extract_pdf_link(text, base_url):
    """Extract PDF link from HTML text"""
    pdf_patterns = [
        r'href="([^"]*\.pdf[^"]*)"',
        r'href=\'([^\']*\.pdf[^\']*)\'',
        r'url\(["\']([^"\']*\.pdf[^"\']*)["\']',
    ]
    
    for pattern in pdf_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pdf_link = match.group(1)
            if not pdf_link.startswith('http'):
                pdf_link = urljoin(base_url, pdf_link)
            return pdf_link
    
    return None

if __name__ == "__main__":
    try:
        count = scrape_dte_circulars()
        print(f"Scraper completed successfully with {count} circulars")
        timeout_timer.cancel()  # Cancel timeout if successful
        sys.exit(0 if count > 0 else 1)
    except TimeoutException:
        print("ERROR: Script timed out after 150 seconds")
        # Create empty files to prevent frontend errors
        os.makedirs('data', exist_ok=True)
        empty_files = ['latest.json', 'dvp.json', 'exam.json', 'acm.json', 'departmental.json']
        for file in empty_files:
            with open(f'data/{file}', 'w') as f:
                json.dump([], f)
        
        # Create timestamp with timeout status
        timestamp = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "timeout",
            "circulars_count": 0
        }
        with open('data/timestamp.json', 'w') as f:
            json.dump(timestamp, f, indent=2)
        
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        timeout_timer.cancel()  # Cancel timeout on error
        sys.exit(1)