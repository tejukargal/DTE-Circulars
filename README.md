# DTE Karnataka Circulars Web App

A modern web application to view and access departmental circulars from the Directorate of Technical Education (DTE), Karnataka Government.

![DTE Circulars App](https://img.shields.io/badge/Status-Active-green) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey)

## Features

- **Real-time scraping**: Fetches circulars directly from the DTE website on every request
- **Optimized card design**: Larger cards with improved readability and full text display
- **Serial numbering**: Cards are numbered 1-20 in website order with clear serial numbers
- **Organized headers**: Each card header shows Serial # with Date and Order Number stacked below
- **Dark/Light mode**: Toggle between dark and light themes with persistent preference
- **Full text display**: Complete subject content displayed without truncation
- **Optimized typography**: Font sizes optimized for card dimensions and readability
- **Uniform card layout**: All cards have identical height (300px) with consistent button positioning
- **Perfect button alignment**: Rectangular buttons with equal dimensions and proper spacing from card edges
- **Smart sharing**: Share circulars with formatted message including Date, Order & Subject
- **Mobile optimized**: 2-column layout on mobile devices with responsive design
- **Solid color design**: Modern UI with vibrant solid colors and smooth animations
- **Smooth animations**: Elegant hover effects, loading spinners, and card transitions
- **No text wrapping**: Header information displays without text wrapping or overflow
- **Error handling**: Comprehensive handling for SSL certificate errors, timeouts, and connection issues
- **No caching**: Always displays the most recent circulars (20 latest)
- **Cross-device responsive**: Optimized for desktop, tablet, and mobile displays

## 🚀 Quick Installation

### For Windows Users (Recommended)
1. Download `install.bat` from this repository
2. Right-click and "Run as Administrator" 
3. Follow the installation prompts
4. Run `run.bat` to start the app
5. Open http://localhost:5000

### For Developers
```bash
git clone https://github.com/tejukargal/DTE-Circulars.git
cd DTE-Circulars
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

### Manual Setup
1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
**Windows:**
```bash
venv\Scripts\activate
```
**Linux/Mac:**
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and go to: `http://localhost:5000`

## Usage

- The app automatically loads the latest 20 circulars when opened
- **Header Controls**: Top-left Refresh (🔄) and top-right Dark Mode (🌙/☀️) buttons
- Click the "🔄 Refresh" button to fetch the latest circulars with smooth loading animation
- Click the "🌙 Dark / ☀️ Light" button to switch themes
- Each circular card shows:
  - **Header**: Serial number (#1, #2, etc.) with Date and Order Number stacked below
  - **Body**: Complete subject/description with optimized font size and full text display
  - **Actions**: Two buttons fixed at bottom of each card with uniform positioning
- **Open PDF**: Opens the PDF document in a new browser tab
- **Share**: Share circular with formatted message including:
  - **Bold headers** for Serial No, Date, Order No, and Subject
  - **Proper alignment** with emojis for better readability
  - **PDF link** for direct access
  - Works with native share (mobile) or clipboard copy (desktop)
- **Mobile Experience**: 2-column layout with compact cards optimized for touch
- Cards animate smoothly when loading and on hover
- Your dark/light mode preference is automatically saved
- The app handles Kannada content from the DTE website

## Error Handling

The application handles several types of errors:

- **SSL Certificate Errors**: Bypasses certificate verification for the DTE website
- **Timeout Errors**: 30-second timeout with user-friendly error messages
- **Connection Errors**: Network connectivity issue handling
- **Parsing Errors**: Graceful handling of HTML structure changes

## Technical Details

- **Backend**: Python Flask with BeautifulSoup for web scraping
- **Frontend**: Vanilla JavaScript with modern CSS Grid
- **No Database**: Data is fetched fresh on every request
- **No Caching**: Ensures always up-to-date information

## File Structure

```
├── app.py              # Flask web server
├── scraper.py          # Web scraping logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main HTML template
└── static/
    ├── style.css      # CSS styling
    └── script.js      # JavaScript functionality
```