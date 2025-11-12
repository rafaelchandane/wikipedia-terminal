# Local Configuration Example
# Copy this file to local_config.ps1 and customize for your system
# local_config.ps1 is git-ignored and won't be pushed to GitHub

# Set your ZIM file path
$env:ZIM_PATH = "C:\Vibe Code\Wikipedia ZIM\wikipedia_en_all_nopic_2025-08.zim"

# Add Python Scripts to PATH (if needed)
$env:PATH += ";C:\Users\joelt\AppData\Roaming\Python\Python314\Scripts"

Write-Host "✓ Local config loaded" -ForegroundColor Green
Write-Host "  ZIM_PATH: $env:ZIM_PATH" -ForegroundColor Cyan
