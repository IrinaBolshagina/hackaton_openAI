from server import app
from llm import chat
import os
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    chat()
    # app.run()