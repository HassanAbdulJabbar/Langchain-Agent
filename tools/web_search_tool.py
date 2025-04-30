from langchain_community.tools.tavily_search.tool import TavilySearchResults


def get_web_search_tool():
    """
    Returns the Tavily web search tool, allowing agents to search the web.
    Make sure TAVILY_API_KEY is set in environment variables.
    """
    return TavilySearchResults()
