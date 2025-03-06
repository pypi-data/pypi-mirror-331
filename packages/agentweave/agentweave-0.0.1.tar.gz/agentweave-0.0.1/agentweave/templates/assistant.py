"""Assistant template for general-purpose assistant agents."""

from typing import Any, Dict

from agentweave.core.tools import get_default_tools
from agentweave.templates.base import Template


class AssistantTemplate(Template):
    """
    Template for a general-purpose assistant agent.

    This template configures an agent optimized for conversation and
    assistance tasks using LangGraph.
    """

    def __init__(self):
        """Initialize the assistant template."""
        super().__init__(
            name="assistant",
            description="A general-purpose conversational assistant agent",
        )

    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration for an assistant agent.

        Returns:
            A dictionary with the assistant agent configuration
        """
        # Get default tools for the assistant
        tools = get_default_tools()

        return {
            "model": "claude-3-5-sonnet-latest",
            "tools": tools,
            "agent_type": "langgraph",  # Use the basic ReAct agent for assistants
            "temperature": 0.7,  # More creative for conversational interactions
            "thread_id": None,  # Will be generated per agent
            "verbose": True,
        }
