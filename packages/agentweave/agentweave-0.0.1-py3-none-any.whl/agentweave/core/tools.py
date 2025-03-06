"""Tool implementations for AgentWeave with LangGraph compatibility."""

import inspect
from typing import Any, Callable, List

from langchain_core.tools import BaseTool, tool

from agentweave.core.base import Tool


class LangGraphToolAdapter(Tool):
    """Adapter to make AgentWeave tools compatible with LangGraph."""

    def __init__(self, name: str, description: str, func: Callable):
        """
        Initialize the tool adapter.

        Args:
            name: Name of the tool
            description: Description of what the tool does
            func: The function to execute when the tool is run
        """
        super().__init__(name=name, description=description)
        self.func = func
        self._signature = inspect.signature(func)

    def run(self, *args, **kwargs) -> Any:
        """
        Execute the tool functionality.

        Args:
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool

        Returns:
            The result of the tool execution
        """
        return self.func(*args, **kwargs)

    def to_langchain_tool(self) -> BaseTool:
        """
        Convert to a LangChain tool format for use with LangGraph.

        Returns:
            A LangChain-compatible tool
        """

        # Create a LangChain tool using the tool decorator
        @tool(description=self.description)
        def langchain_tool(*args, **kwargs):
            """Tool function with the name and description from the adapter."""
            return self.run(*args, **kwargs)

        # Set the tool name
        langchain_tool.name = self.name

        return langchain_tool


class SearchTool(LangGraphToolAdapter):
    """Simple search tool implementation."""

    def __init__(self):
        """Initialize the search tool."""
        super().__init__(
            name="search",
            description="Search the web for information",
            func=self._search,
        )

    def _search(self, query: str) -> str:
        """
        Perform a web search.

        Args:
            query: The search query

        Returns:
            Search results
        """
        # This is a placeholder implementation
        if "weather" in query.lower():
            return "The weather is sunny today."
        elif "news" in query.lower():
            return "Latest news: AI continues to advance rapidly."
        else:
            return f"Search results for: {query}"


class CalculatorTool(LangGraphToolAdapter):
    """Simple calculator tool implementation."""

    def __init__(self):
        """Initialize the calculator tool."""
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations",
            func=self._calculate,
        )

    def _calculate(self, expression: str) -> str:
        """
        Evaluate a mathematical expression.

        Args:
            expression: The expression to evaluate

        Returns:
            Result of the calculation
        """
        try:
            # Basic safety check - only allow simple expressions
            allowed_chars = set("0123456789+-*/() .")
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"

            # Evaluate the expression
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating result: {str(e)}"


def get_default_tools() -> List[Tool]:
    """
    Get a list of default tools.

    Returns:
        List of default tools
    """
    return [
        SearchTool(),
        CalculatorTool(),
    ]
