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
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import requests


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
            "Content-Type": "application/json",
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
            "ai_id": chat_id,
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
            params["offset"] = offset

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


def unix_timestamp_to_iso(timestamp_ms: int) -> str:
    """
    Convert unix timestamp in milliseconds to ISO 8601 datetime string.

    Args:
        timestamp_ms: Unix timestamp in milliseconds

    Returns:
        ISO 8601 formatted datetime string with timezone info
    """
    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000
    # Create datetime object and format as ISO string with timezone
    dt = datetime.fromtimestamp(timestamp_s)
    return dt.isoformat()


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
        api_key = load_api_key()
        client = KindroidAPIClient(api_key, args.base_url)
        chat_id = load_chat_id(args.chat_id)

        # Determine pagination strategy
        requested_limit = args.limit if args.limit else 50
        api_limit = min(requested_limit, 100)  # API max is 100
        needs_pagination = requested_limit > 100

        all_messages = []
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

            all_messages.extend(messages)
            messages_fetched += len(messages)

            # Check if we have more pages
            pagination = response.get("pagination", {})
            if not pagination.get("hasMore", False) or not needs_pagination:
                break

            # Set cursor for next page
            start_after_timestamp = pagination.get("lastTimestamp")

        # Limit results to requested amount
        all_messages = all_messages[:requested_limit]

        # Output as JSONL with converted timestamps
        for message in all_messages:
            # Convert timestamp if present
            if "timestamp" in message and isinstance(message["timestamp"], (int, float)):
                message["timestamp"] = unix_timestamp_to_iso(message["timestamp"])

            # Output as JSONL (one JSON object per line)
            print(json.dumps(message))

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        return 1


def chat_command(args):
    """Handle the interactive chat command."""
    try:
        api_key = load_api_key()
        client = KindroidAPIClient(api_key, args.base_url)
        chat_id = load_chat_id(args.chat_id)

        print("Starting chat (press Ctrl-C to exit)...\n")

        while True:
            try:
                # Prompt user for message
                message = input("You: ").strip()
                if not message:
                    continue

                # Send message to AI
                try:
                    response = client.send_message(
                        chat_id=chat_id,
                        message=message,
                    )

                    # Display the response
                    if "raw_response" in response:
                        # Unescape JSON escaped characters but keep the quotes
                        text = response["raw_response"]
                        text = text.replace('\\"', '"').replace('\\n', '\n')
                        print(f"Kindroid: {text}\n")
                    else:
                        print(f"Kindroid: {format_response(response, args.pretty)}\n")

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
    chat_parser.set_defaults(func=chat_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

