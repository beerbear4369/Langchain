# Conversation Export Tool

This tool exports conversation history from Supabase in multiple formats for different use cases:

- **Full conversation format** (JSONL): Complete conversations for training/evaluation
- **Turn-by-turn format** (JSONL): Individual exchanges for OpenAI evaluation platform  
- **Text format** (TXT): Human-readable conversations for annotation

## Setup

### Prerequisites
1. **Supabase Environment Variables** must be set:
   ```bash
   export SUPABASE_URL=https://your-project.supabase.co
   export SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

2. **Python Dependencies** (already in requirements.txt):
   ```bash
   pip install supabase python-dotenv
   ```

## Usage

### Basic Export

**Auto-detect format from file extension:**
```bash
cd data_export
python export_conversations.py conversations.txt      # Text format
python export_conversations.py output.jsonl          # Full conversation format
```

**Explicit format specification:**
```bash
python export_conversations.py output.jsonl --format full           # Full conversations
python export_conversations.py turns.jsonl --format turn-by-turn    # Turn-by-turn for evaluation
python export_conversations.py annotation.txt --format txt          # Text for annotation
```

### Filtering Options

**Export recent conversations:**
```bash
python export_conversations.py output.jsonl --recent 7
```

**Export by date range:**
```bash
python export_conversations.py output.jsonl --start-date 2025-06-01 --end-date 2025-06-15
```

**Export high-rated conversations:**
```bash
python export_conversations.py output.jsonl --min-rating 4
```

**Export completed sessions only:**
```bash
python export_conversations.py output.jsonl --status ended
```

**Export specific sessions:**
```bash
python export_conversations.py output.jsonl --session-ids session-123 session-456
```

**Require minimum conversation length:**
```bash
python export_conversations.py output.jsonl --min-messages 8
```

**Combine filters:**
```bash
python export_conversations.py output.jsonl --recent 30 --min-rating 3 --status ended --min-messages 6
```

## Output Formats

### 1. Full Conversation Format (JSONL)

Complete conversations as single training examples. One conversation per line:

```json
{
  "input": [
    {
      "role": "system",
      "text": "Act as a patient and inspiring Coach named Kuku...",
      "name": null,
      "tool_calls": null,
      "function_call": null,
      "tool_call_id": null,
      "refusal": null,
      "finish_reason": null
    },
    {
      "role": "user", 
      "text": "I want to talk about retirement.",
      "name": null,
      "tool_calls": null,
      "function_call": null,
      "tool_call_id": null,
      "refusal": null,
      "finish_reason": null
    },
    {
      "role": "assistant",
      "text": "Thank you for sharing that. What's truly important for you to discuss about retirement today?",
      "name": null,
      "tool_calls": null,
      "function_call": null,
      "tool_call_id": null,
      "refusal": null,
      "finish_reason": null
    }
  ],
  "output": {
    "model": "ft:gpt-4.1-mini-2025-04-14:kuku-tech:coach-prompt10-purevetted49-basemodel-outofshell-parachange2:Bj66Dtia",
    "choices": [{
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "That's a powerful vision of freedom and choice. How have you experienced this freedom or lack of it so far in your life?",
        "refusal": null,
        "tool_calls": null,
        "function_call": null
      },
      "finish_reason": "stop"
    }]
  }
}
```

### 2. Turn-by-Turn Format (JSONL)

Individual user-AI exchanges for OpenAI evaluation platform. Multiple examples per conversation:

```json
{"input": [{"role": "system", "content": "Act as a patient and inspiring Coach..."}, {"role": "user", "content": "I want to talk about retirement."}], "output": "Thank you for sharing that. What's truly important for you to discuss about retirement today?"}
{"input": [{"role": "system", "content": "..."}, {"role": "user", "content": "I want to talk about retirement."}, {"role": "assistant", "content": "Thank you for sharing that..."}, {"role": "user", "content": "I was born because I don't want to work."}], "output": "I hear you—there's a strong feeling about work here. Help me understand what not wanting to work means for you."}
```

### 3. Text Format (TXT)

Human-readable format for annotation. **Creates separate files per conversation** for easier annotation workflow:

**Input:** `python export_conversations.py conversations.txt --recent 7`

**Output:** Multiple files named with session IDs:
- `conversations_session-abc123.txt`
- `conversations_session-def456.txt`
- `conversations_session-ghi789.txt`

**File content format:**
```
User: I want to talk about retirement.
Coach: Thank you for sharing that. What's truly important for you to discuss about retirement today?
--------------------------------------------------
User: I was born because I don't want to work.
Coach: I hear you—there's a strong feeling about work here. Help me understand what not wanting to work means for you.
--------------------------------------------------
User: It means freedom. It means I don't have to do work if I don't want to.
Coach: That's a powerful vision of freedom and choice. How have you experienced this freedom or lack of it so far in your life?
--------------------------------------------------

FINAL SUMMARY AND ACTION PLAN
==================================================
The client explored their relationship with work and retirement...
```

## Testing

Run the test suite to verify everything works:
```bash
cd data_export
python test_export.py
```

This will:
- Test database connection
- Test message retrieval
- Test format conversion
- Test full export functionality

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `output_file` | Path to output file (.jsonl or .txt) | `conversations.txt` |
| `--format` | Export format (full/turn-by-turn/txt) | `--format turn-by-turn` |
| `--start-date` | Start date filter (YYYY-MM-DD) | `--start-date 2025-06-01` |
| `--end-date` | End date filter (YYYY-MM-DD) | `--end-date 2025-06-15` |
| `--session-ids` | Specific session IDs to export | `--session-ids session-123 session-456` |
| `--min-rating` | Minimum session rating (1-5) | `--min-rating 4` |
| `--status` | Session status (active/ended) | `--status ended` |
| `--min-messages` | Minimum messages per conversation | `--min-messages 6` |
| `--recent` | Export conversations from last N days | `--recent 7` |

## Use Cases

### 1. Model Evaluation with OpenAI Platform
Export turn-by-turn exchanges for system prompt testing:
```bash
python export_conversations.py eval_turns.jsonl --format turn-by-turn --min-rating 4 --status ended --min-messages 8
```

### 2. Training Data Collection
Export complete conversations for fine-tuning:
```bash
python export_conversations.py training_data.jsonl --format full --recent 30 --min-messages 6
```

### 3. Human Annotation
Export readable text format as separate files per session:
```bash
python export_conversations.py annotation.txt --format txt --min-rating 3 --status ended
# Creates: annotation_session-123.txt, annotation_session-456.txt, etc.
```

### 4. Quality Analysis
Export specific sessions for detailed review as individual files:
```bash
python export_conversations.py review_data.txt --format txt --session-ids session-abc123 session-def456
# Creates: review_data_session-abc123.txt, review_data_session-def456.txt
```

### 5. System Prompt Testing
Export individual turns for A/B testing different prompts:
```bash
python export_conversations.py prompt_test.jsonl --format turn-by-turn --recent 7
```

## File Structure

```
data_export/
├── export_conversations.py    # Main export script
├── test_export.py            # Test suite
└── README.md                 # This documentation
```

## Troubleshooting

### Common Issues

**"Cannot connect to database" error:**
- Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables
- Check if the service role key has proper permissions

**"No sessions found" message:**
- Verify sessions exist in the database
- Check date filters aren't too restrictive

**Empty output file:**
- Check filter criteria (may be too restrictive)
- Verify conversations meet minimum message requirements
- Ensure conversations end with AI responses

**JSON format errors:**
- Check that message content doesn't contain invalid characters
- Verify conversations have proper structure

**Import errors:**
- Make sure you're running from the `data_export` directory
- Verify parent directory contains `database_service.py` and `config.py`

### Debug Mode
Add print statements or use the test script to diagnose issues:
```bash
cd data_export
python test_export.py
```

## Data Privacy

- This script exports conversation content - ensure compliance with privacy policies
- Consider anonymizing or filtering sensitive information before exporting
- Use appropriate access controls for exported files

## Integration with Main Project

This tool integrates with the main Kuku Coach project:
- Uses `../database_service.py` for Supabase connections
- Uses `../config.py` for system prompts and configuration
- Follows the same data format as the main application
- Can be run independently without affecting the main API