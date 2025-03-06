"""Tests for tool implementations."""


from agentweave.tools import Calculator, WebSearch


def test_calculator():
    """Test Calculator implementation."""
    calculator = Calculator()

    # Test basic arithmetic
    result = calculator.run("2 + 2")
    assert result == 4.0

    # Test more complex expressions
    result = calculator.run("sqrt(16) + pow(2, 3)")
    assert result == 12.0

    # Test error handling
    result = calculator.run("1/0")
    assert isinstance(result, str)
    assert "Error" in result


def test_web_search():
    """Test WebSearch implementation."""
    search = WebSearch(api_key="test_key", search_engine="google", result_count=3)

    # Test search functionality
    results = search.run("test query")
    assert isinstance(results, list)
    assert len(results) > 0

    # Check result structure
    for result in results:
        assert "title" in result
        assert "url" in result
        assert "snippet" in result

    # Test API key setting
    search.set_api_key("new_key")
    assert search.api_key == "new_key"
