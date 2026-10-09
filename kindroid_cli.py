#!/usr/bin/env python3
"""
Kindroid CLI - A command-line interface for interacting with the Kindroid API.

This utility provides commands to interact with the Kindroid API endpoints:
- /send-message: Send a message to a chat
- /get-chat-messages: Retrieve chat messages

Documentation: https://docs.kindroid.ai/
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests

# Windows-specific: support for multi-line input with Shift+Enter
if sys.platform == "win32":
    import ctypes
    import msvcrt

# Session-local input history used by chat prompt navigation.
_INPUT_HISTORY = []
_MAX_INPUT_HISTORY = 200


class KindroidAPIClient:
    """Client for interacting with the Kindroid API."""

    DEFAULT_BASE_URL = "https://api.kindroid.ai/v1"

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        """
        Initialize the Kindroid API client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL of the Kindroid API (default: production)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type" : "application/json",
        })

    def send_message(
            self,
            chat_id: str,
            message: str,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a chat.

        Args:
            chat_id: The ID of the chat to send the message to
            message: The message content
            metadata: Optional metadata to attach to the message

        Returns:
            The API response as a dictionary

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/send-message"
        payload = {
            "ai_id"  : chat_id,
            "message": message,
        }
        if metadata:
            payload["metadata"] = metadata

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError:
            # If not JSON, return the raw text as response
            return {"raw_response": response.text}

    def get_chat_messages(
            self,
            chat_id: str,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve messages from a chat.

        Args:
            chat_id: The ID of the chat to retrieve messages from
            limit: Maximum number of messages to retrieve (default: API default)
            offset: Offset for pagination (default: 0)

        Returns:
            The API response containing messages

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/get-chat-messages"
        params = {"ai_id": chat_id}

        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["start_after_timestamp"] = offset

        response = self.session.get(url, params=params)
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError:
            # If not JSON, return the raw text as response
            return {"raw_response": response.text}


def load_api_key() -> str:
    """
    Load the API key from environment variable.

    Returns:
        The API key

    Raises:
        ValueError: If the API key is not found
    """
    api_key = os.environ.get("KINDROID_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please set the KINDROID_API_KEY environment variable."
        )
    return api_key


def load_chat_id(command_line_chat_id: Optional[str]) -> str:
    """
    Load the chat_id from command line argument or environment variable.

    Args:
        command_line_chat_id: The chat_id passed via command line (if any)

    Returns:
        The chat_id

    Raises:
        ValueError: If chat_id is not provided via command line or environment
    """
    if command_line_chat_id:
        return command_line_chat_id

    chat_id = os.environ.get("CHAT_ID")
    if not chat_id:
        raise ValueError(
            "Chat ID not found. Please pass --chat-id or set the CHAT_ID environment variable."
        )
    return chat_id


def load_kindroid_name(command_line_name: Optional[str]) -> str:
    """
    Load the kindroid name from command line argument or environment variable.

    Args:
        command_line_name: The kindroid name passed via command line (if any)

    Returns:
        The kindroid name

    Raises:
        ValueError: If kindroid name is not provided
    """
    if command_line_name:
        return command_line_name

    kindroid_name = os.environ.get("KINDROID_NAME")
    if not kindroid_name:
        raise ValueError(
            "Kindroid name not found. Please pass --kindroid or set the KINDROID_NAME environment variable."
        )
    return kindroid_name


def format_response(response: Dict[str, Any], pretty: bool = True) -> str:
    """
    Format the API response for display.

    Args:
        response: The API response dictionary
        pretty: Whether to pretty-print the JSON

    Returns:
        Formatted response string
    """
    if pretty:
        return json.dumps(response, indent=2)
    return json.dumps(response)


def format_unix_timestamp(timestamp_ms: int, format_str: str = "%Y-%m-%dT%H:%M:%S") -> str:
    """
    Convert unix timestamp in milliseconds to a formatted string.

    The timestamp is assumed to be in UTC and is automatically converted to
    the system's local timezone by datetime.fromtimestamp().

    Args:
        timestamp_ms: Unix timestamp in milliseconds
        format_str: strftime format string. Defaults to ISO 8601 with seconds.
                   Common formats:
                   - "%Y-%m-%dT%H:%M:%S" - ISO with seconds (default)
                   - "%Y-%m-%d %H:%M" - Display format without seconds
                   - "%Y-%m-%dT%H:%M:%S.%f" - ISO with microseconds

    Returns:
        Formatted timestamp string in the system's local timezone
    """
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000
    # Create datetime object (automatically converts UTC to system timezone)
    dt = datetime.fromtimestamp(timestamp_s)
    # Format according to provided format string
    return dt.strftime(format_str)


def send_message_command(args):
    """Handle the send-message command."""
    try:
        api_key = load_api_key()
        client = KindroidAPIClient(api_key, args.base_url)

        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in metadata", file=sys.stderr)
                return 1

        response = client.send_message(
            chat_id=load_chat_id(args.chat_id),
            message=args.message,
            metadata=metadata if metadata else None,
        )

        # Display the response
        if "raw_response" in response:
            # Unescape JSON escaped characters but keep the quotes
            text = response["raw_response"]
            text = text.replace('\\"', '"').replace('\\n', '\n')
            print(text)
        else:
            print(format_response(response, args.pretty))
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        return 1


def get_messages_command(args):
    """Handle the get-messages command."""
    try:
        # Check if we need to read from an existing output file
        offset_override = args.offset
        if args.output_file and os.path.exists(args.output_file):
            try:
                latest_timestamp = None
                with open(args.output_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            message = json.loads(line)
                            # Use the timestamp field (converted or original)
                            if "timestamp" in message:
                                latest_timestamp = message["timestamp"]

                if latest_timestamp:
                    # Convert ISO string back to milliseconds if needed for API
                    # For now, we'll pass it directly as the API expects it
                    offset_override = latest_timestamp
                    print(f"Resuming from timestamp: {latest_timestamp}", file=sys.stderr)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error reading output file: {e}", file=sys.stderr)
                return 1

        # Temporarily override offset for the generator
        original_offset = args.offset
        args.offset = offset_override

        # Collect all messages from the generator
        messages = list(_get_messages_impl(args))

        # Restore original args for consistency
        args.offset = original_offset

        # Output messages
        if args.output_file:
            # Append to file
            try:
                with open(args.output_file, 'a') as f:
                    for message in messages:
                        f.write(json.dumps(message) + '\n')
                print(f"Wrote {len(messages)} messages to {args.output_file}", file=sys.stderr)
            except IOError as e:
                print(f"Error writing to output file: {e}", file=sys.stderr)
                return 1
        else:
            # Print to console
            for message in messages:
                print(json.dumps(message))

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        return 1


def _get_messages_impl(args):
    """Handle the get-messages command."""
    try:
        api_key = load_api_key()
        client = KindroidAPIClient(api_key, args.base_url)
        chat_id = load_chat_id(args.chat_id)

        # Determine pagination strategy
        requested_limit = args.limit if args.limit else 50
        api_limit = min(requested_limit, 100)  # API max is 100
        needs_pagination = requested_limit > 100

        start_after_timestamp = args.offset if args.offset else None
        messages_fetched = 0

        # Fetch messages with pagination if needed
        while messages_fetched < requested_limit or not needs_pagination:
            response = client.get_chat_messages(
                chat_id=chat_id,
                limit=api_limit,
                offset=start_after_timestamp,
            )

            messages = response.get("messages", [])
            if not messages:
                break

            for m in messages:
                if requested_limit and messages_fetched >= requested_limit:
                    break
                if "timestamp" in m and isinstance(m["timestamp"], (int, float)):
                    m["datetime"] = format_unix_timestamp(m["timestamp"])
                yield m

            messages_fetched += len(messages)

            # Check if we have more pages
            pagination = response.get("pagination", {})
            if not pagination.get("hasMore", False) or not needs_pagination:
                break

            # Set cursor for next page
            start_after_timestamp = pagination.get("lastTimestamp")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)


def multiline_input(line_prompt: str = "", prompt: str = "") -> str:
    """
    Read multi-line input from user.

    On Windows: Shift+Enter creates a newline, Enter submits the message
    On other systems: Falls back to standard input()

    Args:
        line_prompt: The prompt to display

    Returns:
        The complete input (possibly multi-line) as a string
    """
    if sys.platform != "win32":
        # On non-Windows systems, use standard input
        return input(line_prompt)

    def redraw_current_line(line: str, cursor: int) -> None:
        # Basic in-place redraw for the active line (single-line editor behavior).
        terminal_width = max(20, shutil.get_terminal_size((80, 24)).columns)
        clear_width = max(terminal_width - 1, len(line_prompt) + len(line) + 2)
        print("\r" + (" " * clear_width) + "\r" + line_prompt + line, end="", flush=True)
        move_left = len(line) - cursor
        if move_left > 0:
            print("\b" * move_left, end="", flush=True)

    def shift_pressed() -> bool:
        # VK_SHIFT = 0x10
        return bool(ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000)

    lines = []
    current_chars = []
    cursor_pos = 0
    history_index = None
    draft_line = ""
    print(prompt)
    print(line_prompt, end="", flush=True)

    def set_current_line(text: str) -> None:
        nonlocal current_chars, cursor_pos
        current_chars = list(text)
        cursor_pos = len(current_chars)
        redraw_current_line("".join(current_chars), cursor_pos)

    while True:
        char = msvcrt.getch()

        if char == b"\x03":
            raise KeyboardInterrupt()

        if char in (b"\x00", b"\xe0"):
            ext = msvcrt.getch()
            # Left / Right / Up / Down / Home / End / Delete
            if ext == b"K" and cursor_pos > 0:
                cursor_pos -= 1
                redraw_current_line("".join(current_chars), cursor_pos)
            elif ext == b"M" and cursor_pos < len(current_chars):
                cursor_pos += 1
                redraw_current_line("".join(current_chars), cursor_pos)
            elif ext == b"H":  # Up: previous input history (single-line only)
                if lines:
                    continue
                if not _INPUT_HISTORY:
                    continue
                if history_index is None:
                    draft_line = "".join(current_chars)
                    history_index = len(_INPUT_HISTORY) - 1
                elif history_index > 0:
                    history_index -= 1
                set_current_line(_INPUT_HISTORY[history_index])
            elif ext == b"P":  # Down: next input history / restore draft
                if lines:
                    continue
                if history_index is None:
                    continue
                if history_index < len(_INPUT_HISTORY) - 1:
                    history_index += 1
                    set_current_line(_INPUT_HISTORY[history_index])
                else:
                    history_index = None
                    set_current_line(draft_line)
            elif ext == b"G":
                cursor_pos = 0
                redraw_current_line("".join(current_chars), cursor_pos)
            elif ext == b"O":
                cursor_pos = len(current_chars)
                redraw_current_line("".join(current_chars), cursor_pos)
            elif ext == b"S" and cursor_pos < len(current_chars):
                del current_chars[cursor_pos]
                redraw_current_line("".join(current_chars), cursor_pos)
            continue

        if char == b"\x08":  # Backspace
            if cursor_pos > 0:
                del current_chars[cursor_pos - 1]
                cursor_pos -= 1
                redraw_current_line("".join(current_chars), cursor_pos)
            continue

        if char == b"\r":  # Enter
            current_line = "".join(current_chars)
            if shift_pressed():
                # Shift+Enter inserts newline and keeps editing next line.
                lines.append(current_line)
                current_chars = []
                cursor_pos = 0
                print()
                print(line_prompt, end="", flush=True)
                continue

            lines.append(current_line)
            print()
            message = "\n".join(lines)
            # Keep prompt history practical for line recall (single-line messages only).
            if message and "\n" not in message:
                _INPUT_HISTORY.append(message)
                if len(_INPUT_HISTORY) > _MAX_INPUT_HISTORY:
                    del _INPUT_HISTORY[0]
            return message

        if char == b"\x1a":  # Ctrl+Z
            raise EOFError()

        # Regular printable character insert at cursor.
        char_str = char.decode("utf-8", errors="ignore")
        if char_str and char_str.isprintable():
            current_chars.insert(cursor_pos, char_str)
            cursor_pos += 1
            redraw_current_line("".join(current_chars), cursor_pos)


def chat_command(args):
    """Handle the interactive chat command."""
    try:
        api_key = load_api_key()
        client = KindroidAPIClient(api_key, args.base_url)
        chat_id = load_chat_id(args.chat_id)
        kindroid_name = load_kindroid_name(args.kindroid)

        # Fetch recent messages from last 24 hours
        print(f"Loading chat history...\n", file=sys.stderr)

        try:
            # Calculate offset for 24 hours ago (in milliseconds for API)
            now = datetime.now()
            twenty_four_hours_ago = now - timedelta(hours=24)
            offset_timestamp = int(twenty_four_hours_ago.timestamp() * 1000)

            # Create a mock args object for _get_messages_impl
            # Set high limit to ensure pagination captures all messages from last 24 hours
            history_args = argparse.Namespace(
                chat_id=args.chat_id,
                limit=9999,  # Fetch many messages to get full 24-hour history
                offset=offset_timestamp,  # Start from 24 hours ago
                base_url=args.base_url
            )

            all_recent_messages = list(_get_messages_impl(history_args))

            # Filter messages from last 24 hours (redundant but safe)
            recent_messages = []
            for msg in all_recent_messages:
                if "timestamp" in msg and isinstance(msg["timestamp"], (int, float)):
                    msg_time = datetime.fromtimestamp(msg["timestamp"] / 1000)
                    if msg_time >= twenty_four_hours_ago:
                        recent_messages.append(msg)

            # Display last 4 messages
            last_four = recent_messages[-4:] if recent_messages else []

            if last_four:
                print("\n--- Last messages ---\n")
                for msg in last_four:
                    sender = msg.get("sender", "unknown")
                    timestamp = msg.get("timestamp")
                    message_text = msg.get("message", "")

                    if timestamp and isinstance(timestamp, (int, float)):
                        time_str = format_unix_timestamp(timestamp, "%Y-%m-%d %H:%M")
                        if sender == "ai":
                            print(f"------------------\n[{time_str}] {kindroid_name}:")
                        else:
                            print(f"------------------\n[{time_str}]")
                        print(f"{message_text}\n")

        except Exception as e:
            print(f"Warning: Could not load chat history: {e}", file=sys.stderr)

        print(f"\n--- New messages ---\n")

        # Interactive loop
        while True:
            try:
                time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                # Prompt user for message (supports multi-line on Windows)
                message = multiline_input("", f"\n------------------\n[{time_str}]: ").strip()
                print(f"\n------------------")
                if not message:
                    continue

                # Send message to AI
                try:
                    response = client.send_message(
                        chat_id=chat_id,
                        message=message,
                    )

                    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    print(f"[{time_str}] {kindroid_name}:")

                    # Display the response
                    if "raw_response" in response:
                        # Unescape JSON escaped characters but keep the quotes
                        text = response["raw_response"].replace('\\"', '"').replace('\\n', '\n')
                        print(f"{text}\n")
                    else:
                        print(f"{format_response(response, args.pretty)}\n")

                except requests.exceptions.RequestException as e:
                    print(f"Error sending message: {e}\n", file=sys.stderr)

            except EOFError:
                # Ctrl-D on Unix or Ctrl-Z on Windows
                print("\nExiting chat...")
                return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # Ctrl-C
        print("\nExiting chat...")
        return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Kindroid API CLI - Interact with the Kindroid API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send a message to a chat
  python kindroid_cli.py send --chat-id abc123 "Hello, world!"

  # Get chat messages
  python kindroid_cli.py get --chat-id abc123 --limit 10

  # Use a custom API base URL
  python kindroid_cli.py --base-url https://api.example.com send --chat-id abc123 "Hello"

Environment Variables:
   KINDROID_API_KEY    The API key for authentication (required)
   CHAT_ID             The chat ID (fallback if --chat-id not provided)
        """,
    )

    parser.add_argument(
        "--base-url",
        default=KindroidAPIClient.DEFAULT_BASE_URL,
        help="The base URL of the Kindroid API (default: %(default)s)",
    )
    parser.add_argument(
        "--no-pretty",
        dest="pretty",
        action="store_false",
        default=True,
        help="Disable pretty-printing of JSON responses",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # send-message command
    send_parser = subparsers.add_parser(
        "send",
        help="Send a message to a chat",
    )
    send_parser.add_argument(
        "--chat-id",
        required=False,
        help="The ID of the chat to send the message to (can also use CHAT_ID env var)",
    )
    send_parser.add_argument(
        "message",
        help="The message content",
    )
    send_parser.add_argument(
        "--metadata",
        help="Optional JSON metadata to attach to the message",
    )
    send_parser.set_defaults(func=send_message_command)

    # get-chat-messages command
    get_parser = subparsers.add_parser(
        "get",
        help="Retrieve messages from a chat",
    )
    get_parser.add_argument(
        "--chat-id",
        required=False,
        help="The ID of the chat to retrieve messages from (can also use CHAT_ID env var)",
    )
    get_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of messages to retrieve",
    )
    get_parser.add_argument(
        "--offset",
        type=int,
        help="Offset for pagination",
    )
    get_parser.add_argument(
        "--output-file",
        help="File to write messages to (JSONL format). If file exists, continues from latest message.",
    )
    get_parser.set_defaults(func=get_messages_command)

    # chat command
    chat_parser = subparsers.add_parser(
        "chat",
        help="Start an interactive chat",
    )
    chat_parser.add_argument(
        "--chat-id",
        help="The ID of the chat to use (can also use CHAT_ID env var)",
    )
    chat_parser.add_argument(
        "--kindroid",
        help="The name of the Kindroid (can also use KINDROID_NAME env var)",
    )
    chat_parser.set_defaults(func=chat_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
