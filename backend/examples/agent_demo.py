"""Demonstration script for the Task Management AI Agent.

This script shows how to use the agent programmatically to manage tasks
via natural language commands.

Prerequisites:
    1. Set OPENAI_API_KEY environment variable
    2. Have a running database with user tasks
    3. Know a valid user_id (UUID) from the system

Usage:
    cd backend
    uv run python examples/agent_demo.py

Example Output:
    User: Add a task called 'Buy groceries' with description 'Milk, eggs, bread'
    Agent: Created task 'Buy groceries' (ID: abc123-...)

    User: Show my tasks
    Agent: You have 3 tasks:
           1. [ ] Buy groceries (ID: abc...)
           2. [✓] Call mom (ID: def...)
           3. [ ] Finish report (ID: ghi...)
"""

import os
import sys

# Add the backend/src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_environment() -> bool:
    """Check if required environment variables are set."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY=sk-...")
        return False
    return True


def demo_sync():
    """Demonstrate synchronous agent usage."""
    from src.agent import run_agent

    # This should be a real user ID from your system
    demo_user_id = "550e8400-e29b-41d4-a716-446655440000"

    print("=" * 60)
    print("Task Management Agent Demo (Synchronous)")
    print("=" * 60)

    # Example commands to demonstrate
    demo_commands = [
        "Show my tasks",
        "Add a task called 'Buy groceries' with description 'Milk, eggs, bread'",
        "Show my tasks",
    ]

    for command in demo_commands:
        print(f"\nUser: {command}")
        try:
            response = run_agent(command, demo_user_id)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

        print("-" * 40)


async def demo_async():
    """Demonstrate asynchronous agent usage."""
    from src.agent import run_agent_async

    demo_user_id = "550e8400-e29b-41d4-a716-446655440000"

    print("\n" + "=" * 60)
    print("Task Management Agent Demo (Asynchronous)")
    print("=" * 60)

    commands = [
        "What tasks do I have?",
        "Create a task to call my dentist",
    ]

    for command in commands:
        print(f"\nUser: {command}")
        try:
            response = await run_agent_async(command, demo_user_id)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

        print("-" * 40)


def main():
    """Run the demo."""
    print("\nTask Management AI Agent - Demo Script")
    print("======================================\n")

    if not check_environment():
        sys.exit(1)

    # Run synchronous demo
    print("\nNote: This demo requires a running database and valid user.")
    print("If you see connection errors, ensure your DATABASE_URL is set.\n")

    try:
        demo_sync()
    except Exception as e:
        print(f"Sync demo failed: {e}")

    # Uncomment to run async demo
    # import asyncio
    # asyncio.run(demo_async())

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
