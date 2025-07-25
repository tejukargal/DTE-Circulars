@echo off
echo ================================================
echo   DTE Circulars - GitHub Pages Deployment
echo ================================================
echo.

echo Checking if git is installed...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH.
    echo Please install Git from: https://git-scm.com/download/win
    echo Then run this script again.
    pause
    exit /b 1
)

echo Git is installed ✓
echo.

echo Setting up local repository...
if exist ".git" (
    echo Repository already initialized ✓
) else (
    git init
    echo Repository initialized ✓
)

echo.
echo Adding remote repository...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/tejukargal/DTE-Circulars.git
echo Remote added ✓

echo.
echo Adding files to staging...
git add index.html
git add deploy.md
git add _config.yml
git add README.md
git add *.py
git add *.bat
git add requirements.txt
git add templates/
echo Files staged ✓

echo.
echo Creating commit...
git commit -m "Deploy DTE Circulars web app to GitHub Pages

✨ Features:
- Live scraping of DTE Karnataka circulars
- Mobile responsive design
- Cross-device compatibility
- Export to JSON functionality
- Direct PDF document links

🚀 Access at: https://tejukargal.github.io/DTE-Circulars/"

echo Commit created ✓

echo.
echo ================================================
echo   IMPORTANT: GitHub Authentication Required
echo ================================================
echo.
echo The next step will push to GitHub and may require:
echo 1. Your GitHub username: tejukargal
echo 2. Your GitHub password OR personal access token
echo.
echo If you use 2FA, you'll need a Personal Access Token:
echo - Go to GitHub.com → Settings → Developer settings
echo - Generate new token with 'repo' permissions
echo - Use token as password when prompted
echo.
echo Press any key to continue with push...
pause >nul

echo.
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Push failed. This might be due to:
    echo 1. Authentication issues
    echo 2. Network connectivity
    echo 3. Repository permissions
    echo.
    echo Please check your credentials and try again.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   🎉 SUCCESS! Files uploaded to GitHub
echo ================================================
echo.
echo Next steps:
echo 1. Go to: https://github.com/tejukargal/DTE-Circulars
echo 2. Click Settings tab
echo 3. Scroll to Pages section
echo 4. Select "Deploy from a branch"
echo 5. Choose "main" branch and "/ (root)"
echo 6. Click Save
echo.
echo Your app will be live at:
echo https://tejukargal.github.io/DTE-Circulars/
echo.
echo (Takes 2-3 minutes to deploy)
echo.
pause