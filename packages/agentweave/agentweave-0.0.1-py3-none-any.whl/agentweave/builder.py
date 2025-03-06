"""Builder module for creating agents with a fluent API."""

from typing import Any, Dict, List, Optional, Type

from agentweave.core.base import BaseAgent


class AgentBuilder:
    """
    Builder class for creating Agent instances with a fluent API.

    This builder provides a more flexible and expressive way to configure
    agents compared to the basic constructor. It's designed for advanced
    users who need fine-grained control over agent configuration.

    Examples:
        >>> agent = Agent.builder()\\
        ...     .with_memory(VectorStoreMemory())\\
        ...     .with_tools([WebSearch(), Calculator()])\\
        ...     .with_model("gpt-4")\\
        ...     .build()
    """

    def __init__(self, agent_cls: Type[BaseAgent]):
        """
        Initialize the builder.

        Args:
            agent_cls: The agent class to build (usually Agent)
        """
        self.agent_cls = agent_cls
        self.config: Dict[str, Any] = {}
        self.tools: List[Any] = []
        self.memory: Optional[Any] = None
        self.model: Optional[str] = None

    def with_memory(self, memory: Any) -> "AgentBuilder":
        """
        Set the agent's memory component.

        Args:
            memory: A memory component instance

        Returns:
            The builder instance for chaining
        """
        self.memory = memory
        return self

    def with_tools(self, tools: List[Any]) -> "AgentBuilder":
        """
        Set the agent's tools.

        Args:
            tools: A list of tool instances

        Returns:
            The builder instance for chaining
        """
        self.tools = tools
        return self

    def with_model(self, model: str) -> "AgentBuilder":
        """
        Set the agent's language model.

        Args:
            model: The model identifier (e.g., "gpt-4")

        Returns:
            The builder instance for chaining
        """
        self.model = model
        return self

    def with_config(self, config: Dict[str, Any]) -> "AgentBuilder":
        """
        Set multiple configuration options at once.

        Args:
            config: A dictionary of configuration options

        Returns:
            The builder instance for chaining
        """
        self.config.update(config)
        return self

    def build(self) -> BaseAgent:
        """
        Build the agent with the configured options.

        Returns:
            An initialized Agent instance
        """
        # Merge all the configuration into a single dictionary
        final_config = self.config.copy()

        if self.memory is not None:
            final_config["memory"] = self.memory

        if self.tools:
            final_config["tools"] = self.tools

        if self.model:
            final_config["model"] = self.model

        # Create and return the agent instance
        return self.agent_cls(**final_config)
