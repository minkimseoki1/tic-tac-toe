@echo off
cd /d "%~dp0"
python main.py >> "%~dp0logs\newsletter.log" 2>&1
