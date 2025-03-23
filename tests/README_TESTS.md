# Test Organization

This directory contains the test files for the project. All new test scripts should be placed in this directory.

## Test File Naming Convention

- Use descriptive names that indicate what is being tested
- Prefix with `test_` to make it clear it's a test file
- Use underscores to separate words

## Creating New Test Files

When creating new test files:

1. Place them in this `tests` directory
2. Add the following import pattern to access modules from the parent directory:

```python
import os
import sys

# Add parent directory to Python path to allow imports from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the parent directory
from conversation import Conversation, safe_print  # Import what you need
```

## Test Files

### Conversation Tests

- `test_conversation_end_extended.py` - Tests for conversation end logic, including:
  - Standard wrap-up detection (25 messages with Way Forward content)
  - Closing summary generation
  - End-to-end conversation flow
  - Early wrap-up detection (strong Way Forward before 25 messages)
  - Message count only wrap-up (exceeding 25 messages without Way Forward)
  - Time-based wrap-up (30 minutes elapsed)

- `test_conversation_memory.py` - Tests for conversation memory and retention

- `test_real_conversation.py` - Tests using samples of real conversations

### Summarization Tests

- `test_summarization.py` - Tests for the summarization functionality

### Utility Tests

- `check_summary_logs.py` - Utility to check and analyze summary logs

## Running Tests

To run tests, navigate to the tests directory and run:

```bash
# Navigate to tests directory
cd tests

# Run a specific test
python test_conversation_end_extended.py

# For more detailed output
python -u test_conversation_end_extended.py
```

## Testing Guidelines

1. Keep tests focused and independent
2. Include assertions to validate results
3. Use descriptive function and variable names
4. Add comments explaining the purpose of test sections
5. Always place new test files in this directory
6. Include clear output and return values for easy validation
7. Consider edge cases and potential failure modes 