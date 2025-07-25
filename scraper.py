import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import ssl
import urllib3
from urllib.parse import urljoin, urlparse
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DTECircularScraper:
    def __init__(self, base_url="https://dtek.karnataka.gov.in"):
        self.base_url = base_url
        self.categories = {
            'DVP': "https://dtek.karnataka.gov.in/page/Circulars/DVP/kn",
            'Exam': "https://dtek.karnataka.gov.in/page/Circulars/Exam/kn", 
            'ACM': "https://dtek.karnataka.gov.in/page/Circulars/ACM-Polytechnic/kn",
            'Departmental': "https://dtek.karnataka.gov.in/info-4/Departmental+Circulars/kn"
        }
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_page(self, url):
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def extract_circulars(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        circulars = []
        
        # Look for the main table containing circulars
        table = soup.find('table')
        if not table:
            return []
        
        # Find all rows except the header row
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows[:10]:  # Get first 10 rows
            circular = self.parse_table_row(row)
            if circular:
                circulars.append(circular)
        
        return circulars

    def parse_table_row(self, row):
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 4:
                return None
            
            # Extract data from table columns
            # Column order: Date, Order Number, Title/Description, Size, View Link
            date_text = cells[0].get_text(strip=True)
            order_number = cells[1].get_text(strip=True)
            title_text = cells[2].get_text(strip=True)
            
            # Skip if essential data is missing
            if not title_text or len(title_text) < 5:
                return None
            
            # Skip header rows
            if 'ದಿನಾಂಕ' in title_text or 'ವಿಷಯ' in title_text:
                return None
            
            # Extract view link from the last column
            link = None
            if len(cells) >= 5:
                link_element = cells[4].find('a')
                if link_element and link_element.get('href'):
                    href = link_element.get('href')
                    link = urljoin(self.base_url, href) if not href.startswith('http') else href
            
            # Create title with order number
            full_title = f"{order_number}: {title_text}" if order_number else title_text
            
            # Create description (truncate if too long)
            description = title_text
            if len(description) > 150:
                description = description[:147] + "..."
            
            return {
                'title': full_title,
                'description': description,
                'date': date_text,
                'order_number': order_number,
                'link': link,
                'source': 'DTE Karnataka'
            }
        
        except Exception as e:
            print(f"Error parsing row: {e}")
            return None

    def extract_date(self, text):
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',
            r'\d{1,2}\.\d{1,2}\.\d{4}',
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return "Date not available"

    def scrape_circulars(self, category='DVP'):
        print(f"Fetching DTE Karnataka {category} circulars...")
        
        target_url = self.categories.get(category, self.categories['DVP'])
        html_content = self.fetch_page(target_url)
        if not html_content:
            return []
        
        circulars = self.extract_circulars(html_content)
        return circulars

    def scrape_all_categories(self):
        all_data = {}
        
        for category, url in self.categories.items():
            print(f"\nScraping {category} circulars from {url}")
            circulars = self.scrape_circulars(category)
            all_data[category] = circulars
            print(f"Found {len(circulars)} {category} circulars")
        
        return all_data

    def save_to_json(self, circulars, filename='circulars.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(circulars, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(circulars)} circulars to {filename}")

def main():
    import sys
    import os
    
    # Set UTF-8 encoding for console output
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    scraper = DTECircularScraper()
    
    # Check if we should scrape all categories or just one
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        print("Scraping all categories...")
        all_data = scraper.scrape_all_categories()
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save each category to separate files
        for category, circulars in all_data.items():
            filename = f"data/{category.lower()}.json"
            scraper.save_to_json(circulars, filename)
            print(f"Saved {len(circulars)} {category} circulars to {filename}")
        
        # Also save DVP as the default latest.json
        if 'DVP' in all_data:
            scraper.save_to_json(all_data['DVP'], 'data/latest.json')
            scraper.save_to_json(all_data['DVP'], 'circulars.json')  # Backward compatibility
            print("Saved DVP circulars as latest.json")
        
    else:
        # Default behavior - scrape DVP circulars only
        circulars = scraper.scrape_circulars('DVP')
        
        if circulars:
            print(f"\n=== Recent {len(circulars)} DVP Circulars from DTE Karnataka ===\n")
            
            for i, circular in enumerate(circulars, 1):
                try:
                    print(f"{i}. {circular['title']}")
                    print(f"   Date: {circular['date']}")
                    print(f"   Order: {circular.get('order_number', 'N/A')}")
                    if circular['link']:
                        print(f"   Link: {circular['link']}")
                    print(f"   Description: {circular['description']}")
                    print("-" * 80)
                except UnicodeEncodeError:
                    # Fallback for problematic characters
                    title = circular['title'].encode('ascii', 'ignore').decode('ascii')
                    desc = circular['description'].encode('ascii', 'ignore').decode('ascii')
                    print(f"{i}. {title}")
                    print(f"   Date: {circular['date']}")
                    print(f"   Order: {circular.get('order_number', 'N/A')}")
                    if circular['link']:
                        print(f"   Link: {circular['link']}")
                    print(f"   Description: {desc}")
                    print("-" * 80)
            
            scraper.save_to_json(circulars)
            
        else:
            print("No circulars found. The website structure might have changed.")
            print("Please check the website manually and update the scraper if needed.")

if __name__ == "__main__":
    main()