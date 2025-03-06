"""Calculator tool for performing mathematical operations."""

import math
from typing import Union

from agentweave.core.base import Tool


class Calculator(Tool):
    """
    A calculator tool for performing mathematical operations.

    This tool allows agents to perform basic and advanced mathematical
    operations safely, using Python's built-in math functions.
    """

    def __init__(self):
        """Initialize the calculator tool."""
        super().__init__(
            name="calculator", description="Performs mathematical calculations"
        )

    def run(self, expression: str) -> Union[float, str]:
        """
        Evaluate a mathematical expression.

        The calculator uses a restricted environment to prevent
        code execution vulnerabilities.

        Args:
            expression: The mathematical expression to evaluate

        Returns:
            The result of the calculation or an error message

        Examples:
            >>> calculator = Calculator()
            >>> calculator.run("2 + 2")
            4.0
            >>> calculator.run("sqrt(16)")
            4.0
        """
        try:
            # Create a safe evaluation context with only math functions
            safe_context = {
                "abs": abs,
                "round": round,
                "max": max,
                "min": min,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "e": math.e,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "ceil": math.ceil,
                "floor": math.floor,
            }

            # Evaluate the expression in the safe context
            result = eval(expression, {"__builtins__": {}}, safe_context)

            return float(result)
        except Exception as e:
            return f"Error: {str(e)}"
