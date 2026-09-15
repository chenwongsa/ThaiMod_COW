@echo off
REM Build ThaiMod Installer v1.1 with PyInstaller (onedir mode)
cd /d "%~dp0"
echo === Cleaning previous build ===
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo === PyInstaller build ===
pyinstaller ^
  --onedir --windowed ^
  --name "ThaiMod_Installer_WildHorizonGaming" ^
  --icon "icon\app_icon.ico" ^
  --add-data "moddata;moddata" ^
  --noconfirm ^
  patcher_gui.py

if errorlevel 1 (
  echo BUILD FAILED
  exit /b 1
)

echo.
echo === Build output ===
dir /b dist\ThaiMod_Installer_WildHorizonGaming\ | findstr /R "exe"

echo.
echo BUILD OK. Next: zip dist\ThaiMod_Installer_WildHorizonGaming\ into release zip.
