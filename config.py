import os  # For accessing environment variables
import json
from dotenv import load_dotenv  # For loading .env files
import sys

# Add debugging information
print("=== Config Debug Info ===")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
if hasattr(sys, '_MEIPASS'):
    print(f"PyInstaller _MEIPASS: {sys._MEIPASS}")
else:
    print("Not running from PyInstaller package")

# Try to load from .env file first (for development)
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# If API key is not set, try to load from config.json
if not OPENAI_API_KEY:
    try:
        # Look for config.json in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                if 'OPENAI_API_KEY' in config_data:
                    OPENAI_API_KEY = config_data['OPENAI_API_KEY']
    except Exception as e:
        print(f"Warning: Could not load config file: {e}")

print(f"Final API key status: {'Set' if OPENAI_API_KEY else 'Not set'}")
print("=== End Config Debug Info ===")

# Model Configuration
# This defines which OpenAI model to use

# Model fine-tuned in the week of 24th Feb 2025
# MODEL_NAME = "ft:gpt-4o-mini-2024-07-18:bearly-alone:coaching-finetuning-test:B4VpCGe9:ckpt-step-90"

# Model fine-tuned in the week of 2nd Mar 2025 with 8 dialogues and new system prompt with T-GROW and ORID integration etc
# MODEL_NAME ="ft:gpt-4o-mini-2024-07-18:bearly-alone::B6sTevwQ:ckpt-step-90"

# Model fine-tuned with 8 dialogues and new system prompt with T-GROW and ORID integration etc on original 4o mini model
# MODEL_NAME ="ft:gpt-4o-mini-2024-07-18:bearly-alone:4o-mini-with-real-data:B6syMadK:ckpt-step-90"

# Model fine-tuned on 7 March 2025 with 8 dialogues and new system prompt with user feedback 4o mini
# MODEL_NAME ="ft:gpt-4o-mini-2024-07-18:bearly-alone:coach-prompt4-realdata-v2:B8FyjppY"

# Model fine-tuned on 7 March 2025 with 8 dialogues and new system prompt with user feedback 4o
# MODEL_NAME ="ft:gpt-4o-2024-08-06:bearly-alone:coach-prompt4-realdata-4o-v3:B8GBRv5R"

# Model fine-tuned on 7 March 2025 with 8 dialogues and new system prompt5 with user feedback 4o
MODEL_NAME ="ft:gpt-4o-mini-2024-07-18:bearly-alone:coach-prompt5-realdata-v1:B8MoGLxp:ckpt-step-80"


# Model for testing with gpt-4.5-preview(largest model)
# MODEL_NAME = "gpt-4.5-preview"

MODEL_TEMPERATURE = 0.7

# Audio Recording Configuration
# These settings control how audio is recorded
SAMPLE_RATE = 44100  # CD quality audio (44.1 kHz)
CHANNELS = 1  # Mono audio (1 channel)
CHUNK_SIZE = 1024  # How many samples to process at once
RECORD_SECONDS = 300  # Maximum recording time in seconds (5 minutes)
WAVE_OUTPUT_FILENAME = "input.wav"  # Default filename if needed

# Text-to-Speech Configuration
# This controls which voice is used for speech synthesis
DEFAULT_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer

# Conversation Configuration
# This defines how the AI assistant should behave
SYSTEM_PROMPT = """You are a helpful, friendly coaching assistant. Respond concisely and clearly.
Your responses will be spoken out loud to the user, so format them appropriately for speech."""

# UI Configuration
# These messages are displayed to the user during different stages
RECORDING_START_MESSAGE = "Listening..."
RECORDING_STOP_MESSAGE = "Processing..."
RESPONSE_START_MESSAGE = "Responding..." 