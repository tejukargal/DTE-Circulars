from flask import Flask, render_template, jsonify, send_from_directory, request, Response
from scraper import DTECircularScraper
import logging
import requests
from urllib.parse import urlparse

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scraper
scraper = DTECircularScraper()

def _get_sample_data():
    """Provide sample data when real scraping fails (for demo purposes)"""
    from datetime import datetime, timedelta
    base_date = datetime.now()
    
    sample_circulars = []
    for i in range(5):
        date_str = (base_date - timedelta(days=i*2)).strftime('%Y-%m-%d')
        sample_circulars.append({
            'serial_no': i + 1,
            'date': date_str,
            'order_no': f'DTE/ADMIN/{2024 + i}/SAMPLE-{i+1:03d}',
            'subject': f'Sample Circular {i+1}: Railway deployment demo data - This is sample content shown when the DTE website cannot be accessed from cloud platforms',
            'pdf_link': 'https://example.com/sample.pdf'
        })
    
    return sample_circulars

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/circulars')
def get_circulars():
    """API endpoint to get circulars data from GitHub Actions updated file"""
    try:
        logger.info("API endpoint called - loading circulars data")
        import os
        import json
        from datetime import datetime
        
        # Log environment info
        logger.info(f"Environment: Railway={'RAILWAY_ENVIRONMENT' in os.environ}")
        
        # Try to load from data file first (GitHub Actions updated)
        data_file = 'data/circulars.json'
        circulars = []
        data_source = "file"
        
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                circulars = data.get('circulars', [])
                last_updated = data.get('last_updated', 'Unknown')
                logger.info(f"Loaded {len(circulars)} circulars from data file (updated: {last_updated})")
                
                # Check if data is recent (less than 24 hours old)
                try:
                    updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - updated_time).total_seconds() / 3600
                    if age_hours > 24:
                        logger.warning(f"Data file is {age_hours:.1f} hours old")
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Error reading data file: {e}")
                circulars = []
        
        # Fallback to live scraping only if no data file exists and not on Railway
        if not circulars and 'RAILWAY_ENVIRONMENT' not in os.environ:
            logger.info("No data file found, attempting live scraping...")
            try:
                circulars = scraper.scrape_circulars(limit=20)
                data_source = "live_scraping"
                logger.info(f"Successfully scraped {len(circulars)} circulars")
                
                # Add serial numbers
                for i, circular in enumerate(circulars, 1):
                    circular['serial_no'] = i
            except Exception as e:
                logger.error(f"Live scraping failed: {e}")
                circulars = []
        
        # Final fallback to sample data
        if not circulars:
            logger.info("Using sample data as final fallback")
            circulars = _get_sample_data()
            data_source = "sample_data"
        
        return jsonify({
            'success': True,
            'circulars': circulars,
            'count': len(circulars),
            'data_source': data_source
        })
        
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}", exc_info=True)
        
        # Provide helpful error message for Railway deployment issues
        error_msg = str(e)
        is_railway = 'RAILWAY_ENVIRONMENT' in os.environ
        
        if is_railway:
            if any(keyword in error_msg.lower() for keyword in ['timeout', 'timed out', 'connection', 'ssl', 'network']):
                logger.info("Railway deployment network issue detected - returning sample data")
                # Return successful response with sample data for Railway
                sample_data = _get_sample_data()
                for i, circular in enumerate(sample_data, 1):
                    circular['serial_no'] = i
                
                return jsonify({
                    'success': True,
                    'circulars': sample_data,
                    'count': len(sample_data),
                    'notice': 'Demo data shown due to Railway network restrictions'
                })
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'circulars': _get_sample_data(),  # Provide sample data as fallback
            'debug_info': {
                'error_type': type(e).__name__,
                'railway_env': is_railway,
                'fallback_data': True
            }
        }), 200  # Return 200 with fallback data instead of 500

@app.route('/pdf-viewer/<path:pdf_url>')
def pdf_viewer(pdf_url):
    """Serve PDF viewer page"""
    return render_template('pdf_viewer.html', pdf_url=pdf_url)

@app.route('/proxy-pdf')
def proxy_pdf():
    """Proxy PDF requests to handle CORS issues"""
    pdf_url = request.args.get('url')
    if not pdf_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        response = requests.get(pdf_url, verify=False, timeout=30)
        response.raise_for_status()
        
        return Response(
            response.content,
            mimetype='application/pdf',
            headers={'Content-Disposition': 'inline'}
        )
    except Exception as e:
        logger.error(f"Error proxying PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-data', methods=['POST'])
def update_data():
    """Manual endpoint to update circulars data (for local use only)"""
    import os
    import json
    from datetime import datetime
    
    # Only allow from local environment for security
    if 'RAILWAY_ENVIRONMENT' in os.environ:
        return jsonify({'error': 'Manual updates not allowed on Railway deployment'}), 403
    
    try:
        logger.info("Manual data update triggered")
        
        # Scrape fresh data
        circulars = scraper.scrape_circulars(limit=25)
        
        if not circulars:
            return jsonify({'error': 'No circulars found during scraping'}), 400
        
        # Add serial numbers
        for i, circular in enumerate(circulars, 1):
            circular['serial_no'] = i
        
        # Create data structure
        data = {
            'circulars': circulars,
            'count': len(circulars),
            'last_updated': datetime.now().isoformat(),
            'source': 'manual_update'
        }
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Write to data file
        with open('data/circulars.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully updated data with {len(circulars)} circulars")
        
        return jsonify({
            'success': True,
            'message': f'Data updated with {len(circulars)} circulars',
            'timestamp': data['last_updated']
        })
        
    except Exception as e:
        logger.error(f"Error during manual update: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    if debug_mode:
        print("Starting DTE Circulars Web App...")
        print("Open your browser and go to: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)