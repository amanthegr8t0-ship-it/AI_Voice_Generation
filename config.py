import os
from dotenv import load_dotenv
from exceptions import ConfigurationError

load_dotenv()

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value or not value.strip():
        raise ConfigurationError(
            f"Missing required environment variable: '{key}'\n"
            f"Add it to your .env file: {key}=your_value_here"
        )
    return value.strip()

NVIDIA_API_KEY = _require("NVIDIA_API_KEY")