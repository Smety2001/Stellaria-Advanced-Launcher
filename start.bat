@echo off
cd "%~dp0"
curl -f -o main.py https://raw.githubusercontent.com/Smety2001/Stellaria-Advanced-Launcher/main/main.py
pip install -r https://raw.githubusercontent.com/Smety2001/Stellaria-Advanced-Launcher/main/requirements.txt
start /MIN pythonw main.py