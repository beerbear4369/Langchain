# Voice-Enabled Chatbot

A conversational assistant that accepts spoken input, processes it using advanced language models, and responds with synthesized speech. Built with Python, LangChain, and OpenAI APIs.

## Features

- Speech-to-text using OpenAI's Whisper API
- Natural language understanding with GPT-4o
- Text-to-speech using OpenAI's TTS API
- Conversation memory to maintain context
- Simple console-based interface

## Requirements

- Python 3.8+
- OpenAI API key
- Microphone and speakers

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the application:

```
python main.py
```

### How the Application Works

1. When you start the application, it will welcome you with a voice greeting
2. When you see "Listening..." in the console, speak your question or command
3. The system will convert your speech to text using Whisper
4. It will then process your input using GPT-4o
5. You'll see and hear the response from the assistant
6. This process repeats until you say "exit", "quit", "bye", or "goodbye"

### Example Conversation

```
Voice-Enabled Chatbot
Say 'exit' or 'quit' to end the conversation.
--------------------------------------------------
Assistant: Hello! I'm your voice assistant. How can I help you today?
Listening...
Recording...
Recording finished.
Processing...
You: What's the weather like today?
Responding...
Assistant: I don't have access to real-time weather data. To check the current weather, you could look out a window, use a weather app on your phone, or check a weather website like weather.com or accuweather.com. Would you like me to help you with something else?
Listening...
```

### Customization

You can customize the assistant by modifying the following in `config.py`:

- **Recording duration**: Change `RECORD_SECONDS` to adjust how long it records
- **Voice**: Change `DEFAULT_VOICE` to use a different TTS voice
- **System prompt**: Modify `SYSTEM_PROMPT` to change the assistant's behavior and personality

## Troubleshooting

- **No audio recording**: Make sure your microphone is properly connected and has permission
- **API errors**: Verify your API key is correct in the `.env` file
- **Audio playback issues**: Check your speakers/headphones are connected and working
- **Poor transcription**: Try speaking clearly and reducing background noise

## How It Works

This application has four main components:

1. **Audio Input**: Records audio from your microphone and transcribes it using Whisper
2. **Conversation**: Manages the dialogue using LangChain and GPT-4o
3. **Audio Output**: Converts text responses to speech using OpenAI's TTS API
4. **Main Loop**: Coordinates the other components and handles user interaction

## File Structure

- `main.py`: The entry point of the application
- `audio_input.py`: Handles recording and transcription
- `conversation.py`: Manages the conversation flow
- `audio_output.py`: Handles text-to-speech conversion
- `config.py`: Contains configuration settings
- `requirements.txt`: Lists the required Python packages 