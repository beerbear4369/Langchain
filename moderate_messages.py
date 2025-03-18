import json
import os
import argparse
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def check_moderation(text):
    """
    Check if a text violates OpenAI's content policy using the moderation API.
    Returns the moderation response.
    """
    try:
        response = client.moderations.create(
            model="text-moderation-latest",  # Using the latest moderation model
            input=text
        )
        return response
    except Exception as e:
        return f"Error in moderation check: {str(e)}"

def process_jsonl_file(file_path):
    """
    Process a JSONL file and check all messages with the moderation API.
    """
    results = []
    
    # Read the JSONL file
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            try:
                # Parse JSON object
                entry = json.loads(line)
                
                # Extract messages from input
                if 'input' in entry and 'messages' in entry['input']:
                    for msg in entry['input']['messages']:
                        if 'content' in msg and msg['content']:
                            message_content = msg['content']
                            moderation_result = check_moderation(message_content)
                            
                            results.append({
                                'line_number': line_number,
                                'source': 'input',
                                'role': msg.get('role', 'unknown'),
                                'content': message_content[:100] + "..." if len(message_content) > 100 else message_content,
                                'moderation_result': moderation_result
                            })
                
                # Extract messages from preferred_output
                if 'preferred_output' in entry:
                    for msg in entry['preferred_output']:
                        if 'content' in msg and msg['content']:
                            message_content = msg['content']
                            moderation_result = check_moderation(message_content)
                            
                            results.append({
                                'line_number': line_number,
                                'source': 'preferred_output',
                                'role': msg.get('role', 'unknown'),
                                'content': message_content[:100] + "..." if len(message_content) > 100 else message_content,
                                'moderation_result': moderation_result
                            })
                
                # Extract messages from non_preferred_output
                if 'non_preferred_output' in entry:
                    for msg in entry['non_preferred_output']:
                        if 'content' in msg and msg['content']:
                            message_content = msg['content']
                            moderation_result = check_moderation(message_content)
                            
                            results.append({
                                'line_number': line_number,
                                'source': 'non_preferred_output',
                                'role': msg.get('role', 'unknown'),
                                'content': message_content[:100] + "..." if len(message_content) > 100 else message_content,
                                'moderation_result': moderation_result
                            })
            
            except json.JSONDecodeError:
                print(f"Error parsing JSON at line {line_number}")
            except Exception as e:
                print(f"Error processing line {line_number}: {str(e)}")
    
    return results

def display_results(results):
    """
    Display only the moderation results that have been flagged.
    """
    print("\n===== FLAGGED CONTENT =====\n")
    
    flagged_count = 0
    total_count = len(results)
    
    for idx, result in enumerate(results, 1):
        # Check if the message was flagged
        is_flagged = False
        flag_reason = ""
        
        if isinstance(result['moderation_result'], str):
            # If there was an error, consider it flagged for review
            is_flagged = True
            flag_reason = result['moderation_result']
        else:
            # Normal moderation result
            if hasattr(result['moderation_result'], 'results') and result['moderation_result'].results:
                first_result = result['moderation_result'].results[0]
                is_flagged = first_result.flagged
                
                if is_flagged:
                    # Get flagged categories
                    categories = {k: v for k, v in first_result.categories.model_dump().items() if v}
                    scores = {k: round(v, 4) for k, v in first_result.category_scores.model_dump().items() 
                            if v > 0.01}  # Only show significant scores
                    flag_reason = f"Categories: {categories}, Scores: {scores}"
        
        # Only display flagged content
        if is_flagged:
            flagged_count += 1
            print(f"⚠️  FLAGGED CONTENT - Message {idx} (Line {result['line_number']}):")
            print(f"Source: {result['source']}, Role: {result['role']}")
            print(f"Content: {result['content']}")
            print(f"Reason: {flag_reason}")
            
            # Option to show raw response
            if not isinstance(result['moderation_result'], str):
                try:
                    raw_response = result['moderation_result'].model_dump_json(indent=2)
                    print(f"Raw API Response:\n{raw_response}")
                except AttributeError:
                    print(f"Raw API Response: {result['moderation_result']}")
            
            print("-" * 80)
    
    print(f"\nTotal messages checked: {total_count}")
    print(f"Flagged messages: {flagged_count}")
    
    if flagged_count == 0:
        print("✅ No content was flagged by the moderation API.")

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Check JSONL file messages with OpenAI Moderation API')
    parser.add_argument('--file', '-f', type=str, default="annotator/rlhf_exports/dpo.jsonl",
                        help='Path to the JSONL file (default: annotator/rlhf_exports/dpo.jsonl)')
    
    args = parser.parse_args()
    file_path = args.file
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    print(f"Processing file: {file_path}")
    results = process_jsonl_file(file_path)
    display_results(results)

if __name__ == "__main__":
    main() 