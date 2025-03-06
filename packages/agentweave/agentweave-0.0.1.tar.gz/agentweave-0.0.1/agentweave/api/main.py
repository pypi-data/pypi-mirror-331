"""Main FastAPI application for AgentWeave."""

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agentweave import Agent
from agentweave.templates import list_templates

app = FastAPI(
    title="AgentWeave API",
    description="API for interacting with AgentWeave agents powered by LangGraph",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests and responses
class AgentRequest(BaseModel):
    """Request model for creating an agent."""

    template: str
    config: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    """Request model for querying an agent."""

    query: str
    agent_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request model for chat with an agent."""

    message: str
    thread_id: Optional[str] = None
    agent_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """Model for chat messages."""

    role: str
    content: str


class Step(BaseModel):
    """Model for tool execution steps."""

    tool: str
    input: str
    output: str


class AgentResponse(BaseModel):
    """Response model with agent information."""

    agent_id: str
    template: str
    config: Dict[str, Any]


class QueryResponse(BaseModel):
    """Response model with query results."""

    result: Any
    agent_id: str


class ChatResponse(BaseModel):
    """Response model with chat results."""

    messages: List[Message]
    thread_id: str
    agent_id: str
    steps: Optional[List[Step]] = None


# In-memory store for active agents
active_agents: Dict[str, Agent] = {}


@app.get("/")
async def root():
    """Get API information."""
    return {
        "name": "AgentWeave API",
        "version": "0.1.0",
        "description": "API for interacting with AgentWeave agents powered by LangGraph",
    }


@app.get("/templates", response_model=Dict[str, str])
async def get_templates():
    """Get available agent templates."""
    return list_templates()


@app.post("/agents", response_model=AgentResponse)
async def create_agent(request: AgentRequest):
    """Create a new agent from a template."""
    try:
        # Generate a simple ID based on the number of agents
        agent_id = f"agent_{len(active_agents) + 1}"

        # Create the agent from the template
        config = request.config or {}
        agent = Agent.create(request.template, **config)

        # Store the agent
        active_agents[agent_id] = agent

        return {
            "agent_id": agent_id,
            "template": request.template,
            "config": config,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating agent: {str(e)}"
        ) from e


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Query an agent with a prompt."""
    # Check if agent_id is provided and valid
    if request.agent_id:
        if request.agent_id not in active_agents:
            raise HTTPException(
                status_code=404, detail=f"Agent {request.agent_id} not found"
            )
        agent = active_agents[request.agent_id]
    else:
        # Create a default agent if none specified
        agent = Agent.create("assistant")
        request.agent_id = "default_agent"

    try:
        # Run the agent with the query
        result = agent.run(request.query, **(request.config or {}))

        return {
            "result": result,
            "agent_id": request.agent_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error querying agent: {str(e)}"
        ) from e


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with an agent and get the full conversation state."""
    # Check if agent_id is provided and valid
    if request.agent_id:
        if request.agent_id not in active_agents:
            raise HTTPException(
                status_code=404, detail=f"Agent {request.agent_id} not found"
            )
        agent = active_agents[request.agent_id]
    else:
        # Create a default agent if none specified
        agent = Agent.create("assistant")
        request.agent_id = "default_agent"

    try:
        # Prepare configuration with thread_id
        config = request.config or {}
        if request.thread_id:
            config["thread_id"] = request.thread_id

        # Run the agent chat method
        state = agent.chat(request.message, **config)

        # Get thread_id from state or create a default one
        thread_id = config.get("thread_id", "default_thread")

        # Format messages to match our API response model
        messages = [
            Message(role=m["role"], content=m["content"])
            for m in state.get("messages", [])
        ]

        # Format steps if they exist
        steps = None
        if "steps" in state and state["steps"]:
            steps = [
                Step(tool=s["tool"], input=s["input"], output=s["output"])
                for s in state["steps"]
            ]

        return {
            "messages": messages,
            "thread_id": thread_id,
            "agent_id": request.agent_id,
            "steps": steps,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error chatting with agent: {str(e)}"
        ) from e


@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for streaming interactions with an agent."""
    await websocket.accept()

    try:
        # Check if the agent exists
        if agent_id not in active_agents and agent_id != "new_agent":
            await websocket.send_json({"error": f"Agent {agent_id} not found"})
            await websocket.close()
            return

        # Create a new agent if requested
        if agent_id == "new_agent":
            agent_id = f"agent_{len(active_agents) + 1}"
            active_agents[agent_id] = Agent.create("assistant")
            await websocket.send_json({"agent_id": agent_id, "status": "created"})

        agent = active_agents[agent_id]

        # Handle messages
        while True:
            data = await websocket.receive_json()

            if "message" in data:
                # Process the chat message
                message = data["message"]
                thread_id = data.get("thread_id")
                config = data.get("config", {})

                if thread_id:
                    config["thread_id"] = thread_id

                # Process chat and get response
                state = agent.chat(message, **config)

                # Get the thread_id from config or create a default one
                thread_id = config.get("thread_id", "default_thread")

                # Format steps if they exist
                steps = None
                if "steps" in state and state["steps"]:
                    steps = [
                        {"tool": s["tool"], "input": s["input"], "output": s["output"]}
                        for s in state["steps"]
                    ]

                # Send complete state back to client
                await websocket.send_json(
                    {
                        "messages": state.get("messages", []),
                        "thread_id": thread_id,
                        "agent_id": agent_id,
                        "steps": steps,
                        "status": "complete",
                    }
                )

    except WebSocketDisconnect:
        # Handle client disconnect
        pass
    except Exception as e:
        # Handle errors
        await websocket.send_json({"error": str(e)})
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
