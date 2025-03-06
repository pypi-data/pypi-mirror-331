"""LangGraph-based agent implementation for AgentWeave."""

import uuid
from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from agentweave.core.base import BaseAgent


class LangGraphAgent(BaseAgent):
    """
    Agent implementation using LangGraph.

    This class provides a LangGraph-powered agent that uses the ReAct pattern
    for reasoning and tool use.
    """

    def __init__(
        self,
        model: Optional[str] = "claude-3-5-sonnet-latest",
        memory: Optional[Any] = None,
        tools: Optional[List[Any]] = None,
        **kwargs,
    ):
        """
        Initialize the LangGraph agent with common components.

        Args:
            model: Language model identifier (defaults to Claude 3.5 Sonnet)
            memory: Memory component for the agent
            tools: List of tools the agent can use
            **kwargs: Additional configuration options
        """
        super().__init__(model=model, memory=memory, tools=tools, **kwargs)

        # Initialize LangGraph components
        self.thread_id = kwargs.get("thread_id", str(uuid.uuid4()))
        self.temperature = kwargs.get("temperature", 0)
        self.checkpointer = MemorySaver()

        # Initialize the LLM
        self.llm = ChatAnthropic(model=self.model, temperature=self.temperature)

        # Create the LangGraph agent
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph agent graph."""
        # Convert tools to LangChain format if needed
        langchain_tools = self._prepare_tools()

        # Create the ReAct agent
        return create_react_agent(
            self.llm, langchain_tools, checkpointer=self.checkpointer
        )

    def _prepare_tools(self) -> List[Any]:
        """Prepare tools for use with LangGraph."""
        # If no tools are provided, return an empty list
        if not self.tools:
            return []

        # Convert AgentWeave tools to LangChain tool format if needed
        langchain_tools = []
        for t in self.tools:
            if hasattr(t, "to_langchain_tool"):
                langchain_tools.append(t.to_langchain_tool())
            else:
                # Assume it's already a LangChain-compatible tool
                langchain_tools.append(t)

        return langchain_tools

    def run(self, input_text: str, **kwargs) -> Any:
        """
        Run the agent with the given input.

        Args:
            input_text: The text input to process
            **kwargs: Additional run-time parameters

        Returns:
            The result of the agent's processing
        """
        # Convert input to message format
        messages = [{"role": "user", "content": input_text}]

        # Use thread ID from kwargs if provided, otherwise use the default
        thread_id = kwargs.get("thread_id", self.thread_id)

        # Run the agent
        final_state = self.graph.invoke(
            {"messages": messages}, config={"configurable": {"thread_id": thread_id}}
        )

        # Return the last message - handle AIMessage objects which have .content property
        last_message = final_state["messages"][-1]
        # Handle both dictionary messages and AIMessage objects
        if hasattr(last_message, "content"):
            return last_message.content
        elif isinstance(last_message, dict) and "content" in last_message:
            return last_message["content"]
        else:
            return str(last_message)  # Fallback to string representation

    def chat(self, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Chat with the agent and return the full state.

        Args:
            input_text: The text input to process
            **kwargs: Additional run-time parameters

        Returns:
            The full state including messages history
        """
        # Get thread ID from kwargs or use default
        thread_id = kwargs.get("thread_id", self.thread_id)

        # Get existing messages if they exist
        existing_state = self.checkpointer.get(thread_id) if thread_id else None

        if existing_state and "messages" in existing_state:
            # Add new message to existing messages
            messages = existing_state["messages"] + [
                {"role": "user", "content": input_text}
            ]
        else:
            # Start a new conversation
            messages = [{"role": "user", "content": input_text}]

        # Run the agent
        final_state = self.graph.invoke(
            {"messages": messages}, config={"configurable": {"thread_id": thread_id}}
        )

        # Convert any Message objects to dictionaries for consistent return format
        if "messages" in final_state:
            converted_messages = []
            for msg in final_state["messages"]:
                if hasattr(msg, "content") and hasattr(msg, "type"):
                    # Convert LangChain message to dict format
                    role = (
                        "assistant"
                        if msg.type == "ai"
                        else "user"
                        if msg.type == "human"
                        else "system"
                    )
                    converted_messages.append({"role": role, "content": msg.content})
                elif isinstance(msg, dict):
                    # Already a dict
                    converted_messages.append(msg)
                else:
                    # Unknown format, convert to string
                    converted_messages.append({"role": "unknown", "content": str(msg)})

            # Replace messages with converted format
            final_state = dict(
                final_state
            )  # Create a copy to avoid modifying the original
            final_state["messages"] = converted_messages

        return final_state  # type: ignore
