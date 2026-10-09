#!/usr/bin/env python3
"""
Example usage of the Kindroid CLI utility.

This script demonstrates how to use the kindroid_cli module programmatically.
"""

import os
from kindroid_cli import KindroidAPIClient, load_api_key


def main():
    """Run example commands."""

    try:
        # Load API key from environment
        api_key = load_api_key()
        client = KindroidAPIClient(api_key)

        # Example 1: Send a message
        print("=" * 50)
        print("Example 1: Sending a message")
        print("=" * 50)
        try:
            response = client.send_message(
                chat_id="example_chat_id",
                message="Hello from the Kindroid CLI!",
                metadata={"source": "cli_example", "version": "1.0"}
            )
            print("Success! Response:")
            print(response)
        except Exception as e:
            print(f"Failed to send message: {e}")

        # Example 2: Get chat messages
        print("\n" + "=" * 50)
        print("Example 2: Retrieving chat messages")
        print("=" * 50)
        try:
            response = client.get_chat_messages(
                chat_id="example_chat_id",
                limit=10,
                offset=0
            )
            print("Success! Response:")
            print(response)
        except Exception as e:
            print(f"Failed to retrieve messages: {e}")

    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set the KINDROID_API_KEY environment variable:")
        print("  Windows (PowerShell): $env:KINDROID_API_KEY = 'your_key'")
        print("  Linux/macOS: export KINDROID_API_KEY='your_key'")


if __name__ == "__main__":
    main()

