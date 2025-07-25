from flask import Flask, render_template, jsonify
from scraper import DTECircularScraper
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/circulars')
def get_circulars():
    try:
        scraper = DTECircularScraper()
        circulars = scraper.scrape_circulars()
        
        return jsonify({
            'success': True,
            'count': len(circulars),
            'circulars': circulars,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'circulars': []
        }), 500

@app.route('/refresh')
def refresh_circulars():
    return get_circulars()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)