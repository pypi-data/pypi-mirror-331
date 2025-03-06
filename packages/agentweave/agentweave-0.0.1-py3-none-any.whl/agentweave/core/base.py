"""Base classes for the AgentWeave framework."""

import abc
from typing import Any, List, Optional


class BaseAgent(abc.ABC):
    """
    Abstract base class for all agents.

    This class defines the core interface that all agents must implement.
    It provides the foundation for the multi-layered architecture of AgentWeave.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        memory: Optional[Any] = None,
        tools: Optional[List[Any]] = None,
        **kwargs,
    ):
        """
        Initialize the base agent with common components.

        Args:
            model: Language model identifier
            memory: Memory component for the agent
            tools: List of tools the agent can use
            **kwargs: Additional configuration options
        """
        self.model = model
        self.memory = memory
        self.tools = tools or []
        self.config = kwargs

    @abc.abstractmethod
    def run(self, input_text: str, **kwargs) -> Any:
        """
        Run the agent with the given input.

        Args:
            input_text: The text input to process
            **kwargs: Additional run-time parameters

        Returns:
            The result of the agent's processing
        """
        pass


class Tool(abc.ABC):
    """
    Abstract base class for all tools.

    Tools provide specific capabilities to agents, such as web search,
    calculation, or API interactions.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the tool.

        Args:
            name: Name of the tool
            description: Description of what the tool does
        """
        self.name = name
        self.description = description

    @abc.abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Execute the tool functionality.

        Args:
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool

        Returns:
            The result of the tool execution
        """
        pass


class Memory(abc.ABC):
    """
    Abstract base class for all memory components.

    Memory components allow agents to store and retrieve information
    across interactions.
    """

    @abc.abstractmethod
    def add(self, data: Any) -> None:
        """
        Add data to memory.

        Args:
            data: The data to store in memory
        """
        pass

    @abc.abstractmethod
    def retrieve(self, query: str, **kwargs) -> List[Any]:
        """
        Retrieve data from memory based on a query.

        Args:
            query: The query to search for in memory
            **kwargs: Additional parameters for retrieval

        Returns:
            A list of relevant memory items
        """
        pass
