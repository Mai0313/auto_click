@echo off
:: 設置命令行編碼為 UTF-8
chcp 65001
setlocal enabledelayedexpansion

set /p port="Enter the port number (default is 8000): "
if "%port%"=="" (
    set port=16416
)

@REM rye run main
start powershell -NoExit -Command "uv run python main.py --port=%port%"
