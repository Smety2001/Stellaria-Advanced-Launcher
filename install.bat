:: Download and install the latest version of Python
echo Installing Python...
curl -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install required libraries
echo Installing required libraries...
pip install -r https://raw.githubusercontent.com/Smety2001/Stellaria-Advanced-Launcher/main/requirements.txt

:: Clean up
del python-installer.exe
echo Installation and script execution complete.
pause