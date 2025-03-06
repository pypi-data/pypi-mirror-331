"""Example of creating and using a custom tool in AgentWeave."""

import sys
from pathlib import Path
from typing import Any, Dict

import requests

# Add the parent directory to the path so we can import agentweave
sys.path.append(str(Path(__file__).parent.parent))

from agentweave import Agent
from agentweave.tools import Tool


class WeatherTool(Tool):
    """Tool for accessing current weather information."""

    def __init__(self, api_key: str = None):
        """
        Initialize the weather tool.

        Args:
            api_key: API key for OpenWeatherMap (optional for demo)
        """
        super().__init__(
            name="weather",
            description="Gets current weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name and optionally country code, e.g. 'London,UK'",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Temperature unit (metric: Celsius, imperial: Fahrenheit)",
                    },
                },
                "required": ["location"],
            },
        )
        self.api_key = api_key

    def run(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather for a location.

        Args:
            location: A city name (and optional country code)
            units: Temperature unit (metric/imperial)

        Returns:
            Dictionary with weather information
        """
        try:
            # Check if we have an API key
            if self.api_key:
                # Make a real API call
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {"q": location, "units": units, "appid": self.api_key}
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return {
                    "location": f"{data['name']}, {data['sys']['country']}",
                    "temperature": f"{data['main']['temp']}°{'C' if units == 'metric' else 'F'}",
                    "conditions": data["weather"][0]["description"],
                    "humidity": f"{data['main']['humidity']}%",
                    "wind": f"{data['wind']['speed']} {'m/s' if units == 'metric' else 'mph'}",
                }
            else:
                # Demo mode - return fake data
                temp = "22" if units == "metric" else "72"
                return {
                    "location": location,
                    "temperature": f"{temp}°{'C' if units == 'metric' else 'F'}",
                    "conditions": "Partly cloudy",
                    "humidity": "65%",
                    "wind": f"5 {'m/s' if units == 'metric' else 'mph'}",
                    "note": "This is simulated data as no API key was provided.",
                }
        except Exception as e:
            return {
                "error": f"Could not get weather data: {str(e)}",
                "location": location,
            }


class LocationSearchTool(Tool):
    """Tool for searching for locations by name."""

    def __init__(self):
        """Initialize the location search tool."""
        super().__init__(
            name="location_search",
            description="Search for locations by name to get detailed information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Location name to search for",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                    },
                },
                "required": ["query"],
            },
        )

    def run(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for locations by name.

        Args:
            query: Location name to search for
            limit: Maximum number of results

        Returns:
            Dictionary with location information
        """
        # This is a demo implementation with hardcoded data
        locations = [
            {"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278},
            {"name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060},
            {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522},
            {"name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503},
            {"name": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093},
            {"name": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437},
            {"name": "Berlin", "country": "DE", "lat": 52.5200, "lon": 13.4050},
            {"name": "Madrid", "country": "ES", "lat": 40.4168, "lon": -3.7038},
            {"name": "Rome", "country": "IT", "lat": 41.9028, "lon": 12.4964},
            {"name": "Cairo", "country": "EG", "lat": 30.0444, "lon": 31.2357},
        ]

        # Filter locations by query
        results = [
            loc
            for loc in locations
            if query.lower() in loc["name"].lower()
            or query.lower() in loc["country"].lower()
        ]

        # Limit results
        results = results[:limit]

        if not results:
            return {"error": f"No locations found for '{query}'"}

        return {"query": query, "count": len(results), "locations": results}


def main():
    """Run an example of using the custom tools."""
    # Create the tools
    weather_tool = WeatherTool()
    location_tool = LocationSearchTool()

    # Create an agent with the tools
    agent = (
        Agent.builder()
        .with_tools([weather_tool, location_tool])
        .with_model("gpt-4")
        .build()
    )

    print("=== Weather Tool Agent ===")
    print("Ask about weather in different locations or search for places.")
    print("Type 'exit' or 'quit' to end the program.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            response = agent.run(user_input)
            print(f"\nAgent: {response}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

    print("\nThank you for using the Weather Tool example!")


if __name__ == "__main__":
    main()
