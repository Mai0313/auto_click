@echo off
:: 設置命令行編碼為 UTF-8
chcp 65001
setlocal enabledelayedexpansion

@REM set /p port="Enter the port number (default is 8000): "
@REM if "%port%"=="" (
@REM     set port=16416
@REM )

@REM rye run main
@REM start powershell -NoExit -Command "uv run python main.py --port=%port%"
start powershell -NoExit -Command "uv run python main.py --port=16416"
start powershell -NoExit -Command "uv run python main.py --port=16448"
