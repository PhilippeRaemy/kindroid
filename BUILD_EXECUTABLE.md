# Building a Windows Executable

This guide explains how to compile `kindroid_cli.py` into a self-contained Windows executable.

## Prerequisites

Make sure you have PyInstaller installed:

```bash
pip install pyinstaller
```

Or install all development dependencies:

```bash
pip install -r requirements.txt
```

## Building the Executable

### Option 1: Simple One-File Executable (Recommended)

Run this command from the project directory:

```bash
pyinstaller --onefile --name kindroid kindroid_cli.py
```

This creates a single executable file at:
```
dist\kindroid.exe
```

### Option 2: With Console Window Hidden

If you want to hide the console window (useful for GUI wrappers):

```bash
pyinstaller --onefile --windowed --name kindroid kindroid_cli.py
```

⚠️ **Note:** For a CLI tool, you probably want the console visible, so use Option 1.

### Option 3: With Icon (Windows Only)

Add a custom icon to your executable:

```bash
pyinstaller --onefile --name kindroid --icon=icon.ico kindroid_cli.py
```

(Replace `icon.ico` with your icon file path)

## What Gets Created

After running the PyInstaller command, you'll get:

```
kindroid/
├── build/           (temporary build files - can delete)
├── dist/
│   └── kindroid.exe (your executable!)
└── kindroid.spec    (PyInstaller configuration - keep for rebuilds)
```

## Using the Executable

The `kindroid.exe` executable works exactly like the Python script:

```bash
# Show help
kindroid.exe --help

# Send a message
kindroid.exe send --chat-id abc123 "Hello world"

# Get messages to console
kindroid.exe get --chat-id abc123 --limit 50

# Get messages to file
kindroid.exe get --chat-id abc123 --limit 200 --output-file messages.jsonl

# Interactive chat
kindroid.exe chat --chat-id abc123
```

## Environment Variables

The executable still uses environment variables:

```bash
# Set API key
$env:KINDROID_API_KEY = 'kn_your_api_key'

# Set default chat ID (optional)
$env:CHAT_ID = 'your_chat_id'

# Run the executable
kindroid.exe send --chat-id abc123 "Hello"
```

## Distributing the Executable

To share `kindroid.exe` with others:

1. Only distribute the `dist\kindroid.exe` file
2. Users don't need Python installed on their machine
3. The executable is ~50-100 MB (includes Python runtime and dependencies)

## Troubleshooting

### Antivirus Warnings

PyInstaller executables sometimes trigger antivirus warnings because they bundle a Python interpreter. This is normal and safe. To minimize warnings:
- Build on Windows (not in WSL)
- Keep PyInstaller updated: `pip install --upgrade pyinstaller`

### Missing Dependencies

If the executable fails at runtime with import errors:

```bash
# Rebuild with explicit hidden imports
pyinstaller --onefile --hidden-import=requests --name kindroid kindroid_cli.py
```

### Reducing File Size

To create a smaller executable:

```bash
pyinstaller --onefile --noupx --name kindroid kindroid_cli.py
```

## Rebuilding

If you update the code, just run the PyInstaller command again. PyInstaller will use the `.spec` file for consistency:

```bash
pyinstaller kindroid.spec
```

## Advanced Configuration

For more control, create a `kindroid.spec` file manually and customize it. See:
```bash
pyi-makespec --help
```

Or visit: https://pyinstaller.org/en/stable/usage.html

