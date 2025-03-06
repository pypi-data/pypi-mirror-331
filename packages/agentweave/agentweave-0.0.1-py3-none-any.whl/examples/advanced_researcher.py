"""Example of an advanced research agent using AgentWeave."""

import sys
from pathlib import Path

# Add the parent directory to the path to be able to import agentweave
# This is only needed when running the example directly
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agentweave import Agent
from agentweave.memory import VectorStoreMemory
from agentweave.tools import Calculator, WebSearch


def main():
    """Run an advanced research agent example."""
    # Create a more advanced agent with explicit configuration
    agent = (
        Agent.builder()
        .with_memory(VectorStoreMemory())
        .with_tools([WebSearch(), Calculator()])
        .with_model("gpt-4")
        .build()
    )

    print("Advanced AgentWeave Research Agent")
    print("=================================")
    print("This agent uses:")
    print("- Vector store memory for semantic recall")
    print("- Web search for up-to-date information")
    print("- Calculator for numerical operations")
    print("- GPT-4 for advanced reasoning")
    print()
    print("Type 'exit' to quit")
    print()

    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("Research question: ")

            # Exit if requested
            if user_input.lower() in ("exit", "quit"):
                break

            print("\nProcessing your request. This may take a moment...\n")

            # Process the input
            response = agent.run(user_input)

            # Display the response
            print(f"\nFindings:\n{response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
