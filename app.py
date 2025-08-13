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

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/circulars')
def get_circulars():
    """API endpoint to get circulars data with serial numbers"""
    try:
        logger.info("Fetching circulars from API endpoint")
        circulars = scraper.scrape_circulars(limit=20)
        
        # Add serial numbers starting from 1
        for i, circular in enumerate(circulars, 1):
            circular['serial_no'] = i
        
        return jsonify({
            'success': True,
            'circulars': circulars,
            'count': len(circulars)
        })
        
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'circulars': []
        }), 500

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