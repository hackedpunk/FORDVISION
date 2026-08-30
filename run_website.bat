@echo off
title FORDVISION Local Server
echo Starting local server for FordVision...
start http://localhost:8000
python -m http.server 8000
pause