@echo off
rem IP Packet Monitor run file
rem Change PYTHON path if needed (ex: C:\py27test\python.exe)
set PYTHON=C:\anaconda2\python.exe

cd /d "%~dp0"
"%PYTHON%" main.py
if errorlevel 1 pause
