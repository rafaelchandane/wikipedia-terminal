# 📚 Wikipedia Terminal

**Access Wikipedia offline in your terminal with a retro Fallout-style interface.**

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## ✨ Features

- 🚀 **Blazing Fast** - Binary search through 19+ million articles
- 💾 **Completely Offline** - No internet required after setup
- 🎨 **Retro UI** - Fallout-inspired green terminal interface
- 📖 **Full Articles** - Read complete Wikipedia articles with pagination
- 🔍 **Smart Search** - Quick title-based search with optional FTS support
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux
- 🪶 **Lightweight** - No web server, direct ZIM file access

## 🎥 Demo

```
WIKIPEDIA TERMINAL
Type a query and press Enter. q to quit.

Query> python programming
Found 100 result(s). Enter number to open, or new query.

1. Python (programming language)
2. Python Software Foundation
3. Python for S60
...

Open # / new query / q > 1

Page 1/156 — n/p nav, b back, q quit
Python (programming language)

Python is a high-level, general-purpose programming language. Its design
philosophy emphasizes code readability with the use of significant
indentation...
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** (tested with Python 3.14)
2. **Wikipedia ZIM file** - Download from [Kiwix](https://wiki.kiwix.org/wiki/Content_in_all_languages)

### Installation

```bash
# Clone the repository
git clone https://github.com/rafaelchandane/wikipedia-terminal.git
cd wikipedia-terminal

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.wikipedia_tui.ui_curses --zim /path/to/wikipedia.zim
```

Or set the ZIM path permanently:

```bash
# Linux/macOS
export ZIM_PATH="/path/to/wikipedia_en_all_nopic_2025-08.zim"

# Windows (PowerShell)
$env:ZIM_PATH = "C:\path\to\wikipedia_en_all_nopic_2025-08.zim"

# Then run without arguments
python -m src.wikipedia_tui.ui_curses
```

## 📦 Recommended ZIM Files

Download from [https://download.kiwix.org/zim/wikipedia/](https://download.kiwix.org/zim/wikipedia/)

| Language | Size | Articles | Recommended |
|----------|------|----------|-------------|
| English (no pics) | ~50GB | 6.8M | ⭐ Best for most users |
| English (mini) | ~8GB | 100K | Good for testing |
| Spanish | ~4GB | 1.9M | Español |
| French | ~5GB | 2.5M | Français |

**Tip**: The "nopic" versions exclude images but include full text, saving significant space.

## 🎮 Usage

### Navigation

- **Search**: Type your query and press Enter
- **Select Article**: Type the article number (1, 2, 3...)
- **Next Page**: Press `n`
- **Previous Page**: Press `p`
- **Go Back**: Press `b` or Enter
- **Quit**: Press `q`

### Examples

```bash
# Search for Python
Query> python

# Open first result
Open # / new query / q > 1

# Navigate through pages
Page 1/156 — n/p nav, b back, q quit
> n  # Next page
> p  # Previous page
> b  # Back to search results

# New search
Query> quantum physics
```

## 🛠️ Configuration

### Environment Variables

- `ZIM_PATH` - Path to ZIM file
- `FTS_DB_PATH` - Path to FTS database (optional)
- `USE_SIMPLE_INPUT` - Set to `1` to force simple input mode

### Command Line Options

```bash
python -m src.wikipedia_tui.ui_curses --help

Options:
  --zim PATH    Path to ZIM file (overrides ZIM_PATH)
```

## 🏗️ Architecture

```
wikipedia-terminal/
├── src/
│   └── wikipedia_tui/
│       ├── __init__.py       # Package initialization
│       ├── ui_curses.py      # Terminal UI and main loop
│       ├── zim_access.py     # ZIM file reader
│       └── fts_index.py      # Full-text search (optional)
├── tests/                    # Unit tests (coming soon)
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
└── README.md
```

### How It Works

1. **ZIM Files**: Uses the [zimply](https://github.com/kimbauters/ZIMply) library to read compressed Wikipedia dumps
2. **Binary Search**: Efficiently searches through millions of articles using binary search on sorted index
3. **HTML Conversion**: Converts Wikipedia HTML to readable plain text
4. **Pagination**: Splits long articles into 20-line pages for comfortable reading

## 📊 Performance

- **Search Speed**: < 1 second for most queries
- **Memory Usage**: ~50-100MB (caches opened ZIM file)
- **Startup Time**: < 2 seconds (after first run)
- **Article Loading**: < 0.5 seconds

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and create virtual environment
git clone https://github.com/rafaelchandane/wikipedia-terminal.git
cd wikipedia-terminal
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (coming soon)
pytest
```

## 🗺️ Roadmap

See [GitHub Issues](https://github.com/rafaelchandane/wikipedia-terminal/issues) for planned features.

**v0.1.0** (Current)
- ✅ Basic search and article viewing
- ✅ Pagination support
- ✅ Cross-platform compatibility

**v0.2.0** (Planned)
- [ ] Full-text search (FTS5)
- [ ] Search history with arrow keys
- [ ] Bookmarks system
- [ ] Configuration file

**v1.0.0** (Future)
- [ ] Internal link following
- [ ] Multiple ZIM file support
- [ ] Better HTML rendering
- [ ] Export to Markdown/PDF

## 📝 FAQ

**Q: Where can I download ZIM files?**  
A: [https://wiki.kiwix.org/wiki/Content_in_all_languages](https://wiki.kiwix.org/wiki/Content_in_all_languages)

**Q: Why is search slow?**  
A: First search after opening a ZIM file is slower. Consider building an FTS index for faster searches.

**Q: Can I use multiple ZIM files?**  
A: Not yet, but it's planned for v1.0.0.

**Q: How much disk space do I need?**  
A: The English Wikipedia (no pics) is ~50GB. Mini version is ~8GB.

**Q: Does it work on Raspberry Pi?**  
A: Yes! Perfect for offline knowledge on low-power devices.

## 🙏 Acknowledgments

- [Kiwix](https://www.kiwix.org/) - For maintaining Wikipedia ZIM files
- [zimply](https://github.com/kimbauters/ZIMply) - Python ZIM file reader
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) - Terminal UI framework
- [Wikipedia](https://www.wikipedia.org/) - For free knowledge

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with 💚 by [Rafael Chandane](https://github.com/rafaelchandane)**

*Inspired by the Fallout terminal aesthetic and the desire for offline knowledge access.*
