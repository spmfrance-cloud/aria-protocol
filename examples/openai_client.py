#!/usr/bin/env python3
"""
Example: Using OpenAI client with ARIA Protocol.

This example demonstrates how to use the standard OpenAI Python client
to interact with ARIA Protocol's OpenAI-compatible API server.

Prerequisites:
    1. Install the OpenAI client: pip install openai
    2. Start an ARIA node: aria node start --port 8765 --model aria-2b-1bit
    3. Start the API server: aria api start --port 3000 --node-port 8765

Usage:
    python examples/openai_client.py

MIT License - Anthony MURGO, 2026
"""

import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI client not installed.")
    print("Install it with: pip install openai")
    sys.exit(1)


def main():
    """Demonstrate OpenAI client usage with ARIA."""

    # Configure the client to use ARIA's API server
    # The api_key can be any string - ARIA doesn't require authentication
    client = OpenAI(
        base_url="http://localhost:3000/v1",
        api_key="aria"  # Any value works, ARIA doesn't check this
    )

    print("ARIA Protocol - OpenAI Client Example")
    print("=" * 50)
    print()

    # Example 1: Simple chat completion
    print("1. Simple Chat Completion")
    print("-" * 50)

    try:
        response = client.chat.completions.create(
            model="aria-2b-1bit",
            messages=[
                {"role": "user", "content": "What is artificial intelligence?"}
            ],
            max_tokens=100
        )

        print(f"Model: {response.model}")
        print(f"Response ID: {response.id}")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Finish reason: {response.choices[0].finish_reason}")
        print(f"Usage: {response.usage.prompt_tokens} prompt + "
              f"{response.usage.completion_tokens} completion = "
              f"{response.usage.total_tokens} total tokens")

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure ARIA node and API server are running:")
        print("  Terminal 1: aria node start --port 8765 --model aria-2b-1bit")
        print("  Terminal 2: aria api start --port 3000 --node-port 8765")
        return 1

    print()

    # Example 2: Chat with system message
    print("2. Chat with System Message")
    print("-" * 50)

    response = client.chat.completions.create(
        model="aria-2b-1bit",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Explain quantum computing in one sentence."}
        ],
        max_tokens=50,
        temperature=0.7
    )

    print(f"Content: {response.choices[0].message.content}")
    print()

    # Example 3: Multi-turn conversation
    print("3. Multi-turn Conversation")
    print("-" * 50)

    messages = [
        {"role": "user", "content": "What is Python?"},
    ]

    response = client.chat.completions.create(
        model="aria-2b-1bit",
        messages=messages,
        max_tokens=50
    )

    # Add assistant response to conversation
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    print(f"User: What is Python?")
    print(f"Assistant: {assistant_message}")

    # Continue the conversation
    messages.append({"role": "user", "content": "What are its main uses?"})

    response = client.chat.completions.create(
        model="aria-2b-1bit",
        messages=messages,
        max_tokens=50
    )

    print(f"User: What are its main uses?")
    print(f"Assistant: {response.choices[0].message.content}")
    print()

    # Example 4: List available models
    print("4. List Available Models")
    print("-" * 50)

    models = client.models.list()
    for model in models.data:
        print(f"  - {model.id} (owned by: {model.owned_by})")
    print()

    # Example 5: Streaming (simulated)
    print("5. Streaming Response")
    print("-" * 50)

    stream = client.chat.completions.create(
        model="aria-2b-1bit",
        messages=[
            {"role": "user", "content": "Count from 1 to 5."}
        ],
        max_tokens=50,
        stream=True
    )

    print("Response: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()
    print()

    print("=" * 50)
    print("All examples completed successfully!")
    print()
    print("ARIA Protocol provides an OpenAI-compatible API that allows")
    print("you to use any tool or library designed for OpenAI's API.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
