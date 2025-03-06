"""Tests for memory implementations."""


from agentweave.memory import SimpleMemory, VectorStoreMemory


def test_simple_memory():
    """Test SimpleMemory implementation."""
    memory = SimpleMemory(max_items=3)

    # Test adding items
    memory.add("Item 1")
    memory.add("Item 2")
    memory.add("Item 3")

    assert len(memory) == 3

    # Test max items limit
    memory.add("Item 4")
    assert len(memory) == 3

    # Test simple retrieval
    results = memory.retrieve("Item")
    assert len(results) > 0

    # Test clear
    memory.clear()
    assert len(memory) == 0


def test_vector_store_memory():
    """Test VectorStoreMemory implementation."""
    memory = VectorStoreMemory(embedding_model="test-model")

    # Test adding items
    memory.add("Information about AI")
    memory.add({"text": "Information about robotics", "type": "article"})

    # Test retrieval
    results = memory.retrieve("AI", limit=1)
    assert len(results) <= 1

    # Test clear
    memory.clear()

    # Test adding and retrieving with metadata
    memory.add({"text": "Data with metadata", "source": "test", "importance": "high"})
    results = memory.retrieve("data")

    assert len(results) > 0
    assert "metadata" in results[0]
