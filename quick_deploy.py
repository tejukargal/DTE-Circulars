#!/usr/bin/env python3
"""
Quick deployment script for DTE Circulars to GitHub Pages
This script automates the git operations for deployment
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"{'🔄' if description else ''} {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description or 'Command'} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or 'Command'} failed: {e.stderr}")
        return None

def main():
    print("=" * 60)
    print("   DTE Circulars - GitHub Pages Deployment")
    print("=" * 60)
    print()
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("\n❌ Git is not installed. Please install Git and try again.")
        print("Download from: https://git-scm.com/download/win")
        input("Press Enter to exit...")
        return
    
    # Initialize repository if needed
    if not os.path.exists(".git"):
        run_command("git init", "Initializing Git repository")
    
    # Add remote
    run_command("git remote remove origin", "")  # Remove existing remote if any
    run_command("git remote add origin https://github.com/tejukargal/DTE-Circulars.git", 
               "Adding GitHub remote")
    
    # Stage essential files
    essential_files = [
        "index.html",
        "deploy.md", 
        "_config.yml",
        "README.md"
    ]
    
    print("\n📁 Staging files...")
    for file in essential_files:
        if os.path.exists(file):
            run_command(f"git add {file}", f"Adding {file}")
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} not found")
    
    # Add Python files (optional)
    python_files = ["scraper.py", "gui_app.py", "web_app.py", "launcher.py"]
    for file in python_files:
        if os.path.exists(file):
            run_command(f"git add {file}", "")
    
    # Add other files
    run_command("git add requirements.txt", "")
    run_command("git add *.bat", "")
    
    # Create commit
    commit_message = """Deploy DTE Circulars web app to GitHub Pages

✨ Features:
- Live scraping of DTE Karnataka circulars  
- Mobile responsive design
- Cross-device compatibility
- Export to JSON functionality
- Direct PDF document links

🚀 Access at: https://tejukargal.github.io/DTE-Circulars/

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"""

    if not run_command(f'git commit -m "{commit_message}"', "Creating commit"):
        print("⚠️  Nothing to commit (files might already be up to date)")
    
    print("\n" + "=" * 60)
    print("   🔐 GitHub Authentication Required")
    print("=" * 60)
    print("\nThe next step requires your GitHub credentials:")
    print("• Username: tejukargal")
    print("• Password: Your GitHub password or Personal Access Token")
    print("\nIf you use 2FA, create a Personal Access Token:")
    print("• GitHub.com → Settings → Developer settings → Personal access tokens")
    print("• Generate token with 'repo' permissions")
    print("• Use token as password when prompted")
    
    input("\nPress Enter to continue with GitHub push...")
    
    # Push to GitHub
    if run_command("git push -u origin main", "Pushing to GitHub"):
        print("\n" + "=" * 60)
        print("   🎉 SUCCESS! Deployment Complete")
        print("=" * 60)
        print("\n✅ Files uploaded to GitHub successfully!")
        print("\n📋 Next Steps:")
        print("1. Go to: https://github.com/tejukargal/DTE-Circulars")
        print("2. Click 'Settings' tab")
        print("3. Scroll to 'Pages' section (left sidebar)")
        print("4. Under 'Source', select 'Deploy from a branch'")
        print("5. Choose 'main' branch and '/ (root)' folder")
        print("6. Click 'Save'")
        print("\n🌐 Your app will be live at:")
        print("   https://tejukargal.github.io/DTE-Circulars/")
        print("\n⏰ Deployment takes 2-3 minutes")
        
    else:
        print("\n❌ Push failed. Please check your credentials and try again.")
        print("\nCommon issues:")
        print("• Wrong username/password")
        print("• Need Personal Access Token for 2FA")
        print("• Network connectivity issues")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()