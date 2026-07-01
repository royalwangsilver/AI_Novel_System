import os
from dotenv import load_dotenv

load_dotenv()

API_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model": os.getenv("MODEL_NAME", "deepseek-chat"),
}
