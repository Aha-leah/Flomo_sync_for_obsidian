# Aha-leah (Flomo Sync for Obsidian)

A simple but powerful Obsidian plugin to sync your **Flomo (浮墨)** memos into your Obsidian vault automatically.

> **Note**: This tool uses a Python script with Playwright to simulate a browser login, ensuring stability even without an official API key.

## Features

- 🚀 **One-click Sync**: Trigger sync from the ribbon icon or command palette.
- 🍪 **Auto Login**: Supports scanning QR code once, and then auto-logins via cookies.
- 🖼 **Image Support**: Syncs memos with images (saves image links).
- 🏷 **Tag Support**: Automatically extracts tags from Flomo content.
- 📂 **Auto Organization**: Saves memos into date-based folders (e.g., `Flomo/2023-10-27`).
- 🚫 **Duplication Check**: Intelligent content checking to prevent duplicate imports.

## Installation

### 1. Install the Plugin
1. Create a folder named `flomo-sync-launcher` in your Obsidian vault's plugin directory: `.obsidian/plugins/flomo-sync-launcher`.
2. Copy `main.js`, `manifest.json`, and `flomo_sync.py` into that folder.
3. Enable the plugin in Obsidian settings.

### 2. Setup Python Environment
This plugin requires Python 3 and Playwright.

```bash
# Install dependencies
pip3 install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Configure the Plugin
1. Open Obsidian Settings -> **Flomo Sync Launcher**.
2. **Python Path**: Enter the absolute path to your Python executable.
   - Run `which python3` in your terminal to find it (e.g., `/usr/bin/python3` or `/opt/homebrew/bin/python3`).
3. **Default Tag** (Optional): A tag to append to all synced memos (e.g., `#flomo`).

### 4. Configure Flomo Account (Optional but Recommended)
For fully automated background sync (no QR code scanning required every time), edit `flomo_sync.py`:

```python
# Open flomo_sync.py and edit these lines at the top:
FLOMO_ACCOUNT = "your_phone_or_email"
FLOMO_PASSWORD = "your_password"
```

If you leave these blank, the script will pop up a browser window for you to scan the QR code manually upon first run. It will then save your login session (cookies) for future runs.

## Usage

1. Click the **Refresh Icon** in the left ribbon bar.
2. Or use `Cmd/Ctrl + P` and search for **"Sync Flomo Now"**.
3. Watch the notifications! 
   - First run might take a moment to launch the browser.
   - Subsequent runs will be faster.

## Structure
- `main.js`: The Obsidian plugin frontend.
- `flomo_sync.py`: The Python backend that handles the crawling and file generation.

## License
MIT
