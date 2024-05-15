@REM CALL conda activate automa
CALL .\binaries\adb.exe connect 127.0.0.1:16416
CALL rye sync
CALL rye run python main.py
pause
