import logging

from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_community.tools import TavilySearchResults

from utils.llm_util import LLM_UTIL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_hybrid_agent(verbose=False):
    llm = LLM_UTIL.get_llm()

    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="output"
    )

    # Define the tools
    tools = [
        Tool(
            name="web_search",
            func=TavilySearchResults().run,
            description="Default tool for food, health, and general queries. Use for combined topics.",
        ),
        Tool(
            name="weather_agent",
            func=lambda query: "Weather information is available through the weather agent",
            description="Only for pure weather queries like temperature or rain.",
        ),
    ]

    # Create a concise prompt template
    template = """
    You are a helpful AI assistant who can answer all questions out of internet. Use tools to answer questions.
    
    Previous conversation:
    {chat_history}
    
    Tools:
    {tools}
    
    Format:
    Question: {input}
    Thought: Think about the query
    Action: Choose a tool [{tool_names}]
    Action Input: Query for the tool
    Observation: Tool's response
    Thought: Analyze the response
    Final Answer: Your answer
    
    Rules:
    1. Use web_search for any general queries
    2. Use weather_agent only for pure weather queries
    3. Default to web_search if unsure
    4. Always provide a final answer
    
    Question: {input}
    Thought: {agent_scratchpad}
    """

    prompt = PromptTemplate.from_template(template)

    # Initialize the agent with memory
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  # Changed to chat agent type
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=5,
        early_stopping_method="generate",
        memory=memory,  # Added memory
        return_intermediate_steps=True,  # Added to track conversation steps
    )

    return agent


def route_query(query: str, agent):
    """
    Route the query to the appropriate agent or tool
    """
    try:
        logger.info(f"Processing query: {query}")
        response = agent.invoke({"input": query})
        logger.info(f"Query processed successfully")

        if isinstance(response, dict):
            if "output" in response:
                return response["output"]
            elif "input" in response and "output" in response:
                return response["output"]

        return str(response)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return f"An error occurred while processing your query: {str(e)}"
