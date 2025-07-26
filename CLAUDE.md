# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static web application that displays DTE Karnataka circulars, notices, and government orders. The application is built with pure HTML, CSS, and JavaScript (no frameworks) and is hosted on GitHub Pages. Data is automatically updated every 6 hours via GitHub Actions using a Python scraper.

## Architecture

- **Frontend**: Single-page application (`index.html`) with embedded CSS and JavaScript
- **Data Layer**: JSON files stored in `data/` directory, automatically updated via GitHub Actions
- **Automation**: Python scraper runs on GitHub Actions schedule to fetch latest circulars from official DTE website
- **Hosting**: GitHub Pages static hosting

## File Structure

```
├── index.html              # Main application (contains all HTML, CSS, JavaScript)
├── data/                   # Auto-updated circular data (JSON files)
│   ├── dvp.json           # DVP circulars
│   ├── exam.json          # Exam circulars  
│   ├── acm.json           # ACM circulars
│   ├── departmental.json  # Departmental circulars
│   ├── latest.json        # Latest/fallback data
│   └── timestamp.json     # Last update timestamp
├── .github/workflows/     # GitHub Actions automation
│   └── update-circulars.yml
└── .venv/                 # Python virtual environment
```

## Development Commands

### GitHub Actions Workflow
The scraper runs automatically but can be triggered manually:
- **Manual trigger**: Go to GitHub Actions tab and run "Update DTE Circulars Data" workflow
- **Schedule**: Runs every 30 minutes automatically

### Python Environment
```bash
# Activate virtual environment
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# The scraper dependencies are installed via GitHub Actions
pip install requests beautifulsoup4 lxml urllib3
```

### Local Development
- **Live server**: Use any static file server to serve `index.html`
- **Testing**: Open `index.html` directly in browser (data loads from `data/` directory)
- **Data refresh**: Circulars are automatically refreshed every 30 minutes via GitHub Actions

## Data Categories

The application supports four circular categories:
- **DVP**: Director of Technical Education orders (`dvp.json`)
- **Exam**: Examination-related notifications (`exam.json`)  
- **ACM**: Academic and curriculum matters (`acm.json`)
- **Departmental**: General departmental notices (`departmental.json`)

## Key Features

- **Auto-updates**: Data refreshed every 30 minutes via GitHub Actions
- **Multi-category support**: DVP, Exam, ACM, and Departmental circulars
- **Dark/light mode**: Theme toggle with localStorage persistence
- **Mobile responsive**: Optimized layout for all devices
- **Share functionality**: Copy circular details to clipboard or use Web Share API
- **Export feature**: Download data as JSON
- **PDF integration**: Direct links to official documents

## JavaScript Architecture

The main application logic in `index.html` includes:
- **Theme management**: Dark/light mode toggle with localStorage
- **Data loading**: Fetch JSON data from `data/` directory with fallback handling
- **Category switching**: Dynamic loading of different circular categories  
- **Share functionality**: Multi-method sharing (Web Share API, clipboard, manual copy)
- **Export functionality**: Download current data as JSON
- **Error handling**: Comprehensive error display with retry options

## Styling System

CSS uses custom properties for theming:
- **Color scheme**: CSS custom properties for light/dark mode
- **Responsive design**: Mobile-first approach with media queries
- **Card layout**: Circular items with hover effects and animations
- **Government portal aesthetics**: Professional color scheme and typography

## GitHub Actions Integration

The automation workflow (`update-circulars.yml`):
- Runs every 30 minutes automatically
- Uses Python scraper to fetch latest circulars from DTE website
- Updates JSON files in `data/` directory
- Creates timestamp file for last update tracking
- Commits and pushes changes automatically
- Creates backup files with timestamps