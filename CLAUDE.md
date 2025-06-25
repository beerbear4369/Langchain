# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Start API server (development)
python start_api.py

# Start API server with auto-reload
python start_api.py --reload

# Start API server on custom port
python start_api.py --port 8080

# Start API directly with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Testing Commands
```bash
# Run all tests
python -m pytest tests/

# Run conversation memory tests
python tests/test_conversation_memory.py

# Run conversation flow tests (uses real audio files)
python tests/test_conversation_flow.py

# Run API tests (requires server running)
python test_api.py

# Check conversation summary logs
python tests/check_summary_logs.py

# Test specific conversation scenarios
python tests/test_wrap_up_prompt.py
python tests/test_conversation_end_extended.py
```

### Data Export Commands
```bash
# Export conversation data for evaluation (from data_export/ folder)
cd data_export
python export_conversations.py output.jsonl

# Export with filters
python export_conversations.py eval_data.jsonl --min-rating 4 --status ended --min-messages 8

# Test export functionality
python test_export.py
```

### Deployment Commands
```bash
# Build Windows executable
build_ai_coach_b.bat

# Start production server
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Architecture Overview

### Core Components

**FastAPI Application (`app.py`)**
- Main API server with 5 core endpoints for frontend integration
- Session management using in-memory storage (global `sessions` dictionary)
- CORS enabled for frontend integration
- Handles audio upload, transcription, and TTS response generation

**Conversation Engine (`conversation.py`)**
- Built on LangChain with ConversationSummaryBufferMemory for handling long conversations
- Uses fine-tuned GPT models for enhanced emotional intelligence coaching
- Implements automatic conversation summarization after ~3000 tokens
- Complex wrap-up confirmation flow with state-dependent logic

**Audio Processing Pipeline**
- `audio_input.py`: Whisper API for speech-to-text transcription
- `audio_output.py`: ElevenLabs API for text-to-speech generation
- Audio files stored in `temp_audio/` directory
- Audio responses served via `/audio/` endpoint

**Configuration Management (`config.py`)**
- Supports multiple fine-tuned models via AVAILABLE_MODELS dictionary
- Currently using `gpt41mini_hyper2` model with enhanced EQ training
- API keys loaded from environment variables or fallback config.json
- Model-specific temperature settings (O3 models don't support temperature)

### Session Management Architecture

The system uses a **stateless API with simulated state** pattern:
- Each session has a unique `session_id` as the key
- All session context stored in global `sessions` dictionary in `app.py`
- Session attributes include: conversation instance, round count, status, wrap-up flags
- **Critical**: All session state must be consistently stored/retrieved

### Conversation Flow Priority Logic

Message processing follows this **debugged and verified** order:
1. **Check for awaiting wrap-up confirmation** (highest priority)
2. **Check for new wrap-up request** (secondary priority)  
3. **Process as normal conversation** (default)

This order prevents critical logic loop bugs in wrap-up confirmation sequences.

### Memory Management

Uses **ConversationSummaryBufferMemory** for scalable conversation handling:
- Keeps recent messages (up to 3000 tokens) in full detail
- Automatically summarizes older conversation parts using GPT-4o Mini
- Summary evolution logged for monitoring and debugging
- Handles 30+ round conversations efficiently

## Key Files and Relationships

- `config.py` → Central configuration and model selection
- `app.py` → API endpoints and session management
- `conversation.py` → LangChain integration and conversation logic
- `database_service.py` → Planned Supabase integration (not fully connected)
- `memory-bank/` → Project documentation and context files
- `release_notes/deployment_log.md` → Change tracking
- `integration documentation/` → Frontend integration specifications

## Development Patterns

### Model Management
- Fine-tuned models available in AVAILABLE_MODELS dictionary
- Current active model: `gpt41mini_hyper2` with enhanced emotional intelligence
- Easy model switching by updating MODEL_NAME in config.py
- Document model changes in deployment_log.md

### Testing Strategy
- `test_conversation_flow.py` is the gold standard for complex flow testing
- Uses pre-recorded audio files in `mockup_audio/` for realistic testing
- Essential for verifying state-dependent conversation logic
- Always test wrap-up confirmation sequences thoroughly

### Database Integration Status
- Supabase chosen for persistent storage
- `database_service.py` exists but not fully integrated
- Migration from in-memory to database storage is high priority
- Session data structure already database-ready

### Data Export System
- `data_export/` folder contains conversation export tools
- `export_conversations.py` exports Supabase conversations to JSONL format for evaluation
- Supports filtering by date, rating, status, and message count
- Output format matches OpenAI API structure for training/evaluation
- `test_export.py` validates export functionality

### Security Notes
- Never commit API keys to repository
- OpenAI API key required in environment or config.json
- Audio files automatically cleaned up from temp_audio/
- Debug info shows API key status without exposing actual keys

## Memory Bank Maintenance

The `memory-bank/` directory contains critical project documentation:
- `projectbrief.md` - Project overview and goals
- `productContext.md` - Product requirements and features
- `systemPatterns.md` - Architecture patterns and decisions
- `techContext.md` - Technical implementation details
- `activeContext.md` - Current development context
- `progress.md` - Development progress tracking

Always update these files when making significant changes, especially `activeContext.md` and `progress.md`.