# Wasserstein Distance Visualizer

## 🚨 CORS Issue Fix

The "Failed to fetch" error occurs because browsers block local file access for security reasons. Here are **3 solutions**:

## Solution 1: Use Python Server (Recommended)

```bash
# Run the included server script
python3 start_server.py
```

This will:
- Start a local web server on port 8000
- Automatically open the visualizer in your browser
- Serve files properly without CORS issues

## Solution 2: Use Simple HTTP Server

```bash
# Navigate to your project directory
cd /path/to/your/project

# Start Python's built-in server
python3 -m http.server 8000

# Then open in browser:
# http://localhost:8000/wasserstein_visualizer_fixed.html
```

## Solution 3: Use Browser Flags (Chrome/Edge)

**macOS:**
```bash
open -a "Google Chrome" --args --disable-web-security --user-data-dir="/tmp/chrome_dev"
```

**Windows:**
```cmd
chrome.exe --disable-web-security --user-data-dir="c:\temp\chrome_dev"
```

Then open the HTML file directly.

## Files Available

1. **`wasserstein_visualizer_fixed.html`** - Main visualizer (needs server)
2. **`test_wasserstein.html`** - Simple debug version
3. **`start_server.py`** - Easy server launcher

## Features

- **Interactive slider** to filter distance thresholds
- **Real-time statistics** showing filtered pairs
- **Distance histogram** with distribution analysis
- **Searchable motif pairs** list
- **Detailed statistics** panel

## Quick Start

1. Run: `python3 start_server.py`
2. Browser opens automatically
3. Use slider to explore different distance thresholds
4. Search for specific motifs
5. Click on pairs to select them

## Troubleshooting

- **Port 8000 busy?** Edit `start_server.py` and change `PORT = 8000` to another number
- **Python not found?** Try `python` instead of `python3`
- **Still not working?** Use the browser flags method above