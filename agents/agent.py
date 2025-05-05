import logging
from typing import List

from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, Tool
from langchain_community.tools import TavilySearchResults

from agents.weather_agent import WeatherAgent
from utils.llm_util import LLM_UTIL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["weather_response", "original_query"],
            template="""
            You are a weather response reviewer. Your task is to verify and enhance weather information responses.
            
            Original Query: {original_query}
            Weather Response: {weather_response}
            
            Review the response and provide a final, enhanced response that:
            1. Directly answers the original query
            2. Includes all necessary information (temperature, conditions, humidity, wind)
            3. Adds the current time in the local timezone
            4. Is clear and well-formatted
            5. Includes a brief source attribution
            
            Format your response as a single, concise paragraph. Do not include any analysis or numbered points.
            Current time should be in 24-hour format.
            
            Example format:
            "According to the latest weather data, [weather conditions] in [location] at [time]. Temperature is [temp]°C with [humidity]% humidity and [wind] km/h winds. Data provided by OpenWeatherMap."
            """
        )

    def review_response(self, weather_response: str, original_query: str) -> str:
        """Review and enhance the weather agent's response"""
        try:
            # Get the review from the LLM
            review_prompt = self.prompt_template.format(
                weather_response=weather_response, original_query=original_query
            )
            
            review = self.llm.invoke(review_prompt)
            # Clean up the response to remove any analysis or numbered points
            cleaned_response = review.split('\n')[-1] if '\n' in review else review
            return cleaned_response.strip()
        except Exception as e:
            logger.error(f"Error in review agent: {str(e)}")
            return weather_response  # Return original response if review fails


class ToolSelector:
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
        self.tool_descriptions = {tool.name: tool.description for tool in tools}

    def select_tool(self, query: str) -> str:
        """Select the most appropriate tool based on the query."""
        # Simple keyword-based selection
        query_lower = query.lower()

        # Weather-related keywords
        weather_keywords = [
            "weather",
            "temperature",
            "forecast",
            "rain",
            "snow",
            "humidity",
        ]
        if any(keyword in query_lower for keyword in weather_keywords):
            return "weather_agent"

        # Default to web search for everything else
        return "web_search"


def create_hybrid_agent(verbose=False):
    llm = LLM_UTIL.get_llm()
    weather_agent = WeatherAgent(llm)
    review_agent = ReviewAgent(llm)

    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="output"
    )

    # Define the tools with more specific descriptions
    tools = [
        Tool(
            name="web_search",
            func=TavilySearchResults().run,
            description="""Use this tool for:
            - General knowledge questions
            - News and current events
            - Facts and information
            - Non-weather related queries
            - Research and learning topics
            Input should be a clear search query.""",
        ),
        Tool(
            name="weather_agent",
            func=weather_agent.invoke,
            description="""Use this tool for:
            - Current weather conditions
            - Weather forecasts
            - Temperature queries
            - Precipitation information
            - Weather-related questions only""",
        ),
    ]

    # Create tool selector
    tool_selector = ToolSelector(tools)

    # Create a more structured prompt template
    template = """
    You are an intelligent AI assistant with access to specific tools. Your goal is to provide accurate and helpful responses using the most appropriate tool.

    Available Tools:
    {tools}

    Previous conversation:
    {chat_history}

    Current Question: {input}

    Follow these steps:
    1. Analyze the question carefully
    2. Select the most appropriate tool based on the question type
    3. Use the tool ONCE to get information
    4. Provide a clear and concise answer

    Tool Selection Rules:
    - Use weather_agent ONLY for weather-related queries
    - Use web_search for all other queries, especially for:
      * General knowledge questions
      * News and current events
      * Facts and information
      * Research topics
      * Learning concepts
    - If unsure, default to web_search
    - NEVER call the same tool multiple times for the same query

    Format your response as:
    Thought: Your reasoning about which tool to use
    Action: The tool you've selected
    Action Input: Your query for the tool
    Thought: Your analysis of the response
    Final Answer: Your final response to the user

    Current Question: {input}
    Thought: {agent_scratchpad}
    """

    prompt = PromptTemplate.from_template(template)

    # Initialize the agent with memory and custom prompt
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=2,
        early_stopping_method="generate",
        memory=memory,
        return_intermediate_steps=True,
        prompt=prompt,
    )

    return agent, tool_selector, review_agent


def route_query(query: str, agent, tool_selector, review_agent):
    """
    Route the query to the appropriate agent or tool with improved error handling
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # Get tool recommendation
        recommended_tool = tool_selector.select_tool(query)
        logger.info(f"Recommended tool: {recommended_tool}")
        
        # Process the query
        response = agent.invoke({"input": query})
        
        logger.info(f"Query processed successfully")

        # Extract the final answer from the response
        if isinstance(response, dict):
            if "output" in response:
                final_response = response["output"]
            elif "intermediate_steps" in response and response["intermediate_steps"]:
                # Get the last step's output
                last_step = response["intermediate_steps"][-1]
                if isinstance(last_step, tuple) and len(last_step) > 1:
                    # If the last step is an action, execute it
                    if isinstance(last_step[0], dict) and "action" in last_step[0]:
                        tool_name = last_step[0]["action"]
                        tool_input = last_step[0]["action_input"]
                        for tool in agent.tools:
                            if tool.name == tool_name:
                                try:
                                    final_response = tool.func(tool_input)
                                    # If it's a web search, format the response
                                    if tool_name == "web_search":
                                        final_response = format_web_search_response(final_response)
                                except Exception as e:
                                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                                    final_response = f"Sorry, I encountered an error while searching: {str(e)}"
                                break
                    else:
                        final_response = last_step[1]  # Return the observation
            elif "input" in response and "output" in response:
                final_response = response["output"]
            else:
                final_response = str(response)
        else:
            final_response = str(response)

        # If this was a weather query, have the review agent check the response
        if recommended_tool == "weather_agent":
            final_response = review_agent.review_response(final_response, query)

        return final_response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return f"An error occurred while processing your query: {str(e)}"


def format_web_search_response(response):
    """Format web search results into a readable response"""
    try:
        if isinstance(response, list):
            # Format multiple results
            formatted_response = "Here's what I found:\n\n"
            for i, result in enumerate(response[:3], 1):  # Limit to top 3 results
                formatted_response += f"{i}. {result.get('title', 'No title')}\n"
                formatted_response += f"   {result.get('snippet', 'No description')}\n\n"
            return formatted_response.strip()
        elif isinstance(response, dict):
            # Format single result
            return f"{response.get('title', 'No title')}\n{response.get('snippet', 'No description')}"
        else:
            return str(response)
    except Exception as e:
        logger.error(f"Error formatting web search response: {str(e)}")
        return str(response)
