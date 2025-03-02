import os  # For accessing environment variables
from dotenv import load_dotenv  # For loading .env files

# Load environment variables from .env file
# This allows you to store your API key securely
load_dotenv()

# API Configuration
# This gets the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Audio Recording Configuration
# These settings control how audio is recorded
SAMPLE_RATE = 44100  # CD quality audio (44.1 kHz)
CHANNELS = 1  # Mono audio (1 channel)
CHUNK_SIZE = 1024  # How many samples to process at once
RECORD_SECONDS = 5  # Default recording time in seconds
WAVE_OUTPUT_FILENAME = "input.wav"  # Default filename if needed

# Text-to-Speech Configuration
# This controls which voice is used for speech synthesis
DEFAULT_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer

# Conversation Configuration
# This defines how the AI assistant should behave
SYSTEM_PROMPT = """You are a helpful, friendly assistant. Respond concisely and clearly.
Your responses will be spoken out loud to the user, so format them appropriately for speech."""

# UI Configuration
# These messages are displayed to the user during different stages
RECORDING_START_MESSAGE = "Listening..."
RECORDING_STOP_MESSAGE = "Processing..."
RESPONSE_START_MESSAGE = "Responding..." 