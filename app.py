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
    """API endpoint to get fresh circulars data from live scraping"""
    try:
        logger.info("API endpoint called - fetching live data")
        
        # Always fetch fresh data from the website
        logger.info("Attempting live scraping...")
        circulars = scraper.scrape_circulars(limit=20)
        
        if circulars:
            # Add serial numbers
            for i, circular in enumerate(circulars, 1):
                circular['serial_no'] = i
            
            logger.info(f"Successfully scraped {len(circulars)} circulars")
            data_source = "live_scraping"
        else:
            # Fallback to sample data if scraping fails
            logger.info("Live scraping failed - using sample data")
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
        
        # Return sample data as fallback
        logger.info("Error occurred - returning sample data")
        sample_data = _get_sample_data()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'circulars': sample_data,  # Provide sample data as fallback
            'count': len(sample_data),
            'data_source': 'sample_data'
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