"""Simple in-memory storage for agent memory."""

from typing import Any, List

from agentweave.core.base import Memory


class SimpleMemory(Memory):
    """
    A simple in-memory implementation of agent memory.

    This class stores data in a list and provides basic search functionality.
    It's suitable for simple use cases but doesn't scale well for large amounts
    of data or complex semantic search.
    """

    def __init__(self, max_items: int = 100):
        """
        Initialize the simple memory.

        Args:
            max_items: Maximum number of items to store
        """
        self.max_items = max_items
        self.items: List[Any] = []

    def add(self, data: Any) -> None:
        """
        Add data to memory.

        Args:
            data: The data to store in memory
        """
        self.items.append(data)

        # Truncate if we've exceeded max items
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]

    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[Any]:
        """
        Retrieve data from memory based on a simple string search.

        This is a very basic implementation that checks if the query
        is a substring of the string representation of each item.

        Args:
            query: The query to search for in memory
            limit: Maximum number of results to return
            **kwargs: Additional parameters (unused)

        Returns:
            A list of matching memory items
        """
        results = []

        # Simple string matching (not efficient or semantically rich)
        for item in self.items:
            if query.lower() in str(item).lower():
                results.append(item)
                if len(results) >= limit:
                    break

        return results

    def clear(self) -> None:
        """Clear all items from memory."""
        self.items = []

    def __len__(self) -> int:
        """Get the number of items in memory."""
        return len(self.items)
