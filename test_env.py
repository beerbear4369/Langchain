# test_env.py
import os
from dotenv import load_dotenv

# Print current directory to verify where Python is looking for the .env file
print(f"Current directory: {os.getcwd()}")

# You can also specify the path explicitly if needed
# load_dotenv(dotenv_path="C:/Founder_Depression/Backend/langchain/.env")
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key loaded successfully!")
    # Print just the first few characters for verification
    print(f"Key starts with: {api_key[:5]}...")
else:
    print("Failed to load API key. Check your .env file.")
    