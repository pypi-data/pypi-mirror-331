"""Main CLI entry point for AgentWeave."""

import argparse
import os
import sys

from agentweave import Agent
from agentweave.templates import list_templates


def main():
    """Main entry point for the AgentWeave CLI."""
    parser = argparse.ArgumentParser(description="AgentWeave CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List templates command
    subparsers.add_parser("list-templates", help="List available agent templates")

    # Run agent command
    run_parser = subparsers.add_parser("run", help="Run an agent with a query")
    run_parser.add_argument(
        "--template", "-t", default="assistant", help="Template to use"
    )
    run_parser.add_argument("--query", "-q", help="Query to run")
    run_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    # Init project command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new AgentWeave project"
    )
    init_parser.add_argument("project_name", help="Name of the project")

    # Parse arguments
    args = parser.parse_args()

    if args.command == "list-templates":
        # List available templates
        templates = list_templates()
        print("Available templates:")
        for name, description in templates.items():
            print(f"  - {name}: {description}")

    elif args.command == "run":
        # Run an agent
        agent = Agent.create(args.template)

        if args.interactive:
            # Interactive mode
            print(f"AgentWeave CLI - Interactive Mode (Template: {args.template})")
            print("Type 'exit' to quit")

            while True:
                try:
                    query = input("\nYou: ")
                    if query.lower() == "exit":
                        break

                    result = agent.run(query)
                    print(f"\nAgent: {result}")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {str(e)}")

        elif args.query:
            # Single query mode
            result = agent.run(args.query)
            print(result)

        else:
            # No query provided
            print(
                "Error: Please provide a query with --query or use --interactive mode"
            )
            return 1

    elif args.command == "init":
        # Initialize a new project
        project_name = args.project_name

        # Create project directory
        if os.path.exists(project_name):
            print(f"Error: Directory '{project_name}' already exists")
            return 1

        os.makedirs(project_name)

        # Create basic project files
        with open(os.path.join(project_name, "agent_config.yaml"), "w") as f:
            f.write(
                """# AgentWeave configuration
template: assistant
config:
  model: gpt-3.5-turbo
  memory_size: medium
  tools:
    - calculator
    - web_search
"""
            )

        with open(os.path.join(project_name, "README.md"), "w") as f:
            f.write(
                f"""# {project_name}

An AgentWeave project.

## Getting Started

```bash
# Run the agent
agentweave run --config agent_config.yaml
```
"""
            )

        print(f"Initialized new AgentWeave project in '{project_name}'")

    else:
        # No command provided
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
