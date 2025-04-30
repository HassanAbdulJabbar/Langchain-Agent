from typing import Any, Callable, Dict

from agents.weather_agent import WeatherAgent


class CommandHandler:
    def __init__(self, weather_agent: WeatherAgent):
        self.weather_agent = weather_agent
        self.commands: Dict[str, Callable] = {
            "weather": self._handle_weather,
            "forecast": self._handle_forecast,
            "air": self._handle_air,
            "recommend": self._handle_recommend,
            "travel": self._handle_travel,
            "help": self._handle_help,
        }

    def handle_command(self, command: str, args: list) -> str:
        """Handle the given command with its arguments"""
        if command not in self.commands:
            # If command is not recognized, treat the entire input as a query
            query = f"{command} {' '.join(args)}".strip()
            return self.weather_agent.invoke(query)

        return self.commands[command](args)

    def _handle_weather(self, args: list) -> str:
        """Handle weather command"""
        if not args:
            return "Please provide a location. Usage: weather [location]"
        location = " ".join(args)
        return self.weather_agent.invoke(f"What's the current weather in {location}?")

    def _handle_forecast(self, args: list) -> str:
        """Handle forecast command"""
        if len(args) < 1:
            return "Please provide a location and optionally number of days. Usage: forecast [location] [days]"

        location = " ".join(args[:-1]) if len(args) > 1 else args[0]
        days = int(args[-1]) if len(args) > 1 and args[-1].isdigit() else 3

        return self.weather_agent.invoke(
            f"What's the {days}-day forecast for {location}?"
        )

    def _handle_air(self, args: list) -> str:
        """Handle air quality command"""
        if not args:
            return "Please provide a location. Usage: air [location]"
        location = " ".join(args)
        return self.weather_agent.invoke(f"What's the air quality in {location}?")

    def _handle_recommend(self, args: list) -> str:
        """Handle recommendations command"""
        if not args:
            return "Please provide a location. Usage: recommend [location]"
        location = " ".join(args)
        return self.weather_agent.invoke(
            f"What are the weather recommendations for {location}?"
        )

    def _handle_travel(self, args: list) -> str:
        """Handle travel impact command"""
        if not args:
            return "Please provide a location. Usage: travel [location]"
        location = " ".join(args)
        return self.weather_agent.invoke(f"What's the travel impact in {location}?")

    def _handle_help(self, args: list) -> str:
        """Handle help command"""
        help_text = """
        Available commands:
        - 'weather [location]' - Get current weather
        - 'forecast [location] [days]' - Get weather forecast (default 3 days)
        - 'air [location]' - Get air quality information
        - 'recommend [location]' - Get personalized recommendations
        - 'travel [location]' - Get travel impact analysis
        - 'help' - Show this help message
        - 'exit' or 'quit' - Exit the program
        """
        return help_text
