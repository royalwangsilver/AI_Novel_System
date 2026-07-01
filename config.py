import os
from dotenv import load_dotenv

load_dotenv()

API_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
}
