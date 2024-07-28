# # Use this script to build the project
# $folderName = Split-Path -Leaf (Get-Location)
# pyinstaller -F main.py --onefile -n $folderName

# # Move and Rename
# Move-Item -Path ./configs -Destination ./dist/
# Move-Item -Path ./src -Destination ./dist/
# Move-Item -Path ./data -Destination ./dist/
# Move-Item -Path ./binaries -Destination ./dist/

# Copy and Rename
Copy-Item -Path ./configs -Destination ./dist/ -Recurse
Copy-Item -Path ./src -Destination ./dist/ -Recurse
Copy-Item -Path ./data -Destination ./dist/ -Recurse
Copy-Item -Path ./binaries -Destination ./dist/ -Recurse
