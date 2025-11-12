# Quick Start Guide

## Installation

```powershell
# 1. Install the package
pip install -e .

# 2. Create local configuration (RECOMMENDED - won't be pushed to GitHub)
# Copy the example file:
copy local_config.example.ps1 local_config.ps1

# Edit local_config.ps1 with your paths, then load it:
. .\local_config.ps1

# OR manually set for current session:
$env:ZIM_PATH = "C:\path\to\your\wikipedia.zim"
$env:PATH += ";C:\Users\joelt\AppData\Roaming\Python\Python314\Scripts"

# OR permanently add to system PATH:
# Windows Settings → System → About → Advanced system settings → Environment Variables
# Add: C:\Users\joelt\AppData\Roaming\Python\Python314\Scripts
```

## Usage Examples

### Quick Tests (without ZIM file)

```powershell
# See help
wiki --help

# See search command help
wiki search --help
```

### With ZIM File

```powershell
# Set ZIM path (if not in local_config.ps1)
$env:ZIM_PATH = "C:\Vibe Code\Wikipedia ZIM\wikipedia_en_all_nopic_2025-08.zim"

# Search and read workflow (recommended!)
wiki search python
wiki read 1              # Opens first result
wiki r 2                 # Short alias

# Quick search
wiki search "World War 2"

# Quick read
wiki quick "python programming"

# Get specific article
wiki get "Python (programming language)"

# Interactive mode
wiki
```

## Troubleshooting

### "wiki is not recognized"

Add Scripts directory to PATH:
```powershell
$env:PATH += ";C:\Users\joelt\AppData\Roaming\Python\Python314\Scripts"
```

### "No ZIM file found"

Either:
1. Set environment variable: `$env:ZIM_PATH = "path\to\file.zim"`
2. Use --zim flag: `wiki --zim "path\to\file.zim" search python`

### Import warnings

The zimply library warning is harmless and can be ignored.

## Permanent Setup

Add to your PowerShell profile (`$PROFILE`):

```powershell
# Add to PATH
$env:PATH += ";C:\Users\joelt\AppData\Roaming\Python\Python314\Scripts"

# Set ZIM path
$env:ZIM_PATH = "C:\path\to\your\wikipedia.zim"
```

Then reload: `. $PROFILE`
