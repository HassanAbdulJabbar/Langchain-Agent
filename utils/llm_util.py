from langchain_openai import OpenAI

from config.config import config


class LLM_UTIL:
    def get_llm():
        """
        This function is responsible for all communication with the OPENAI.
        """

        return OpenAI(
            temperature=config.TEMPERATURE, openai_api_key=config.OPENAI_API_KEY
        )
