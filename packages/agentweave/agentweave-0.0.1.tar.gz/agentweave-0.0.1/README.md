# AgentWeave

AgentWeave is a framework for building and deploying AI agents powered by LangGraph.

## Features

- **LangGraph Integration**: Build powerful agents using LangGraph's graph-based architecture
- **Multiple Agent Types**: Choose between simple ReAct agents or custom graph-based agents
- **Tool Integration**: Easily add tools to your agents with a simple adapter pattern
- **Conversation Memory**: Maintain conversation context across interactions
- **Modern UI**: Beautiful and responsive UI built with Shadcn components
- **FastAPI Backend**: Robust and performant API built with FastAPI

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentweave.git
cd agentweave
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd web
npm install
```

### Running the Application

1. Start the backend server:
```bash
cd agentweave
uvicorn agentweave.api.main:app --reload
```

2. Start the frontend development server:
```bash
cd web
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

## Architecture

AgentWeave is built with a modular architecture:

- **Core**: Base classes and interfaces for agents, tools, and memory
- **LangGraph Agents**: Implementation of agents using LangGraph
- **API**: FastAPI-based REST API for interacting with agents
- **Web UI**: Next.js frontend with Shadcn UI components

### Agent Types

AgentWeave supports two types of LangGraph-based agents:

1. **LangGraphAgent**: A simple ReAct agent that uses LangGraph's built-in ReAct pattern
2. **CustomGraphAgent**: A more sophisticated agent with a custom graph flow for complex reasoning

### Templates

AgentWeave provides templates for common agent types:

- **Assistant**: A general-purpose conversational assistant
- **Researcher**: An agent optimized for research tasks

## API Reference

### Endpoints

- `GET /templates`: List available agent templates
- `POST /agents`: Create a new agent from a template
- `POST /query`: Send a one-off query to an agent
- `POST /chat`: Chat with an agent and maintain conversation state
- `WebSocket /ws/{agent_id}`: Stream interactions with an agent

## Development

### Adding New Tools

To add a new tool:

1. Create a new class that extends `LangGraphToolAdapter`
2. Implement the required methods
3. Add the tool to the default tools or a specific template

Example:
```python
class WeatherTool(LangGraphToolAdapter):
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather information for a location",
            func=self._get_weather
        )

    def _get_weather(self, location: str) -> str:
        # Implementation here
        return f"Weather for {location}: Sunny, 75°F"
```

### Creating Custom Graph Flows

To create a custom graph flow:

1. Extend the `CustomGraphAgent` class
2. Override the `_build_graph` method to define your custom flow

## License

This project is licensed under the MIT License - see the LICENSE file for details.
