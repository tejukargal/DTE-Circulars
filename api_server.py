#!/usr/bin/env python3
"""
Simple API server for real-time DTE circulars data
Provides CORS-enabled endpoints for the web app
"""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import time
import sys

# Import our scraper
try:
    from advanced_scraper import AdvancedDTECircularsScraper
except ImportError:
    print("Error: advanced_scraper.py not found")
    sys.exit(1)

class CircularsAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.scraper = AdvancedDTECircularsScraper()
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse URL
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Route handling
            if path == '/api/circulars':
                self.handle_circulars_request(query_params)
            elif path == '/api/live':
                self.handle_live_request(query_params)
            elif path == '/api/status':
                self.handle_status_request()
            elif path == '/api/categories':
                self.handle_categories_request()
            else:
                self.send_error_response("Endpoint not found", 404)
                
        except Exception as e:
            self.send_error_response(f"Server error: {str(e)}", 500)
    
    def handle_circulars_request(self, query_params):
        """Handle /api/circulars endpoint - returns cached data"""
        category = query_params.get('category', ['all'])[0]
        
        try:
            if category == 'all':
                # Try to read latest.json
                data = self.read_json_file('data/latest.json')
            else:
                # Try to read category-specific file
                filename = f"data/{category}.json"
                data = self.read_json_file(filename)
            
            response = {
                'success': True,
                'data': data,
                'category': category,
                'count': len(data),
                'source': 'cached',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Error reading cached data: {str(e)}", 500)
    
    def handle_live_request(self, query_params):
        """Handle /api/live endpoint - scrapes fresh data"""
        category = query_params.get('category', ['all'])[0]
        
        try:
            print(f"Scraping live data for category: {category}")
            
            # Get fresh data from scraper
            if category == 'all':
                data = self.scraper.scrape_all_categories()
            else:
                data = self.scraper.scrape_category(category)
            
            response = {
                'success': True,
                'data': data,
                'category': category,
                'count': len(data),
                'source': 'live_scraped',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Error scraping live data: {str(e)}", 500)
    
    def handle_status_request(self):
        """Handle /api/status endpoint - returns server status"""
        try:
            # Check if data files exist
            data_files = {}
            for category in ['dvp', 'exam', 'acm', 'departmental']:
                filename = f"data/{category}.json"
                if os.path.exists(filename):
                    stat = os.stat(filename)
                    data_files[category] = {
                        'exists': True,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                else:
                    data_files[category] = {'exists': False}
            
            # Test connection
            connection_ok = self.scraper.test_connection()
            
            response = {
                'success': True,
                'server_time': datetime.now().isoformat(),
                'connection': 'ok' if connection_ok else 'failed',
                'data_files': data_files,
                'categories': list(self.scraper.categories.keys())
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Error checking status: {str(e)}", 500)
    
    def handle_categories_request(self):
        """Handle /api/categories endpoint - returns available categories"""
        try:
            response = {
                'success': True,
                'categories': self.scraper.categories,
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(f"Error getting categories: {str(e)}", 500)
    
    def read_json_file(self, filename):
        """Read JSON file and return data"""
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def send_error_response(self, message, status_code=400):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_server(port=8000):
    """Run the API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CircularsAPIHandler)
    
    print(f"🚀 DTE Circulars API Server starting on port {port}")
    print(f"📡 Endpoints available:")
    print(f"   GET  http://localhost:{port}/api/circulars?category=dvp")
    print(f"   GET  http://localhost:{port}/api/live?category=all")
    print(f"   GET  http://localhost:{port}/api/status")
    print(f"   GET  http://localhost:{port}/api/categories")
    print(f"🌐 CORS enabled for all origins")
    print(f"⏹️  Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='DTE Circulars API Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    
    args = parser.parse_args()
    
    run_server(args.port)