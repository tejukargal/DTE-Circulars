#!/usr/bin/env python3
"""
Advanced DTE Karnataka Circulars Scraper with BeautifulSoup
Scrapes circulars from https://dtek.karnataka.gov.in with real HTML parsing
"""

import requests
import json
import sys
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import os
from pathlib import Path
import time
import logging

try:
    from bs4 import BeautifulSoup
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("Required packages not found. Install with: pip install beautifulsoup4 lxml urllib3")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedDTECircularsScraper:
    def __init__(self):
        self.base_url = "https://dtek.karnataka.gov.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Category mapping based on actual website structure
        self.categories = {
            'dvp': {
                'name': 'DVP Circulars',
                'url': '/page/Circulars/DVP/kn',
                'file': 'dvp.json'
            },
            'exam': {
                'name': 'Exam Circulars',
                'url': '/page/Circulars/Exam/kn',
                'file': 'exam.json'
            },
            'acm': {
                'name': 'ACM Circulars',
                'url': '/page/Circulars/ACM/kn',
                'file': 'acm.json'
            },
            'departmental': {
                'name': 'Departmental Circulars',
                'url': '/page/Circulars/Department/kn',
                'file': 'departmental.json'
            }
        }
    
    def scrape_category(self, category_key):
        """Scrape circulars for a specific category with real HTML parsing"""
        if category_key not in self.categories:
            logger.error(f"Invalid category: {category_key}")
            return []
        
        category = self.categories[category_key]
        url = self.base_url + category['url']
        
        logger.info(f"Scraping {category['name']} from {url}")
        
        try:
            # Add delay to be respectful to the server
            time.sleep(1)
            
            response = self.session.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # Parse the HTML response
            soup = BeautifulSoup(response.content, 'html.parser')
            circulars = self._parse_circulars_table(soup, category_key)
            
            logger.info(f"Found {len(circulars)} circulars in {category['name']}")
            return circulars
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error scraping {category['name']}: {e}")
            return []
        except Exception as e:
            logger.error(f"Parsing error for {category['name']}: {e}")
            return []
    
    def _parse_circulars_table(self, soup, category_key):
        """Parse the circulars table from BeautifulSoup object"""
        circulars = []
        
        try:
            # Look for table containing circulars data
            table = soup.find('table') or soup.find('div', class_='table-responsive')
            
            if not table:
                logger.warning(f"No table found for category {category_key}")
                return circulars
            
            # Find all table rows (skip header)
            rows = table.find_all('tr')[1:] if table.find_all('tr') else []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 4:  # Expecting at least 4 columns based on screenshot
                    try:
                        # Extract data based on table structure from screenshot
                        date = self._clean_text(cells[0].get_text())
                        order_number = self._clean_text(cells[1].get_text())
                        description = self._clean_text(cells[2].get_text())
                        
                        # Look for download link in last column
                        download_cell = cells[-1]
                        download_link = None
                        
                        # Find download link
                        link_tag = download_cell.find('a')
                        if link_tag and link_tag.get('href'):
                            download_link = urljoin(self.base_url, link_tag.get('href'))
                        
                        # Create circular object
                        circular = {
                            "title": f"{order_number}: {description}",
                            "description": description,
                            "date": self._format_date(date),
                            "order_number": order_number,
                            "link": download_link,
                            "source": "DTE Karnataka",
                            "category": category_key.upper(),
                            "scraped_at": datetime.now().isoformat()
                        }
                        
                        # Only add if we have meaningful data
                        if order_number and description:
                            circulars.append(circular)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing row in {category_key}: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error parsing table for {category_key}: {e}")
        
        return circulars
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    def _format_date(self, date_str):
        """Format date string to consistent format"""
        if not date_str:
            return datetime.now().strftime("%d/%m/%Y")
        
        # Try to parse different date formats
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if len(match.group(3)) == 4:  # YYYY format
                        if '/' in date_str:
                            return date_str
                        else:
                            # Convert to DD/MM/YYYY
                            day, month, year = match.groups()
                            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                    else:
                        return date_str
                except:
                    continue
        
        return date_str
    
    def scrape_all_categories(self):
        """Scrape all categories and save to respective JSON files"""
        all_circulars = []
        
        for category_key in self.categories.keys():
            logger.info(f"Processing category: {category_key}")
            circulars = self.scrape_category(category_key)
            
            if circulars:
                # Save category-specific file
                self._save_json(circulars, f"data/{self.categories[category_key]['file']}")
                all_circulars.extend(circulars)
            
            # Add delay between categories
            time.sleep(2)
        
        # Save combined latest.json
        if all_circulars:
            self._save_json(all_circulars, "data/latest.json")
            
            # Create a backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._save_json(all_circulars, f"data/backup_{timestamp}.json")
        
        return all_circulars
    
    def _save_json(self, data, filename):
        """Save data to JSON file"""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(data)} circulars to {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    def get_live_data(self, category='all'):
        """Get live data for API endpoint - returns fresh scraped data"""
        logger.info(f"Getting live data for category: {category}")
        
        if category == 'all':
            return self.scrape_all_categories()
        elif category in self.categories:
            return self.scrape_category(category)
        else:
            logger.error(f"Invalid category: {category}")
            return []
    
    def test_connection(self):
        """Test connection to DTE website"""
        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            response.raise_for_status()
            logger.info("✅ Connection to DTE website successful")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Advanced DTE Karnataka Circulars Scraper')
    parser.add_argument('--category', choices=['dvp', 'exam', 'acm', 'departmental', 'all'], 
                       default='all', help='Category to scrape')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--all', action='store_true', help='Scrape all categories')
    parser.add_argument('--test', action='store_true', help='Test connection only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scraper = AdvancedDTECircularsScraper()
    
    # Test connection first
    if args.test:
        scraper.test_connection()
        return
    
    if not scraper.test_connection():
        logger.error("Cannot connect to DTE website. Exiting.")
        return
    
    try:
        if args.all or args.category == 'all':
            circulars = scraper.scrape_all_categories()
            if args.output:
                scraper._save_json(circulars, args.output)
        else:
            circulars = scraper.scrape_category(args.category)
            if args.output:
                scraper._save_json(circulars, args.output)
            elif circulars:
                scraper._save_json(circulars, f"data/{scraper.categories[args.category]['file']}")
        
        logger.info(f"✅ Scraping completed. Total circulars: {len(circulars)}")
        return len(circulars)
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return 0

if __name__ == "__main__":
    main()