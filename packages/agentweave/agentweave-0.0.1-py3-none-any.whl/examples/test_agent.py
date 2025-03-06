"""Example script to test the LangGraph agent implementation."""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import agentweave
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentweave import Agent
from agentweave.core.tools import SearchTool, CalculatorTool

# Load environment variables from .env file
load_dotenv()


def test_simple_agent():
    """Test a simple LangGraph agent."""
    print("Creating a simple LangGraph agent...")

    # Create a simple agent
    agent = Agent(
        model="claude-3-5-sonnet-latest",
        tools=[SearchTool(), CalculatorTool()],
        agent_type="langgraph",
    )

    # Test the agent with a simple query
    query = "What is the weather in San Francisco?"
    print(f"\nQuery: {query}")

    response = agent.run(query)
    print(f"\nResponse: {response}")

    # Test with a calculation
    query = "Calculate 15% of 85.75"
    print(f"\nQuery: {query}")

    response = agent.run(query)
    print(f"\nResponse: {response}")


def test_custom_graph_agent():
    """Test a custom graph agent."""
    print("\nCreating a custom graph agent...")

    # Create a custom graph agent
    agent = Agent(
        model="claude-3-5-sonnet-latest",
        tools=[SearchTool(), CalculatorTool()],
        agent_type="custom_graph",
    )

    # Test the agent with a simple query
    query = "What is the weather in New York?"
    print(f"\nQuery: {query}")

    response = agent.run(query)
    print(f"\nResponse: {response}")

    # Test with a calculation
    query = "If I have $120 and spend 35% on food, how much do I have left?"
    print(f"\nQuery: {query}")

    response = agent.run(query)
    print(f"\nResponse: {response}")


def test_chat_with_memory():
    """Test chat functionality with memory."""
    print("\nTesting chat with memory...")

    # Create an agent
    agent = Agent(
        model="claude-3-5-sonnet-latest",
        tools=[SearchTool(), CalculatorTool()],
        agent_type="custom_graph",
    )

    # First message
    message = "Hello, I'm planning a trip to San Francisco."
    print(f"\nUser: {message}")

    response = agent.chat(message)
    print(f"Agent: {response['messages'][-1]['content']}")

    # Get the thread ID for continuity
    thread_id = response.get("thread_id")

    # Follow-up question
    message = "What's the weather like there?"
    print(f"\nUser: {message}")

    response = agent.chat(message, thread_id=thread_id)
    print(f"Agent: {response['messages'][-1]['content']}")

    # Check if tools were used
    if "steps" in response and response["steps"]:
        print("\nTools used:")
        for step in response["steps"]:
            print(f"  Tool: {step['tool']}")
            print(f"  Input: {step['input']}")
            print(f"  Output: {step['output']}")


def test_from_template():
    """Test creating an agent from a template."""
    print("\nCreating an agent from a template...")

    # Create a researcher agent
    agent = Agent.create("researcher")

    # Test the agent
    query = "What are the latest advancements in quantum computing?"
    print(f"\nQuery: {query}")

    response = agent.run(query)
    print(f"\nResponse: {response}")


if __name__ == "__main__":
    # Check if ANTHROPIC_API_KEY is set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        sys.exit(1)

    # Run the tests
    test_simple_agent()
    test_custom_graph_agent()
    test_chat_with_memory()
    test_from_template()
