# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application that scrapes and displays departmental circulars from the DTE (Directorate of Technical Education) Karnataka government website. The app provides a modern web interface to view the latest 20 circulars with features like dark/light mode, sharing functionality, and responsive design.

### Tech Stack
- **Backend**: Python Flask 2.3.3 with web scraping capabilities
- **Scraping**: BeautifulSoup 4.12.2 + lxml 4.9.3 for HTML parsing
- **HTTP Client**: requests 2.31.0 with SSL bypass for government website
- **Frontend**: Vanilla JavaScript with CSS Grid layout
- **Deployment**: Gunicorn 21.2.0 ready with Heroku configuration

## Development Commands

### Quick Start (Recommended)
```bash
# Windows
run.bat

# Linux/Mac
chmod +x run.sh && ./run.sh
```

### Manual Development Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt

# Run application
python app.py
```

### Testing and Demo
```bash
# Test scraper functionality independently
python demo.py

# Direct scraper testing
python scraper.py
```

### Production Deployment
```bash
# Using Gunicorn (production)
gunicorn app:app

# With port specification
gunicorn app:app --bind 0.0.0.0:5000
```

## Architecture and Code Structure

### Core Components

**app.py** - Main Flask application with three key endpoints:
- `/` - Serves the main HTML interface
- `/api/circulars` - JSON API that fetches and returns scraped data with serial numbers
- `/proxy-pdf` - CORS proxy for PDF viewing (handles government website restrictions)

**scraper.py** - Web scraping engine with robust error handling:
- `DTECircularScraper` class handles all scraping logic
- Bypasses SSL certificate issues common with government websites
- Parses HTML tables containing circular data (date, order number, subject, PDF links)
- Handles multiple date formats including Kannada text
- 30-second timeout with comprehensive error handling

**templates/index.html** - Single-page application interface:
- Responsive CSS Grid layout (2 columns on mobile, 4+ on desktop)
- Dark/light theme toggle with localStorage persistence
- Loading states and error handling UI

**static/** directory:
- `style.css` - Modern CSS with CSS Grid, dark mode variables, and animations
- `script.js` - Vanilla JavaScript for API calls, theme switching, and share functionality

### Key Design Patterns

1. **No Database/Caching**: Application fetches fresh data on every request to ensure up-to-date information
2. **SSL Bypass**: Configured for government websites with certificate issues (`verify=False`)
3. **Error-First Design**: Comprehensive error handling for network, SSL, timeout, and parsing issues
4. **Mobile-First Responsive**: CSS Grid with mobile-optimized card layouts
5. **Progressive Enhancement**: Works without JavaScript, enhanced with JS features

### Environment Configuration

- **Development**: Uses Flask development server on port 5000
- **Production**: Configured for Heroku with `Procfile` and `runtime.txt`
- **Python Version**: 3.9.20 (specified in runtime.txt)
- **Environment Variables**: 
  - `PORT` for production port binding
  - `FLASK_ENV=development` for debug mode

### Data Flow

1. User loads `/` → serves index.html
2. JavaScript calls `/api/circulars` → scraper.py fetches from DTE website
3. HTML table parsing → structured JSON with serial numbers
4. Frontend renders cards with PDF links and sharing functionality
5. PDF viewing uses `/proxy-pdf` to handle CORS restrictions

### Government Website Specifics

- **Target URL**: https://dtek.karnataka.gov.in/info-4/Departmental+Circulars/kn
- **Language**: Mixed English/Kannada content requiring Unicode handling  
- **SSL Issues**: Government site has certificate problems requiring verification bypass
- **Table Structure**: Scraper looks for tables with date/order/subject/view columns
- **PDF Links**: Converts relative URLs to absolute URLs for proper linking

### Development Notes

- Virtual environment is essential due to specific library versions
- The scraper includes fallback mechanisms for different table structures
- Error messages are user-friendly while maintaining technical logging
- Share functionality works with both native mobile sharing and clipboard copying
- Dark mode preference persists across browser sessions