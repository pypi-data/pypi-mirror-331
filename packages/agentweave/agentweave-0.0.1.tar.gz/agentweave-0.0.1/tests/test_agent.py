"""Tests for the Agent class."""


from agentweave import Agent
from agentweave.memory import SimpleMemory
from agentweave.tools import Calculator


def test_agent_create():
    """Test the Agent.create class method."""
    agent = Agent.create("assistant")
    assert agent is not None
    assert agent.model == "gpt-3.5-turbo"


def test_agent_builder():
    """Test the Agent builder pattern."""
    agent = (
        Agent.builder()
        .with_memory(SimpleMemory())
        .with_tools([Calculator()])
        .with_model("gpt-4")
        .build()
    )

    assert agent is not None
    assert agent.model == "gpt-4"
    assert len(agent.tools) == 1
    assert agent.memory is not None


def test_agent_run():
    """Test the Agent.run method."""
    agent = Agent.create("assistant")
    response = agent.run("Hello, world!")

    assert response is not None
    assert isinstance(response, str)
    assert "Hello, world!" in response
