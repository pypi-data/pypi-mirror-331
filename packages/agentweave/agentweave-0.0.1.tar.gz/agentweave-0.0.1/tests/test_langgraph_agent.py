"""Tests for the LangGraph agent implementation."""

import os
import unittest
from unittest.mock import MagicMock, patch

from agentweave import Agent
from agentweave.core.custom_graph_agent import CustomGraphAgent
from agentweave.core.langgraph_agent import LangGraphAgent
from agentweave.core.tools import CalculatorTool, SearchTool


class TestLangGraphAgent(unittest.TestCase):
    """Test cases for the LangGraph agent implementation."""

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables for testing
        os.environ["ANTHROPIC_API_KEY"] = "test_key"

    @patch("langchain_anthropic.ChatAnthropic")
    def test_langgraph_agent_creation(self, mock_anthropic):
        """Test that a LangGraph agent can be created."""
        # Mock the LLM
        mock_llm = MagicMock()
        mock_anthropic.return_value = mock_llm

        # Create a LangGraph agent
        agent = LangGraphAgent(
            model="claude-3-5-sonnet-latest", tools=[SearchTool(), CalculatorTool()]
        )

        # Verify the agent was created with the correct properties
        self.assertEqual(agent.model, "claude-3-5-sonnet-latest")
        self.assertEqual(len(agent.tools), 2)
        self.assertIsNotNone(agent.graph)

    @patch("langchain_anthropic.ChatAnthropic")
    def test_custom_graph_agent_creation(self, mock_anthropic):
        """Test that a custom graph agent can be created."""
        # Mock the LLM
        mock_llm = MagicMock()
        mock_anthropic.return_value = mock_llm

        # Create a custom graph agent
        agent = CustomGraphAgent(
            model="claude-3-5-sonnet-latest", tools=[SearchTool(), CalculatorTool()]
        )

        # Verify the agent was created with the correct properties
        self.assertEqual(agent.model, "claude-3-5-sonnet-latest")
        self.assertEqual(len(agent.tools), 2)
        self.assertIsNotNone(agent.graph)

    @patch("agentweave.core.langgraph_agent.LangGraphAgent.run")
    def test_agent_facade(self, mock_run):
        """Test that the Agent facade correctly delegates to the implementation."""
        # Mock the run method
        mock_run.return_value = "Test response"

        # Create an agent using the facade
        agent = Agent(
            model="claude-3-5-sonnet-latest",
            tools=[SearchTool(), CalculatorTool()],
            agent_type="langgraph",
        )

        # Run the agent
        result = agent.run("Test input")

        # Verify the run method was called
        mock_run.assert_called_once_with("Test input")
        self.assertEqual(result, "Test response")

    @patch("agentweave.core.custom_graph_agent.CustomGraphAgent.run")
    def test_custom_agent_facade(self, mock_run):
        """Test that the Agent facade correctly delegates to the custom implementation."""
        # Mock the run method
        mock_run.return_value = "Custom test response"

        # Create an agent using the facade
        agent = Agent(
            model="claude-3-5-sonnet-latest",
            tools=[SearchTool(), CalculatorTool()],
            agent_type="custom_graph",
        )

        # Run the agent
        result = agent.run("Test input")

        # Verify the run method was called
        mock_run.assert_called_once_with("Test input")
        self.assertEqual(result, "Custom test response")


if __name__ == "__main__":
    unittest.main()
