import json
import requests
import os
from pathlib import Path
import sys

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
        
        flagged_count = 0
        total_messages = 0
        flagged_categories = {}
        
        for i, line in enumerate(lines, 1):
            try:
                data = json.loads(line)
                
                # Check messages in input
                for msg in data['input']['messages']:
                    content = msg['content']
                    total_messages += 1
                    result = check_content_moderation(content)
                    
                    if result and result['results'][0]['flagged']:
                        flagged_count += 1
                        print(f"\nLine {i} - Message Content Flagged:")
                        print(f"Content: {content[:200]}...")
                        print("\nFlags:")
                        for category, flagged in result['results'][0]['categories'].items():
                            if flagged:
                                print(f"- {category}")
                                if category in flagged_categories:
                                    flagged_categories[category] += 1
                                else:
                                    flagged_categories[category] = 1
                        print("-" * 80)
                
                # Check preferred and non-preferred outputs
                for output_type in ['preferred_output', 'non_preferred_output']:
                    if output_type in data:
                        for response in data[output_type]:
                            content = response['content']
                            total_messages += 1
                            result = check_content_moderation(content)
                            
                            if result and result['results'][0]['flagged']:
                                flagged_count += 1
                                print(f"\nLine {i} - {output_type} Flagged:")
                                print(f"Content: {content[:200]}...")
                                print("\nFlags:")
                                for category, flagged in result['results'][0]['categories'].items():
                                    if flagged:
                                        print(f"- {category}")
                                        if category in flagged_categories:
                                            flagged_categories[category] += 1
                                        else:
                                            flagged_categories[category] = 1
                                print("-" * 80)
                
            except json.JSONDecodeError:
                print(f"Error parsing JSON at line {i}")
                continue
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"ANALYSIS SUMMARY for {file_path}")
        print("=" * 80)
        print(f"Total messages analyzed: {total_messages}")
        print(f"Total flagged messages: {flagged_count} ({(flagged_count/total_messages)*100:.2f}%)")
        
        if flagged_categories:
            print("\nFlagged categories breakdown:")
            for category, count in sorted(flagged_categories.items(), key=lambda x: x[1], reverse=True):
                print(f"- {category}: {count} ({(count/flagged_count)*100:.2f}%)")
        
        print("=" * 80)
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OPENAI_API_KEY environment variable")
        exit(1)
    
    # Allow passing a file path as a command-line argument
    if len(sys.argv) > 1:
        dpo_file = Path(sys.argv[1])
    else:
        # Default to the dpo.jsonl in the annotator/rlhf_exports directory
        current_dir = Path(__file__).parent
        dpo_file = current_dir / 'annotator' / 'rlhf_exports' / 'dpo.jsonl'
    
    # Check if the file exists
    if not dpo_file.exists():
        print(f"Error: File {dpo_file} does not exist.")
        print("Available DPO files:")
        
        # List available dpo files
        annotator_dir = current_dir / 'annotator' / 'rlhf_exports'
        if annotator_dir.exists():
            dpo_files = list(annotator_dir.glob("**/*dpo*.jsonl"))
            for i, file in enumerate(dpo_files, 1):
                print(f"{i}. {file.relative_to(current_dir)}")
            
            if dpo_files:
                print("\nUsage: python check_moderation.py [path_to_dpo_file]")
            else:
                print("No DPO files found in annotator/rlhf_exports directory.")
        else:
            print(f"Directory {annotator_dir} does not exist.")
        
        exit(1)
    
    # Run the analysis
    analyze_dpo_file(dpo_file) 