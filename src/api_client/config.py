# gorest_api_tests/src/api_client/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()

# Retrieve API base URL from environment variables, with a default fallback
BASE_URL = os.getenv("GOREST_BASE_URL", "https://gorest.co.in/public/v2")

# Retrieve API token from environment variables
API_TOKEN = os.getenv("GOREST_API_TOKEN")

# Critical check: Ensure the API token is set
if not API_TOKEN:
    raise ValueError(
        "GOREST_API_TOKEN environment variable not set. "
        "Please configure your .env file in the project root with GOREST_API_TOKEN."
    )

# Print loaded configuration (optional, for debugging)
# print(f"Loaded API Base URL: {BASE_URL}")
# print(f"API Token loaded: {'Yes' if API_TOKEN else 'No'}")
