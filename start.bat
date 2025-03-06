@echo off
:: 設置命令行編碼為 UTF-8
chcp 65001
setlocal enabledelayedexpansion

uv sync --no-dev
@REM rye run main
start powershell -NoExit -Command "uv run python main.py"
