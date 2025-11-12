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
- ⚡ **Multiple Modes** - Interactive UI, quick search, direct article access
- 🛠️ **CLI Integration** - Use `wiki` command anywhere in your terminal
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux
- 🪶 **Lightweight** - No web server, direct ZIM file access
- 📦 **Pipe-Friendly** - Pipe output to other command-line tools
- 📊 **Progress Tracking** - Visual progress bars with ETA for index building
- 🔙 **History Navigation** - Browse articles with back/forward like a web browser

## 🎥 Demo

### Interactive Mode
```
$ wiki

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

### Quick Modes
```bash
# Quick search - list results
$ wiki search python
Found 100 result(s) for 'python':

  1. Python (programming language)
  2. Python Software Foundation
  3. Monty Python
  ...

# Quick read - instant article
$ wiki quick python
================================================================================
PYTHON (PROGRAMMING LANGUAGE)
================================================================================

Python is a high-level, general-purpose programming language...

# Search and select workflow (NEW!)
$ wiki search "World War 2"
Found 6 result(s) for 'World War 2':

  1. World war 2
  2. World war 2 artillery
  3. World war 2 by country
  4. World war 2 deaths
  5. World war 2 memorial
  6. World war 2 online

Tip: Use 'wiki read <number>' to open an article from this list

$ wiki read 1
================================================================================
WORLD WAR 2
================================================================================

World War II or the Second World War (1 September 1939 – 2 September 1945)...

# Or use the short alias
$ wiki r 3
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

# Install as a command-line tool (recommended)
pip install -e .

# Now you can use 'wiki' from anywhere!
wiki
```

Or run directly without installing:

```bash
python -m src.wikipedia_tui.ui_curses --zim /path/to/wikipedia.zim
```

Or set the ZIM path permanently:

```bash
# Linux/macOS
export ZIM_PATH="/path/to/wikipedia_en_all_nopic_2025-08.zim"

# Windows (PowerShell)
$env:ZIM_PATH = "C:\path\to\wikipedia_en_all_nopic_2025-08.zim"

# Then run without arguments
wiki
```

## 🎮 Usage

Wikipedia Terminal supports multiple modes for different workflows:

### Interactive Mode (Default)

Launch the full terminal UI:

```bash
# Start interactive mode
wiki

# Or explicitly
wiki interactive
```

### Quick Search Mode

Search and display results without entering the UI:

```bash
# Search for articles
wiki search python programming

# Limit number of results
wiki search --limit 10 quantum physics

# Short alias
wiki s linux
```

### Read from Search Results (NEW!)

After searching, read articles by their number:

```bash
# First, search for something
wiki search "World War 2"
# Shows numbered list (1-6)

# Then read any article by number
wiki read 1    # Opens "World war 2"
wiki read 3    # Opens "World war 2 by country"

# Short alias
wiki r 2
```

**Tip:** The search results are cached, so you can run multiple `wiki read` commands without searching again!

### Quick Read Mode

Get the first matching article instantly:

```bash
# Quick lookup - displays first match
wiki quick python

# Short alias
wiki q "machine learning"
```

### Direct Article Access

Get a specific article by exact title:

```bash
# Get exact article
wiki get "Python (programming language)"

# Short alias
wiki g "Albert Einstein"
```

### Build Search Index

Create an FTS5 index for faster full-text search:

```bash
# Build index from ZIM file
wiki build-index /path/to/wikipedia.zim -o wiki_index.db

# With custom batch size and replace existing
wiki build-index wikipedia.zim --batch 1000 --replace
```

### Navigation (Interactive Mode)

**While Searching:**
- **Search**: Type your query and press Enter
- **Select Article**: Type the article number (1, 2, 3...)

**While Reading Articles:**
- **Next Page**: Press `n`
- **Previous Page**: Press `p`
- **Back to Previous Article**: Press `b`, `back`, or `<` (NEW! ⭐)
- **Forward to Next Article**: Press `f`, `forward`, or `>` (NEW! ⭐)
- **Return to Search**: Press Enter
- **Quit**: Press `q`

**History Navigation** - Browse articles like a web browser! The app remembers every article you view, so you can easily navigate back and forward through your reading history.

### Examples

```bash
# Interactive mode (full UI)
wiki

# Quick search while coding
wiki search "binary tree" --limit 5

# Search and read workflow (NEW!)
wiki search Sweden        # Get numbered list
wiki read 11             # Open "Sweden (disambiguation)"

# Get quick info without leaving terminal
wiki quick "quicksort algorithm"

# Read specific article
wiki get "Merge sort"

# Build search index for faster lookups
wiki build-index ~/Downloads/wikipedia.zim

# Pipe to other commands
wiki quick python | less
wiki get "Linux" > linux_article.txt
```

## 🛠️ Configuration

### Environment Variables

- `ZIM_PATH` - Path to ZIM file
- `FTS_DB_PATH` - Path to FTS database (optional)
- `USE_SIMPLE_INPUT` - Set to `1` to force simple input mode

### Command Line Options

```bash
# Get help
wiki --help

# Get help for specific command
wiki search --help
wiki build-index --help

# Specify ZIM file (overrides ZIM_PATH)
wiki --zim /path/to/file.zim search python
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

### Project Cleanup

```bash
# Debug logs and index databases are automatically git-ignored
# They're created during development but won't be committed
# To clean them manually:
rm *.log *.db *.db-shm *.db-wal
rm src/wikipedia_tui/*.log
```

## 🗺️ Roadmap

See [GitHub Issues](https://github.com/rafaelchandane/wikipedia-terminal/issues) for planned features and to vote on priorities.

**v0.1.0** (Current - Released)
- ✅ Basic search and article viewing
- ✅ Pagination support
- ✅ Cross-platform compatibility
- ✅ Binary search through ZIM files
- ✅ HTML to plain text conversion
- ✅ Multiple CLI modes (interactive, search, quick, get)
- ✅ Command-line integration with `wiki` command

**v0.1.1** (Quick Win - In Progress)
- [ ] Complete FTS5 full-text search implementation
- ✅ Progress bars and ETA for index building
- [ ] Resume support for interrupted index builds

**v0.2.0** (Foundation - In Progress)
- ✅ Navigation history (back/forward through articles)
- [ ] Better HTML rendering (tables, lists, formatting)
- [ ] Image alt-text display
- [ ] Search history persistence
- [ ] Configuration file support (`~/.wikipedia_tui/config.yaml`)
- [ ] Improved text wrapping and formatting

**v0.3.0** (Enhanced UX)
- [ ] Internal link following with numbered references
- [ ] Bookmarks system
- [ ] Random article feature
- [ ] Search within current article

**v1.0.0** (Major Features)
- [ ] Multiple ZIM file support
- [ ] Advanced search filters (by category, date, etc.)
- [ ] Enhanced terminal UI (colors, borders, status bar)
- [ ] Table of contents navigation
- [ ] Article categories and metadata display

**v2.0.0** (Future Ideas)
- [ ] Export articles to Markdown/PDF
- [ ] Plugin system for extensions
- [ ] Optional image viewing support
- [ ] Collaborative annotations
- [ ] Offline article updates/syncing

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
