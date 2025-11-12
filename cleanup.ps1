# Cleanup script for wikipedia-terminal
# Removes debug logs, test databases, and temporary files

Write-Host "Cleaning up wikipedia-terminal workspace..." -ForegroundColor Cyan

# Debug logs
$logFiles = @(
    "*.log",
    "src/wikipedia_tui/*.log"
)

# Database files
$dbFiles = @(
    "*.db",
    "*.db-shm",
    "*.db-wal"
)

# Python cache
$cacheFiles = @(
    "**/__pycache__",
    "**/*.pyc",
    "**/*.pyo"
)

$cleaned = 0

# Remove logs
foreach ($pattern in $logFiles) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($files) {
        Remove-Item -Path $files -Force
        $cleaned += $files.Count
        Write-Host "  Removed $($files.Count) log file(s)" -ForegroundColor Green
    }
}

# Remove databases (excluding any production DBs you want to keep)
foreach ($pattern in $dbFiles) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($files) {
        Remove-Item -Path $files -Force
        $cleaned += $files.Count
        Write-Host "  Removed $($files.Count) database file(s)" -ForegroundColor Green
    }
}

# Remove Python cache
Get-ChildItem -Path . -Recurse -Include "__pycache__", "*.pyc", "*.pyo" -ErrorAction SilentlyContinue | 
    ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force
        $cleaned++
    }
Write-Host "  Removed Python cache files" -ForegroundColor Green

Write-Host ""
Write-Host "Cleanup complete! Removed $cleaned item(s)" -ForegroundColor Cyan
Write-Host "Note: These files are git-ignored" -ForegroundColor Gray
