@REM CALL conda activate automa
rye sync
.\binaries\adb.exe connect 16416
rye run python main.py
pause
