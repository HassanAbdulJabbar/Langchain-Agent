# Weather Agent

A sophisticated command-line weather application that combines the power of AI agents with weather forecasting capabilities. This project demonstrates the integration of LangChain, OpenAI, and custom agent architectures to provide intelligent weather-related assistance.

## Features

- Interactive command-line interface with colorful formatting
- AI-powered weather information retrieval
- Hybrid agent architecture for intelligent query processing
- Real-time weather data processing
- Error handling and graceful exit capabilities

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Tavily API key (for enhanced search capabilities)

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project root with your API keys:

    ```bash
    OPENAI_API_KEY=your_openai_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

## Project Structure

```bash
.
├── agents/           # Agent implementations
├── config/          # Configuration files
├── tools/           # Custom tools and utilities
├── utils/           # Utility functions and helpers
├── main.py          # Main application entry point
├── requirements.txt # Project dependencies
└── Makefile         # Build and development commands
```

## Usage

Run the application:

```bash
python main.py
```

The application provides an interactive CLI where you can:

- Ask weather-related questions
- Get real-time weather information
- Exit using 'exit' or 'quit' commands

## Make Commands

The project includes several useful Make commands to help with development and running the application:

```bash
# Start the weather agent (creates venv, installs dependencies, and runs the app)
make start-weather-agent

# Format all Python files using black and isort
make format-code

# Clean Python cache files
make clean-cache
```

## Development

The project uses a hybrid agent architecture that combines:

- Main agent for query processing
- Tool selector for appropriate tool selection
- Review agent for response validation

## Dependencies

- langchain: Core AI framework
- openai: OpenAI API integration
- python-dotenv: Environment variable management
- colorama: Terminal text coloring
- requests: HTTP requests
- tavily-python: Enhanced search capabilities

## Acknowledgments

- OpenAI for providing the AI capabilities
- LangChain for the agent framework
- Tavily for enhanced search capabilities
