import os

import dotenv

dotenv.load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TEMPERATURE = 0


config = Config()
