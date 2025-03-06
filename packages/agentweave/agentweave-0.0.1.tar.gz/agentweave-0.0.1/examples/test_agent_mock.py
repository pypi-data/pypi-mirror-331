"""Example script to test the LangGraph agent implementation with mocks."""

import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import agentweave
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentweave import Agent
from agentweave.core.tools import SearchTool, CalculatorTool


def test_simple_agent():
    """Test a simple LangGraph agent with mocks."""
    print("Creating a simple LangGraph agent...")

    # Create a mock for the LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="This is a mocked response from the LLM."
    )

    # Patch the ChatAnthropic class
    with patch("langchain_anthropic.ChatAnthropic", return_value=mock_llm):
        # Create a simple agent
        agent = Agent(
            model="claude-3-5-sonnet-latest",
            tools=[SearchTool(), CalculatorTool()],
            agent_type="langgraph",
        )

        # Test the agent with a simple query
        query = "What is the weather in San Francisco?"
        print(f"\nQuery: {query}")

        # Patch the run method to return a mock response
        with patch.object(
            agent.implementation,
            "run",
            return_value="The weather in San Francisco is currently 65°F and foggy.",
        ):
            response = agent.run(query)
            print(f"\nResponse: {response}")


def test_custom_graph_agent():
    """Test a custom graph agent with mocks."""
    print("\nCreating a custom graph agent...")

    # Create a mock for the LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="This is a mocked response from the LLM."
    )

    # Patch the ChatAnthropic class
    with patch("langchain_anthropic.ChatAnthropic", return_value=mock_llm):
        # Create a custom graph agent
        agent = Agent(
            model="claude-3-5-sonnet-latest",
            tools=[SearchTool(), CalculatorTool()],
            agent_type="custom_graph",
        )

        # Test the agent with a simple query
        query = "What is the weather in New York?"
        print(f"\nQuery: {query}")

        # Patch the run method to return a mock response
        with patch.object(
            agent.implementation,
            "run",
            return_value="The weather in New York is currently 75°F and sunny.",
        ):
            response = agent.run(query)
            print(f"\nResponse: {response}")


def test_chat_with_memory():
    """Test chat functionality with memory using mocks."""
    print("\nTesting chat with memory...")

    # Create a mock for the LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="This is a mocked response from the LLM."
    )

    # Patch the ChatAnthropic class
    with patch("langchain_anthropic.ChatAnthropic", return_value=mock_llm):
        # Create an agent
        agent = Agent(
            model="claude-3-5-sonnet-latest",
            tools=[SearchTool(), CalculatorTool()],
            agent_type="custom_graph",
        )

        # First message
        message = "Hello, I'm planning a trip to San Francisco."
        print(f"\nUser: {message}")

        # Mock the chat method
        mock_response = {
            "messages": [
                {"role": "user", "content": message},
                {
                    "role": "assistant",
                    "content": "That's great! San Francisco is a beautiful city with lots to see and do.",
                },
            ],
            "thread_id": "mock_thread_123",
        }

        with patch.object(agent.implementation, "chat", return_value=mock_response):
            response = agent.chat(message)
            print(f"Agent: {response['messages'][-1]['content']}")

            # Get the thread ID for continuity
            thread_id = response.get("thread_id")

            # Follow-up question
            message = "What's the weather like there?"
            print(f"\nUser: {message}")

            # Mock the chat method for the follow-up
            mock_response_2 = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, I'm planning a trip to San Francisco.",
                    },
                    {
                        "role": "assistant",
                        "content": "That's great! San Francisco is a beautiful city with lots to see and do.",
                    },
                    {"role": "user", "content": "What's the weather like there?"},
                    {
                        "role": "assistant",
                        "content": "San Francisco typically has mild weather year-round. Currently, it's around 65°F with fog in the morning that usually clears by afternoon.",
                    },
                ],
                "thread_id": thread_id,
                "steps": [
                    {
                        "tool": "search",
                        "input": "current weather in San Francisco",
                        "output": "65°F, foggy in the morning, clear in the afternoon",
                    }
                ],
            }

            with patch.object(
                agent.implementation, "chat", return_value=mock_response_2
            ):
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
    """Test creating an agent from a template with mocks."""
    print("\nCreating an agent from a template...")

    # Create a mock for the LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="This is a mocked response from the LLM."
    )

    # Patch the ChatAnthropic class
    with patch("langchain_anthropic.ChatAnthropic", return_value=mock_llm):
        # Create a researcher agent
        agent = Agent.create("researcher")

        # Test the agent
        query = "What are the latest advancements in quantum computing?"
        print(f"\nQuery: {query}")

        # Patch the run method to return a mock response
        with patch.object(
            agent.implementation,
            "run",
            return_value="Recent advancements in quantum computing include improvements in error correction, increased qubit coherence times, and the development of more stable quantum processors.",
        ):
            response = agent.run(query)
            print(f"\nResponse: {response}")


if __name__ == "__main__":
    # Run the tests
    test_simple_agent()
    test_custom_graph_agent()
    test_chat_with_memory()
    test_from_template()
