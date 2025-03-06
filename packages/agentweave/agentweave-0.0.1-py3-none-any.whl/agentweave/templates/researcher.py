"""Researcher template for research-focused agents."""

from typing import Any, Dict

from agentweave.core.tools import CalculatorTool, SearchTool
from agentweave.templates.base import Template


class ResearcherTemplate(Template):
    """
    Template for a research-focused agent.

    This template configures an agent optimized for research tasks,
    with appropriate tools and settings for use with LangGraph.
    """

    def __init__(self):
        """Initialize the researcher template."""
        super().__init__(
            name="researcher", description="An agent optimized for research tasks"
        )

    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration for a researcher agent.

        Returns:
            A dictionary with the researcher agent configuration
        """
        # Create the tools for research
        search_tool = SearchTool()
        calculator_tool = CalculatorTool()

        return {
            "model": "claude-3-5-sonnet-latest",
            "tools": [search_tool, calculator_tool],
            "agent_type": "custom_graph",  # Use our advanced custom graph implementation
            "temperature": 0.2,  # Slightly creative but mostly factual
            "thread_id": None,  # Will be generated per agent
            "verbose": True,
        }
