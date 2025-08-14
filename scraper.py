import requests
from bs4 import BeautifulSoup
import ssl
import urllib3
from urllib.parse import urljoin
import re
from datetime import datetime
import logging
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DTECircularScraper:
    def __init__(self):
        self.base_url = "https://dtek.karnataka.gov.in/"
        self.circulars_url = "https://dtek.karnataka.gov.in/info-4/Departmental+Circulars/kn"
        
        # Alternative URLs to try
        self.alternative_urls = [
            "https://dtek.karnataka.gov.in/info-4/Departmental+Circulars/kn",
            "http://dtek.karnataka.gov.in/info-4/Departmental+Circulars/kn",
            "https://dtek.karnataka.gov.in/info-4/Departmental%20Circulars/kn"
        ]
        
        self.session = requests.Session()
        
        # Railway-optimized headers with multiple user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Configure session for Railway deployment
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Aggressive retry strategy for Railway
        retry_strategy = Retry(
            total=5,  # More retries
            backoff_factor=1,  # Longer backoff
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            connect=3,  # More connection retries
            read=3,     # More read retries
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def scrape_circulars(self, limit=20):
        """
        Scrape circulars from DTE Karnataka website with Railway optimization
        Returns list of circular dictionaries with error handling
        """
        import os
        
        # Log Railway environment but attempt scraping anyway
        if 'RAILWAY_ENVIRONMENT' in os.environ:
            logger.info("Railway environment detected - using aggressive retry strategy")
        
        # Try multiple approaches
        response = None
        last_error = None
        
        # Approach 1: Try all alternative URLs with different methods
        for attempt, url in enumerate(self.alternative_urls, 1):
            try:
                logger.info(f"Attempt {attempt}: Trying URL {url}")
                
                # Randomize user agent for each attempt
                self.session.headers['User-Agent'] = random.choice(self.user_agents)
                
                # Try with longer timeout for Railway
                response = self.session.get(
                    url,
                    timeout=(30, 60),  # Much longer timeouts
                    verify=False,
                    allow_redirects=True,
                    stream=False
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200 and len(response.content) > 1000:
                    logger.info(f"Success with URL {url}")
                    break
                else:
                    logger.warning(f"Invalid response from {url}: status={response.status_code}, size={len(response.content)}")
                    response = None
                    
            except Exception as e:
                logger.warning(f"Failed attempt {attempt} with {url}: {e}")
                last_error = e
                response = None
                
                # Wait between attempts
                if attempt < len(self.alternative_urls):
                    time.sleep(random.uniform(2, 5))
        
        # If all URLs failed, try with different session configuration
        if not response:
            logger.info("Trying with fresh session and different configuration...")
            try:
                fresh_session = requests.Session()
                fresh_session.verify = False
                fresh_session.headers.update({
                    'User-Agent': 'curl/7.68.0',
                    'Accept': '*/*',
                    'Connection': 'close'
                })
                
                response = fresh_session.get(
                    self.circulars_url,
                    timeout=(45, 90),
                    verify=False,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    logger.info("Success with fresh session")
                else:
                    response = None
                    
            except Exception as e:
                logger.error(f"Fresh session also failed: {e}")
                last_error = e
        
        if not response:
            if last_error:
                raise last_error
            else:
                raise Exception("All connection attempts failed")
        
        try:
            logger.info("Starting HTML parsing...")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            circulars = []
            
            # Try different possible table selectors
            tables = soup.find_all('table')
            
            if not tables:
                logger.warning("No tables found on the page")
                return []
            
            # Look for the table with circulars data
            target_table = None
            for table in tables:
                headers = table.find_all('th') or table.find_all('td')
                if headers and len(headers) >= 4:
                    # Check if it looks like the circulars table
                    header_text = ' '.join([h.get_text(strip=True).lower() for h in headers[:4]])
                    if any(keyword in header_text for keyword in ['date', 'order', 'subject', 'view', 'ದಿನಾಂಕ', 'ಆದೇಶ']):
                        target_table = table
                        break
            
            if not target_table:
                logger.warning("Could not find circulars table")
                return []
            
            # Extract rows from table
            rows = target_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows[:limit]:
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        # Extract data from cells
                        date_cell = cells[0].get_text(strip=True)
                        order_cell = cells[1].get_text(strip=True)
                        subject_cell = cells[2].get_text(strip=True)
                        view_cell = cells[3]
                        
                        # Find PDF link
                        pdf_link = ""
                        link_tag = view_cell.find('a')
                        if link_tag and link_tag.get('href'):
                            href = link_tag.get('href')
                            # Convert relative URLs to absolute
                            if href.startswith('http'):
                                pdf_link = href
                            else:
                                pdf_link = urljoin(self.base_url, href)
                        
                        # Clean and format data
                        circular = {
                            'date': self._parse_date(date_cell),
                            'order_no': order_cell,
                            'subject': subject_cell,
                            'pdf_link': pdf_link
                        }
                        
                        # Only add if we have essential data
                        if circular['subject'] and (circular['order_no'] or circular['date']):
                            circulars.append(circular)
                            
                except Exception as e:
                    logger.error(f"Error parsing row: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(circulars)} circulars")
            return circulars
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Certificate error: {e}")
            raise Exception("SSL Certificate verification failed. The website's security certificate could not be verified.")
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise Exception("Request timed out. The website took too long to respond.")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise Exception("Failed to connect to the website. Please check your internet connection.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Error fetching data from website: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def _parse_date(self, date_str):
        """
        Parse date string and return formatted date
        Handles various date formats including Kannada dates
        """
        if not date_str:
            return ""
        
        # Clean the date string
        date_str = date_str.strip()
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',  # DD/MM/YY or DD-MM-YY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[2]) == 2:  # Two digit year
                        year = 2000 + int(groups[2]) if int(groups[2]) < 50 else 1900 + int(groups[2])
                    else:
                        year = int(groups[2])
                    
                    if len(groups) == 3:
                        if year == int(groups[2]):  # YYYY/MM/DD format
                            day, month = int(groups[1]), int(groups[0])
                        else:  # DD/MM/YYYY format
                            day, month = int(groups[0]), int(groups[1])
                        
                        date_obj = datetime(year, month, day)
                        return date_obj.strftime('%Y-%m-%d')
                except:
                    continue
        
        # If no pattern matches, return original string
        return date_str

# Test function
if __name__ == "__main__":
    scraper = DTECircularScraper()
    try:
        circulars = scraper.scrape_circulars(5)
        for circular in circulars:
            print(f"Date: {circular['date']}")
            print(f"Order: {circular['order_no']}")
            print(f"Subject: {circular['subject'][:100]}...")
            print(f"PDF: {circular['pdf_link']}")
            print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")