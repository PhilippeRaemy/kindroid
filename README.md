# Kindroid CLI

A command-line interface utility for interacting with the Kindroid API.

## Features

- **Send Messages**: Send messages to chats and get responses
- **Interactive Chat**: Real-time conversation mode with automatic response handling
- **Get Chat Messages**: Retrieve messages from chats with automatic pagination
- **JSONL Output**: Messages output as JSON Lines format for easy parsing
- **File Output**: Save messages to a file and automatically resume from the last message
- **Timestamp Conversion**: Unix timestamps automatically converted to ISO 8601 format
- **Authentication**: Bearer token authentication via API key
- **Custom API URLs**: Support for custom API base URLs
- **Environment Variable Fallback**: Support for chat ID via environment variable

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

Set your Kindroid API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:KINDROID_API_KEY = "kn_your_api_key_here"
$env:CHAT_ID = "your_chat_id_here"  # Optional
```

**Windows (Command Prompt):**
```cmd
set KINDROID_API_KEY=kn_your_api_key_here
set CHAT_ID=your_chat_id_here
```

**Linux/macOS:**
```bash
export KINDROID_API_KEY="kn_your_api_key_here"
export CHAT_ID="your_chat_id_here"  # Optional
```

## Usage

### Interactive Chat

Start an interactive chat session:

```bash
python kindroid_cli.py chat --chat-id <chat_id>
```

**Options:**
- `--chat-id`: Optional if `CHAT_ID` environment variable is set

**Example:**
```bash
python kindroid_cli.py chat --chat-id abc123
# Then type messages and receive responses
```

**Exit:** Press `Ctrl+C` or `Ctrl+Z` to exit the chat

### Send a Message

Send a message to a chat:

```bash
python kindroid_cli.py send --chat-id <chat_id> "Your message here"
```

**Options:**
- `--chat-id`: Optional if `CHAT_ID` environment variable is set
- `--metadata`: Optional JSON metadata to attach to the message

**Example:**
```bash
python kindroid_cli.py send --chat-id abc123 "Hello, world!"
python kindroid_cli.py send --chat-id abc123 --metadata '{"user":"john","priority":"high"}' "Important message"
```

### Get Chat Messages

Retrieve messages from a chat:

```bash
python kindroid_cli.py get --chat-id <chat_id> [options]
```

**Options:**
- `--chat-id`: Optional if `CHAT_ID` environment variable is set
- `--limit`: Maximum number of messages to retrieve (auto-paginates if > 100)
- `--offset`: Start position for pagination
- `--output-file`: Save messages to JSONL file (automatically resumes from last message)

**Examples:**
```bash
# Print to console
python kindroid_cli.py get --chat-id abc123 --limit 10

# Save to file (incremental updates)
python kindroid_cli.py get --chat-id abc123 --limit 200 --output-file messages.jsonl

# Get many messages (auto-paginated)
python kindroid_cli.py get --chat-id abc123 --limit 500
```

**Output Format:** Each message is one JSON object per line (JSONL):
```jsonl
{"id":"msg1","sender":"user","timestamp":"2026-10-09T14:30:45.123456","message":"Hello"}
{"id":"msg2","sender":"ai","timestamp":"2026-10-09T14:30:46.654321","message":"Hi there!"}
```

### Global Options

- `--base-url`: Set a custom API base URL (default: `https://api.kindroid.ai/v1`)
- `--no-pretty`: Disable pretty-printing of JSON responses (for send command)

**Example:**
```bash
python kindroid_cli.py --base-url https://api.example.com send --chat-id abc123 "Message"
```

## Building a Windows Executable

To create a self-contained Windows executable that doesn't require Python:

### Option 1: PowerShell Script (Recommended)
```powershell
.\build.ps1
```

### Option 2: Batch Script
```cmd
build.bat
```

### Option 3: Manual Build
```bash
pyinstaller --onefile --name kindroid kindroid_cli.py
```

The executable will be created at `dist\kindroid.exe`

**Using the executable:**
```cmd
dist\kindroid.exe send --chat-id abc123 "Hello"
dist\kindroid.exe get --chat-id abc123 --limit 50 --output-file messages.jsonl
dist\kindroid.exe chat --chat-id abc123
```

See [BUILD_EXECUTABLE.md](BUILD_EXECUTABLE.md) for detailed build instructions.

## Environment Variables

- `KINDROID_API_KEY`: Your Kindroid API key (required)
- `CHAT_ID`: Default chat ID (optional, can be overridden with `--chat-id`)

## Examples

### Full workflow example

```bash
# Set API key
$env:KINDROID_API_KEY = "kn_your_api_key"

# Interactive chat
python kindroid_cli.py chat --chat-id chat_001

# Send a message
python kindroid_cli.py send --chat-id chat_001 "Hello!"

# Retrieve messages to file
python kindroid_cli.py get --chat-id chat_001 --limit 100 --output-file chat_history.jsonl

# Retrieve more recent messages (continues from last)
python kindroid_cli.py get --chat-id chat_001 --limit 50 --output-file chat_history.jsonl
```

## API Documentation

For detailed API endpoint documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

For more information about the Kindroid API:
- https://kindroid.ai/

## Help

View help at any time:

```bash
python kindroid_cli.py --help
python kindroid_cli.py chat --help
python kindroid_cli.py send --help
python kindroid_cli.py get --help
```

## License

This CLI utility is provided as-is for use with the Kindroid API.

