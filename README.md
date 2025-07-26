# DTE Karnataka Circulars

A modern web application to display recent circulars, notices, and government orders from the DTE Karnataka website.

## 🌐 Live Application

Visit: **[https://tejukargal.github.io/DTE-Circulars/](https://tejukargal.github.io/DTE-Circulars/)**

## ✨ Features

- **Auto-Updated Data**: Refreshed every 6 hours via GitHub Actions
- **Multi-Category Support**: DVP, Exam, ACM, and Departmental circulars
- **Modern UI**: Clean, responsive design with dark/light mode
- **Enhanced Cards**: Serial numbers with circular backgrounds and zoom effects
- **Share Functionality**: Share circulars with complete details (subject, date, order number, PDF link)
- **Mobile Optimized**: Works perfectly on all devices
- **PDF Integration**: Direct links to official documents
- **Export Feature**: Download data as JSON

## 🎨 Design Features

- Circular serial numbers with hover zoom effects
- Clean card layout without duplicate information
- Color-coded metadata (dates in blue, order numbers in green)
- Responsive mobile design
- Dark/light theme toggle
- Professional government portal aesthetics

## 📱 Mobile Support

- Touch-friendly interface
- Optimized button sizing
- Stacked layout for small screens
- Fast loading on mobile networks

## 🔄 Data Updates

The application automatically updates circular data using:
- **GitHub Actions**: Scheduled every 6 hours
- **Python Scraper**: Extracts data from official DTE website
- **JSON Storage**: Structured data format for fast loading

## 📂 Repository Structure

```
├── index.html              # Main application file
├── data/                   # Circular data (auto-updated)
│   ├── dvp.json
│   ├── exam.json
│   ├── acm.json
│   ├── departmental.json
│   ├── latest.json
│   └── timestamp.json
├── .github/workflows/      # Auto-update workflow
└── README.md
```

## 🚀 Technology Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript (no frameworks)
- **Hosting**: GitHub Pages (static hosting)
- **Data**: JSON files updated via GitHub Actions
- **Automation**: Python scraper with scheduled workflows

## 📊 Categories

- **DVP Circulars**: Director of Technical Education orders
- **Exam Circulars**: Examination-related notifications  
- **ACM Circulars**: Academic and curriculum matters
- **Departmental Circulars**: General departmental notices

## 🔗 Official Reference

For the most accurate and complete information, always refer to the official DTE Karnataka website.