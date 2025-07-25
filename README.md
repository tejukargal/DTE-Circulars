# DTE Karnataka Circulars Scraper

A web application to scrape and display recent circulars, notices, and government orders from the DTE Karnataka website.

## Features

- Scrapes the latest 10 circulars from DTE Karnataka website
- Clean, organized web interface
- JSON export functionality
- Handles SSL certificate issues
- Responsive design
- Real-time refresh capability

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For the web app, also install Flask:
```bash
pip install flask
```

## Usage

### 🖥️ Desktop GUI Application (Recommended)

Double-click `start_gui.bat` or run:
```bash
python gui_app.py
```

Features:
- Modern desktop interface
- Clickable PDF links
- Real-time refresh
- JSON export functionality
- No browser required

### 🌐 Web Application

Double-click `start_webapp.bat` or run:
```bash
python web_app.py
```

Then open your browser to: `http://localhost:5000`

Features:
- Clean, responsive web interface
- Mobile-friendly design
- Real-time refresh capability
- Direct PDF links

### 💻 Command Line Scraper

Double-click `run_scraper.bat` or run:
```bash
python scraper.py
```

Features:
- Terminal-based output
- Automatic JSON export
- Quick data extraction

## Files

- `scraper.py` - Main scraping logic
- `web_app.py` - Flask web application
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Technical Details

The scraper handles:
- SSL certificate verification issues
- Multiple HTML structure patterns
- Date extraction from various formats
- Link resolution and normalization
- Error handling and retry logic

## Troubleshooting

If the scraper returns no results:
1. Check if the website is accessible
2. The website structure may have changed
3. Try running with different network settings
4. Check the console output for specific errors