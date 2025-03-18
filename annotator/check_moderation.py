import json
import requests
import os
from pathlib import Path

def check_content_moderation(text):
    """Check content using OpenAI's moderation API"""
    url = "https://api.openai.com/v1/moderations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    
    try:
        response = requests.post(url, headers=headers, json={"input": text})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling moderation API: {e}")
        return None

def analyze_dpo_file(file_path):
    """Analyze DPO file content for moderation issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\nAnalyzing file: {file_path}")
        print("-" * 80)
        
        for i, line in enumerate(lines, 1):
            try:
                data = json.loads(line)
                
                # Check messages in input
                for msg in data['input']['messages']:
                    content = msg['content']
                    result = check_content_moderation(content)
                    
                    if result and result['results'][0]['flagged']:
                        print(f"\nLine {i} - Message Content Flagged:")
                        print(f"Content: {content[:200]}...")
                        print("\nFlags:")
                        for category, flagged in result['results'][0]['categories'].items():
                            if flagged:
                                print(f"- {category}")
                        print("-" * 80)
                
                # Check preferred and non-preferred outputs
                for output_type in ['preferred_output', 'non_preferred_output']:
                    if output_type in data:
                        for response in data[output_type]:
                            content = response['content']
                            result = check_content_moderation(content)
                            
                            if result and result['results'][0]['flagged']:
                                print(f"\nLine {i} - {output_type} Flagged:")
                                print(f"Content: {content[:200]}...")
                                print("\nFlags:")
                                for category, flagged in result['results'][0]['categories'].items():
                                    if flagged:
                                        print(f"- {category}")
                                print("-" * 80)
                
            except json.JSONDecodeError:
                print(f"Error parsing JSON at line {i}")
                continue
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OPENAI_API_KEY environment variable")
        exit(1)
        
    # Get the directory of the current script
    current_dir = Path(__file__).parent
    dpo_file = current_dir / 'dpo.jsonl'
    
    analyze_dpo_file(dpo_file) 