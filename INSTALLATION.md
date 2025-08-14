# DTE Karnataka Circulars - Installation Guide

## Quick Installation (Recommended)

### Prerequisites
- **Python 3.9+**: Download from [python.org](https://python.org)
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
- **Git**: Download from [git-scm.com](https://git-scm.com/download/win)

### One-Click Installation
1. Download `install.bat` from the repository
2. Right-click and "Run as Administrator"
3. Follow the prompts

## Manual Installation

### Step 1: Clone Repository
```cmd
git clone https://github.com/tejukargal/DTE-Circulars.git
cd DTE-Circulars
```

### Step 2: Set Up Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 4: Run Application
```cmd
run.bat
```

The app will be available at: **http://localhost:5000**

## Features

✅ **Real-time scraping** of DTE Karnataka circulars  
✅ **Modern web interface** with dark/light mode  
✅ **Responsive design** - works on mobile and desktop  
✅ **PDF viewing** and sharing functionality  
✅ **No database required** - fetches fresh data every time  

## Updating Data

To get the latest circulars:
```cmd
python update_data.py
```

This will:
- Scrape fresh data from DTE website
- Update the data file
- Ready for deployment

## Deployment Options

### 1. Local Development
- Run `run.bat` for local access
- Access at `http://localhost:5000`

### 2. Railway Deployment
- Connect GitHub repository to Railway
- Automatic deployments on git push
- Free hosting with real domain

### 3. Other Cloud Platforms
- Works on Heroku, Vercel, PythonAnywhere
- Uses standard Python/Flask stack
- Includes Procfile and requirements.txt

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Ensure "Add to PATH" was checked
- Restart Command Prompt

### "Git not found" 
- Install Git from git-scm.com
- Restart Command Prompt

### "Virtual environment issues"
- Delete `venv` folder
- Run `python -m venv venv` again

### "Dependencies failed to install"
- Ensure internet connection
- Try: `pip install --upgrade pip`
- Then: `pip install -r requirements.txt`

### "App shows demo data"
- Run `python update_data.py` to fetch real data
- Check internet connection
- Government website may be temporarily down

## Project Structure

```
DTE-Circulars/
├── app.py              # Main Flask application
├── scraper.py          # Web scraping logic
├── templates/          # HTML templates
├── static/            # CSS, JS, assets
├── data/              # Data files
├── requirements.txt   # Python dependencies
├── run.bat           # Quick start script
├── update_data.py    # Manual data update
└── install.bat       # Installation script
```

## Requirements

- **Python**: 3.9 or higher
- **Memory**: 100MB RAM
- **Storage**: 50MB disk space
- **Network**: Internet connection for scraping

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check this installation guide
2. Review the troubleshooting section
3. Create an issue on GitHub repository