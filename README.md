# OpenAI Moderation API Script

This script checks content in JSONL files against OpenAI's moderation API to identify potentially harmful or inappropriate content.

## Setup

1. Install the required package:
```bash
pip install openai
```

2. Set your OpenAI API key as an environment variable:
```bash
# On Windows
set OPENAI_API_KEY=your-api-key-here

# On macOS/Linux
export OPENAI_API_KEY=your-api-key-here
```

## Usage

Run the script with:
```bash
python moderate_messages.py
```

By default, the script will process the file at `annotator/rlhf_exports/dpo.jsonl`.

You can specify a different file using the `--file` or `-f` argument:
```bash
python moderate_messages.py --file path/to/your/file.jsonl
```

## Output

The script will check all messages in the JSONL file against OpenAI's moderation API and output:
- Any flagged content, with details about which categories were flagged
- A summary of the total messages checked and how many were flagged

## Customization

- To change the moderation model, modify the `model` parameter in the `check_moderation` function.
- To process a different file, change the `file_path` variable in the `main` function. 