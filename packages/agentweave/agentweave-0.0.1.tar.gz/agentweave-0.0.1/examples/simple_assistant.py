"""Example of a simple assistant using AgentWeave."""

import sys
from pathlib import Path

# Add the parent directory to the path to be able to import agentweave
# This is only needed when running the example directly
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agentweave import Agent


def main():
    """Run a simple assistant example."""
    # Create a simple assistant agent
    agent = Agent.create("assistant")

    print("Simple AgentWeave Assistant")
    print("==========================")
    print("Type 'exit' to quit")
    print()

    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("You: ")

            # Exit if requested
            if user_input.lower() in ("exit", "quit"):
                break

            # Process the input
            response = agent.run(user_input)

            # Display the response
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
