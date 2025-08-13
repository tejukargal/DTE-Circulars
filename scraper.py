import requests
from bs4 import BeautifulSoup
import ssl
import urllib3
from urllib.parse import urljoin
import re
from datetime import datetime
import logging

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DTECircularScraper:
    def __init__(self):
        self.base_url = "https://dtek.karnataka.gov.in/"
        self.circulars_url = "https://dtek.karnataka.gov.in/info-4/Departmental+Circulars/kn"
        self.session = requests.Session()
        
        # Configure session for SSL issues
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_circulars(self, limit=20):
        """
        Scrape circulars from DTE Karnataka website
        Returns list of circular dictionaries with error handling
        """
        try:
            logger.info("Starting to scrape DTE circulars...")
            
            # Make request with timeout and SSL bypass
            response = self.session.get(
                self.circulars_url,
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            
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