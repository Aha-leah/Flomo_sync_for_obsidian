# Flomo Sync for Obsidian
> by Aha-leah

A simple but powerful Obsidian plugin to sync your **Flomo (浮墨)** memos into your Obsidian vault automatically.

> **Note**: This tool uses a Python script with Playwright to simulate a browser login, ensuring stability even without an official API key.

## Requirements & Compatibility

- **Python**: Version **3.8** or higher is required.
- **Obsidian**: Version **0.15.0** or higher.
- **Playwright**: Version **1.40.0** or higher is recommended.
- **Operating System**:
  - **macOS**: macOS 13 (Ventura) or later recommended.
  - **Windows**: Windows 10/11 or WSL.
  - **Linux**: Ubuntu 20.04+ or equivalent.

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
# Install dependencies (Playwright >= 1.40.0 recommended)
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

## FAQ

### 1. Why do I need to install Python?
Obsidian's internal environment cannot run complex browser automation tools like Playwright. We use a local Python script to handle the secure login and data fetching from Flomo, which is safer and more reliable than pure JavaScript solutions for this use case.

### 2. Is my data safe?
Yes. The script runs entirely on your local machine.
- Your credentials (if saved) are stored locally in `flomo_sync.py` or your system.
- Your session cookies are stored in `flomo_state.json` locally.
- Data flows directly from Flomo to your local Obsidian vault. No third-party servers are involved.

### 3. I get a "Playwright not found" or browser error.
Make sure you have installed the browser binaries:
```bash
pip3 install playwright
playwright install chromium
```
Also, ensure the "Python Path" in the plugin settings points to the same Python environment where you installed these packages.

### 4. Can I sync to a specific folder in Obsidian?
Yes. By default, it syncs to a `Flomo` folder in your vault root.
You can change the `--output-dir` argument in the `main.js` file if you are comfortable editing code, or in the future versions we may add a setting for this.

### 5. My login session keeps expiring.
Flomo's cookies may expire after a while. If sync fails:
1. Delete `flomo_state.json` in the plugin folder.
2. Run sync again to trigger a new QR code scan or auto-login.

## Structure
- `main.js`: The Obsidian plugin frontend.
- `flomo_sync.py`: The Python backend that handles the crawling and file generation.

## ⚠️ Risks & Disclaimers

### 1. Account Security
- **Credentials**: The script supports hardcoding your password in `flomo_sync.py` for auto-login. **DO NOT** commit this file to GitHub if you have entered your password. We strongly recommend using the **QR Code Login** method, which only saves a session cookie locally.
- **Session Cookies**: Your login session is stored in `flomo_state.json`. Keep this file safe and do not share it.

### 2. Data Privacy
- **Local Execution**: All data runs locally on your machine. No data is sent to any third-party servers.
- **Image Links**: The script saves the *URL* of images, not the image files themselves. If Flomo changes their image hosting or requires strict authentication for image viewing, images might not load in Obsidian.

### 3. Platform Compliance
- This tool uses an automated browser (Playwright) to access your own data. While this is generally considered acceptable for personal backup, excessive usage might trigger Flomo's anti-bot protection. The script mimics a real user to minimize this risk.

### 4. Open Source Safety
- The `.gitignore` file is configured to exclude sensitive files like `flomo_state.json` and logs. **Double-check** before you push to GitHub that you haven't accidentally modified the ignore rules.

## License
MIT
