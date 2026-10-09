# Kindroid CLI

A command-line interface utility for interacting with the Kindroid API.

## Features

- **Send Messages**: Send messages to chats via the `/send-message` endpoint
- **Get Chat Messages**: Retrieve messages from chats via the `/get-chat-messages` endpoint
- **JSON Output**: Pretty-printed JSON responses by default
- **Authentication**: Bearer token authentication via API key
- **Custom API URLs**: Support for custom API base URLs

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

Set your Kindroid API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:KINDROID_API_KEY = "your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set KINDROID_API_KEY=your_api_key_here
```

**Linux/macOS:**
```bash
export KINDROID_API_KEY="your_api_key_here"
```

## Usage

### Send a Message

Send a message to a chat:

```bash
python kindroid_cli.py send --chat-id <chat_id> "Your message here"
```

**Options:**
- `--chat-id`: Required. The ID of the chat to send the message to
- `--metadata`: Optional. JSON metadata to attach to the message (as a string)

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
- `--chat-id`: Required. The ID of the chat to retrieve messages from
- `--limit`: Optional. Maximum number of messages to retrieve
- `--offset`: Optional. Offset for pagination

**Example:**
```bash
python kindroid_cli.py get --chat-id abc123
python kindroid_cli.py get --chat-id abc123 --limit 10 --offset 0
```

### Global Options

- `--base-url`: Set a custom API base URL (default: `https://api.kindroid.ai`)
- `--no-pretty`: Disable pretty-printing of JSON responses

**Example:**
```bash
python kindroid_cli.py --base-url https://api.example.com send --chat-id abc123 "Message"
python kindroid_cli.py --no-pretty get --chat-id abc123
```

## Examples

### Full workflow example

```bash
# Set API key
$env:KINDROID_API_KEY = "your_api_key"

# Send a message
python kindroid_cli.py send --chat-id chat_001 "Hello!"

# Retrieve recent messages
python kindroid_cli.py get --chat-id chat_001 --limit 5

# Send another message with metadata
python kindroid_cli.py send --chat-id chat_001 --metadata '{"source":"cli"}' "Another message"
```

## Output

All responses are returned as JSON. By default, they are pretty-printed for readability.

### Example Response (Send Message)
```json
{
  "status": "success",
  "message_id": "msg_12345",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Example Response (Get Messages)
```json
{
  "status": "success",
  "chat_id": "chat_001",
  "messages": [
    {
      "id": "msg_1",
      "content": "Hello",
      "timestamp": "2024-01-15T10:00:00Z",
      "author": "user"
    },
    {
      "id": "msg_2",
      "content": "Hi there!",
      "timestamp": "2024-01-15T10:05:00Z",
      "author": "assistant"
    }
  ],
  "total": 2
}
```

## Error Handling

The CLI provides clear error messages for common issues:

- **Missing API Key**: Reminds you to set `KINDROID_API_KEY`
- **Invalid JSON Metadata**: Reports JSON parsing errors
- **API Errors**: Displays HTTP errors from the Kindroid API

## Environment Variables

- `KINDROID_API_KEY`: Your Kindroid API key (required)

## Help

View help at any time:

```bash
python kindroid_cli.py --help
python kindroid_cli.py send --help
python kindroid_cli.py get --help
```

## API Documentation

For more information about the Kindroid API, refer to the official documentation:
- https://docs.kindroid.ai/

## License

This CLI utility is provided as-is for use with the Kindroid API.

# kindroid
