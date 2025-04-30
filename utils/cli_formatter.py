from colorama import Fore, Style, init

# Initialize colorama once
init(autoreset=True)


class FormatCLI:
    """This class is responsible for formatting CLI"""

    @staticmethod
    def format_user_input(prompt: str) -> str:
        return f"{Fore.GREEN}{Style.BRIGHT}User:{Style.RESET_ALL} {prompt}"

    @staticmethod
    def format_agent_output(response: str) -> str:
        return f"{Fore.CYAN}{Style.BRIGHT}Agent:{Style.RESET_ALL} {response}"

    @staticmethod
    def print_divider():
        print(f"{Fore.YELLOW}{'-'*60}{Style.RESET_ALL}")

    @staticmethod
    def print_intro():
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}🌐 LangChain CLI Assistant (Web + Weather Agent){Style.RESET_ALL}"
        )
        print("Type your question or type 'exit' to quit.\n")
        FormatCLI.print_divider()

    @staticmethod
    def print_exit():
        print(f"\n{Fore.BLUE}👋 Exiting... Goodbye!")

    @staticmethod
    def print_thinking():
        print(f"{Fore.YELLOW}🔎 Thinking...\n")

    @staticmethod
    def print_error(error: str):
        print(f"{Fore.RED}❌ Error: {error}")

    @staticmethod
    def _print_welcome_message() -> None:
        """Print the welcome message and available features"""
        print("Welcome to the Advanced Weather Assistant!")
        print("\nI can help you with:")
        print("- Current weather conditions")
        print("- Weather forecasts")
        print("- Air quality information")
        print("- UV index data")
        print("- Personalized weather recommendations")
        print("- Travel impact analysis")
        print("\nType 'help' for more information or 'exit' to quit")


formatCLI = FormatCLI()
