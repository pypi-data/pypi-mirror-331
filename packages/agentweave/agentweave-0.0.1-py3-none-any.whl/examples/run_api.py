"""Script to run the AgentWeave API server."""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the parent directory to the path so we can import agentweave
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()


def main():
    """Run the API server."""
    # Check if ANTHROPIC_API_KEY is set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable is not set.")
        print("The API will start, but agent functionality may be limited.")

    print("Starting AgentWeave API server...")
    print("API will be available at http://localhost:8000")
    print("API documentation will be available at http://localhost:8000/docs")

    # Run the server
    uvicorn.run("agentweave.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
