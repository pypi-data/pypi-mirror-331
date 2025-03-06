"""Agent module provides the main Agent class for interacting with AgentWeave."""

from typing import Any, Dict, List, Optional, Union

from agentweave.builder import AgentBuilder
from agentweave.core.base import BaseAgent
from agentweave.core.custom_graph_agent import CustomGraphAgent
from agentweave.core.langgraph_agent import LangGraphAgent
from agentweave.core.tools import get_default_tools
from agentweave.templates import get_template


class Agent(BaseAgent):
    """
    The main Agent class for AgentWeave.

    This class provides a simple interface for creating and using agents.
    It supports both a simple API for beginners and advanced customization
    for power users.
    """

    @classmethod
    def create(cls, template_name: str, **kwargs) -> "Agent":
        """
        Create an agent from a template.

        This is the simplest way to create an agent, suitable for beginners.

        Args:
            template_name: The name of the template to use (e.g., "researcher", "assistant")
            **kwargs: Optional overrides for template defaults

        Returns:
            An initialized Agent instance

        Examples:
            >>> agent = Agent.create("researcher")
            >>> result = agent.run("Research quantum computing")
        """
        template = get_template(template_name)
        config = template.get_config()

        # Apply any overrides from kwargs
        for key, value in kwargs.items():
            if key in config:
                config[key] = value

        return cls(**config)

    @classmethod
    def builder(cls) -> AgentBuilder:
        """
        Get an agent builder for advanced configuration.

        This provides a fluent interface for advanced users to configure
        every aspect of the agent.

        Returns:
            An AgentBuilder instance

        Examples:
            >>> agent = Agent.builder()\\
            ...     .with_memory(VectorStoreMemory())\\
            ...     .with_tools([WebSearch(), Calculator()])\\
            ...     .with_model("gpt-4")\\
            ...     .build()
        """
        return AgentBuilder(cls)

    @classmethod
    def from_config(cls, config_path: str) -> "Agent":
        """
        Create an agent from a configuration file.

        Args:
            config_path: Path to a YAML or JSON configuration file

        Returns:
            An initialized Agent instance
        """
        # Implementation for loading from config file will be added
        raise NotImplementedError("Loading from config is not yet implemented")

    def __init__(
        self,
        model: Optional[str] = "claude-3-5-sonnet-latest",
        memory: Optional[Any] = None,
        tools: Optional[List[Any]] = None,
        agent_type: str = "langgraph",
        **kwargs,
    ):
        """
        Initialize the agent with the given configuration.

        Args:
            model: Language model identifier
            memory: Memory component for the agent
            tools: List of tools the agent can use
            agent_type: Type of agent implementation to use
                        ("langgraph", "custom_graph", or "basic")
            **kwargs: Additional configuration options
        """
        # Set default tools if none provided
        if tools is None:
            tools = get_default_tools()

        self.implementation: Union[LangGraphAgent, CustomGraphAgent, None] = None

        if agent_type == "langgraph":
            # Create a simple LangGraph ReAct agent
            self.implementation = LangGraphAgent(
                model=model, memory=memory, tools=tools, **kwargs
            )
        elif agent_type == "custom_graph":
            # Create a custom graph-based agent
            self.implementation = CustomGraphAgent(
                model=model, memory=memory, tools=tools, **kwargs
            )
        else:
            # Fallback to basic implementation
            super().__init__(model=model, memory=memory, tools=tools, **kwargs)
            self.implementation = None

    def run(self, input_text: str, **kwargs) -> Any:
        """
        Run the agent with the given input.

        Args:
            input_text: The text input to process
            **kwargs: Additional run-time parameters

        Returns:
            The result of the agent's processing
        """
        if self.implementation:
            return self.implementation.run(input_text, **kwargs)

        # Fallback implementation
        return f"Agent processed: {input_text}"

    def chat(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Chat with the agent and return the full state.

        Args:
            input_text: The text input to process
            **kwargs: Additional run-time parameters

        Returns:
            The full state including messages history
        """
        if self.implementation is not None and hasattr(self.implementation, "chat"):
            return self.implementation.chat(input_text, **kwargs)

        # Fallback implementation
        result = self.run(input_text, **kwargs)
        return {
            "messages": [
                {"role": "user", "content": input_text},
                {"role": "assistant", "content": result},
            ]
        }
