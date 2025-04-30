import sys
from typing import Tuple

from agents.agent import create_hybrid_agent, route_query
from agents.weather_agent import WeatherAgent
from utils.cli_formatter import formatCLI
from utils.command_handler import CommandHandler
from utils.llm_util import LLM_UTIL


class WeatherApp:
    def __init__(self):
        self.llm = LLM_UTIL.get_llm()
        self.weather_agent = WeatherAgent(self.llm)
        self.command_handler = CommandHandler(self.weather_agent)

    def setup(self) -> None:
        """Initialize the application"""
        try:
            formatCLI.print_intro()
            formatCLI._print_welcome_message()
        except EnvironmentError as e:
            formatCLI.print_error(str(e))
            sys.exit(1)

    def _parse_input(self, user_input: str) -> Tuple[str, list]:
        """Parse user input into command and arguments"""
        parts = user_input.strip().split()
        if not parts:
            return "", []
        command = parts[0].lower()
        args = parts[1:]
        return command, args

    def run(self) -> None:
        """Run the main application loop"""
        while True:
            try:
                user_input = input(formatCLI.format_user_input(""))
                command, args = self._parse_input(user_input)

                if command in {"exit", "quit"}:
                    formatCLI.print_exit()
                    break

                formatCLI.print_thinking()
                agent = create_hybrid_agent(verbose=True)
                response = route_query(user_input, agent)
                print(formatCLI.format_agent_output(response))

            except Exception as e:
                formatCLI.print_error(str(e))

            formatCLI.print_divider()


def main() -> int:
    """Main entry point for the application"""
    try:
        app = WeatherApp()
        app.setup()
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as e:
        formatCLI.print_error(f"An unexpected error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
