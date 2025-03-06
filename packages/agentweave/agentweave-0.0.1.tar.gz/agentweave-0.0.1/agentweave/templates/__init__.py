"""Templates module for predefined agent configurations."""

from typing import Dict

from agentweave.templates.assistant import AssistantTemplate
from agentweave.templates.base import Template
from agentweave.templates.researcher import ResearcherTemplate

_TEMPLATES = {
    "researcher": ResearcherTemplate(),
    "assistant": AssistantTemplate(),
}


def get_template(template_name: str) -> Template:
    """
    Get a template by name.

    Args:
        template_name: The name of the template to get

    Returns:
        The template instance

    Raises:
        ValueError: If the template name is not recognized
    """
    if template_name not in _TEMPLATES:
        raise ValueError(
            f"Unknown template: {template_name}. "
            f"Available templates: {', '.join(_TEMPLATES.keys())}"
        )

    return _TEMPLATES[template_name]


def register_template(name: str, template: Template) -> None:
    """
    Register a new template.

    Args:
        name: The name to register the template under
        template: The template instance
    """
    _TEMPLATES[name] = template


def list_templates() -> Dict[str, str]:
    """
    List all available templates with descriptions.

    Returns:
        A dictionary mapping template names to descriptions
    """
    return {name: template.description for name, template in _TEMPLATES.items()}
