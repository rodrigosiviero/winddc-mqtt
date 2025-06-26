@echo off
cd /d C:\Users\rodri\winddc-mqtt
call .venv\Scripts\activate.bat
python start.py > winddc.log 2>&1 