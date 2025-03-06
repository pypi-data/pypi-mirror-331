"""Base template class for agent templates."""

import abc
from typing import Any, Dict


class Template(abc.ABC):
    """
    Abstract base class for agent templates.

    Templates provide predefined configurations for common agent types.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the template.

        Args:
            name: Template name
            description: Template description
        """
        self.name = name
        self.description = description

    @abc.abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration dictionary for this template.

        Returns:
            A dictionary with the template configuration
        """
        pass
