#!/usr/bin/env python3
"""
Startup script for DTE Circulars with real-time scraping
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import requests
        import bs4
        import urllib3
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def start_api_server():
    """Start the API server"""
    print("🚀 Starting DTE Circulars API server...")
    try:
        # Start API server in background
        process = subprocess.Popen([
            sys.executable, "api_server.py", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ API server started successfully on port 8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def open_browser():
    """Open the web application in default browser"""
    html_file = Path("index.html").absolute()
    if html_file.exists():
        print(f"🌐 Opening {html_file} in browser...")
        webbrowser.open(f"file://{html_file}")
        return True
    else:
        print("❌ index.html not found")
        return False

def main():
    print("🔥 DTE Karnataka Circulars - Real-time Scraping Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("index.html").exists():
        print("❌ Please run this script from the DTE Circulars directory")
        return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Start API server
    server_process = start_api_server()
    
    if server_process:
        # Open browser
        time.sleep(2)
        open_browser()
        
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("📱 The web app is now open in your browser")
        print("⚡ Click 'Live Scrape' button for real-time data")
        print("🔄 Use 'Refresh Data' for cached results")
        print("⏹️  Press Ctrl+C here to stop the API server")
        print("=" * 60)
        
        try:
            # Wait for server process
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping API server...")
            server_process.terminate()
            print("✅ Server stopped")
    else:
        print("\n📱 You can still use the web app with cached data:")
        open_browser()
        print("ℹ️  Live scraping will not work without the API server")

if __name__ == "__main__":
    main()