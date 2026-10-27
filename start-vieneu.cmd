@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
set HF_HOME=%~dp0models\hf-cache
set HF_HUB_DISABLE_SYMLINKS=1
set GRADIO_ANALYTICS_ENABLED=False
set GRADIO_SERVER_NAME=127.0.0.1
set GRADIO_SERVER_PORT=7862
set GRADIO_SHARE=False
"%~dp0.venv\Scripts\vieneu-web.exe"
pause
