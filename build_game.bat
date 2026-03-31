@echo off
echo ===================================================
echo Building the game executable using PyInstaller...
echo This might take a few minutes. Please wait...
echo ===================================================

.\.venv\Scripts\pyinstaller.exe ^
  --noconfirm ^
  --onedir ^
  --windowed ^
  main.py

echo.
echo Copying game assets to the build folder...
xcopy assets dist\main\assets /E /H /C /I /Y

echo.
echo ===================================================
echo Build complete! 
echo Check the "dist\main" folder for your game executable.
echo ===================================================
pause
