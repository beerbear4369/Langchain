#!/usr/bin/env python3
"""
Export conversation history from Supabase in multiple formats
Usage: python export_conversations.py [options]

Supported formats:
- full: Complete conversation as single training example (JSONL)
- turn-by-turn: Each user-AI exchange as separate example (JSONL) 
- txt: Human-readable format for annotation (TXT)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_service import db_service
from config import SYSTEM_PROMPT


def get_system_prompt_with_round(round_num: int = 1, max_rounds: int = 30) -> str:
    """Generate system prompt with current round information"""
    # Extract the base system prompt and add round information
    base_prompt = SYSTEM_PROMPT.strip()
    
    # Add round information at the end
    round_info = f"\n\nCurrent conversation round: {round_num}/{max_rounds}"
    
    return base_prompt + round_info


def format_conversation_for_evaluation(session_data: Dict[str, Any], messages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Convert a conversation from Supabase format to evaluation JSONL format
    
    Args:
        session_data: Session information from Supabase
        messages: List of messages from Supabase
    
    Returns:
        Dict formatted for evaluation or None if conversation is too short
    """
    if len(messages) < 2:  # Need at least user message and AI response
        return None
    
    # Sort messages by creation time
    messages.sort(key=lambda x: x['created_at'])
    
    # Build conversation history
    conversation_messages = []
    
    # Add system prompt (use round count from session or estimate from messages)
    round_count = session_data.get('message_count', len(messages) // 2)
    system_prompt = get_system_prompt_with_round(round_count)
    
    conversation_messages.append({
        "role": "system",
        "text": system_prompt,
        "name": None,
        "tool_calls": None,
        "function_call": None,
        "tool_call_id": None,
        "refusal": None,
        "finish_reason": None
    })
    
    # Add conversation messages
    for msg in messages[:-1]:  # All except the last message
        role = "user" if msg['sender'] == 'user' else "assistant"
        conversation_messages.append({
            "role": role,
            "text": msg['text_content'],
            "name": None,
            "tool_calls": None,
            "function_call": None,
            "tool_call_id": None,
            "refusal": None,
            "finish_reason": None
        })
    
    # The last message should be an AI response for the output
    last_message = messages[-1]
    if last_message['sender'] != 'ai':
        # If last message is from user, we can't use this for evaluation
        return None
    
    # Create the evaluation format
    evaluation_data = {
        "input": conversation_messages,
        "output": {
            "model": "ft:gpt-4.1-mini-2025-04-14:kuku-tech:coach-prompt10-purevetted49-basemodel-outofshell-parachange2:Bj66Dtia",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": last_message['text_content'],
                    "refusal": None,
                    "tool_calls": None,
                    "function_call": None
                },
                "finish_reason": "stop"
            }]
        }
    }
    
    return evaluation_data


def format_conversation_for_annotation(session_data: Dict[str, Any], messages: List[Dict[str, Any]]) -> Optional[str]:
    """
    Convert a conversation from Supabase format to text format for annotation
    
    Args:
        session_data: Session information from Supabase
        messages: List of messages from Supabase
    
    Returns:
        String formatted for annotation or None if conversation is too short
    """
    if len(messages) < 2:  # Need at least user message and AI response
        return None
    
    # Sort messages by creation time
    messages.sort(key=lambda x: x['created_at'])
    
    # Build conversation text
    conversation_lines = []
    
    for i, msg in enumerate(messages):
        if msg['sender'] == 'user':
            conversation_lines.append(f"User: {msg['text_content']}")
        else:
            conversation_lines.append(f"Coach: {msg['text_content']}")
        
        # Add separator after each exchange (except the last one)
        if i < len(messages) - 1:
            conversation_lines.append("--------------------------------------------------")
    
    # Add session summary if available
    if session_data.get('summary'):
        conversation_lines.append("--------------------------------------------------")
        conversation_lines.append("")
        conversation_lines.append("FINAL SUMMARY AND ACTION PLAN")
        conversation_lines.append("==================================================")
        conversation_lines.append("")
        conversation_lines.append(session_data['summary'])
    
    return '\n'.join(conversation_lines) + '\n'


def format_conversation_turn_by_turn(session_data: Dict[str, Any], messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a conversation from Supabase format to turn-by-turn JSONL format for OpenAI evaluation
    
    Args:
        session_data: Session information from Supabase  
        messages: List of messages from Supabase
    
    Returns:
        List of turn examples or empty list if conversation is too short
    """
    if len(messages) < 2:  # Need at least user message and AI response
        return []
    
    # Sort messages by creation time
    messages.sort(key=lambda x: x['created_at'])
    
    # Get system prompt
    round_count = session_data.get('message_count', len(messages) // 2)
    system_prompt = get_system_prompt_with_round(round_count)
    
    turn_examples = []
    conversation_history = [{"role": "system", "content": system_prompt}]
    
    # Process messages in pairs (user -> AI)
    for i in range(0, len(messages) - 1, 2):
        if i + 1 >= len(messages):
            break
            
        user_msg = messages[i]
        ai_msg = messages[i + 1]
        
        # Skip if not a proper user->AI pair
        if user_msg['sender'] != 'user' or ai_msg['sender'] != 'ai':
            continue
        
        # Add user message to history for this turn
        current_input = conversation_history + [{"role": "user", "content": user_msg['text_content']}]
        
        # Create turn example
        turn_example = {
            "input": current_input,
            "output": ai_msg['text_content']
        }
        turn_examples.append(turn_example)
        
        # Update conversation history for next turn
        conversation_history.append({"role": "user", "content": user_msg['text_content']})
        conversation_history.append({"role": "assistant", "content": ai_msg['text_content']})
    
    return turn_examples


def export_conversations(
    output_file: str,
    format_type: str = "full",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session_ids: Optional[List[str]] = None,
    min_rating: Optional[int] = None,
    status: Optional[str] = None,
    min_messages: int = 4
) -> None:
    """
    Export conversations from Supabase in multiple formats
    
    Args:
        output_file: Path to output file
        format_type: Export format ('full', 'turn-by-turn', 'txt')
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        session_ids: List of specific session IDs to export
        min_rating: Minimum session rating filter
        status: Session status filter ('active' or 'ended')
        min_messages: Minimum number of messages required
    """
    try:
        print("🔍 Fetching sessions from Supabase...")
        
        # Get all sessions first
        all_sessions = db_service.debug_get_all_sessions()
        
        if not all_sessions:
            print("❌ No sessions found in database")
            return
        
        print(f"📊 Found {len(all_sessions)} total sessions")
        
        # Apply filters
        filtered_sessions = []
        
        for session in all_sessions:
            # Filter by session IDs
            if session_ids and session['session_id'] not in session_ids:
                continue
            
            # Filter by status
            if status and session['status'] != status:
                continue
            
            # Filter by rating
            if min_rating and (not session.get('rating') or session['rating'] < min_rating):
                continue
            
            # Filter by date range
            if start_date:
                session_date = datetime.fromisoformat(session['created_at'].replace('Z', '+00:00'))
                start_dt = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
                if session_date < start_dt:
                    continue
            
            if end_date:
                session_date = datetime.fromisoformat(session['created_at'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
                if session_date > end_dt:
                    continue
            
            filtered_sessions.append(session)
        
        print(f"📋 {len(filtered_sessions)} sessions match filters")
        
        # Export conversations
        exported_count = 0
        skipped_count = 0
        total_examples = 0  # For turn-by-turn format
        created_files = []  # For TXT format file tracking
        
        # Handle TXT format differently (separate files per session)
        if format_type == "txt":
            for session in filtered_sessions:
                session_id = session['session_id']
                print(f"🔄 Processing session: {session_id}")
                
                # Get conversation history
                messages = db_service.get_conversation_history(session_id)
                
                if len(messages) < min_messages:
                    print(f"⏭️  Skipping {session_id}: only {len(messages)} messages (min: {min_messages})")
                    skipped_count += 1
                    continue
                
                # Generate individual filename for this session
                individual_filename = generate_txt_filename(output_file, session_id)
                
                # Text format for annotation - individual file
                formatted_text = format_conversation_for_annotation(session, messages)
                if formatted_text:
                    with open(individual_filename, 'w', encoding='utf-8') as session_file:
                        session_file.write(formatted_text)
                    created_files.append(individual_filename)
                    exported_count += 1
                    print(f"✅ Exported {session_id} ({len(messages)} messages) → {individual_filename}")
                else:
                    print(f"⏭️  Skipped {session_id}: couldn't format for annotation")
                    skipped_count += 1
        
        else:
            # Handle JSONL formats (full and turn-by-turn) - single file
            with open(output_file, 'w', encoding='utf-8') as f:
                for session in filtered_sessions:
                    session_id = session['session_id']
                    print(f"🔄 Processing session: {session_id}")
                    
                    # Get conversation history
                    messages = db_service.get_conversation_history(session_id)
                    
                    if len(messages) < min_messages:
                        print(f"⏭️  Skipping {session_id}: only {len(messages)} messages (min: {min_messages})")
                        skipped_count += 1
                        continue
                    
                    # Format based on requested format type
                    if format_type == "full":
                        # Full conversation format (existing)
                        formatted_data = format_conversation_for_evaluation(session, messages)
                        if formatted_data:
                            f.write(json.dumps(formatted_data, ensure_ascii=False) + '\n')
                            exported_count += 1
                            print(f"✅ Exported {session_id} ({len(messages)} messages)")
                        else:
                            print(f"⏭️  Skipped {session_id}: couldn't format for evaluation")
                            skipped_count += 1
                    
                    elif format_type == "turn-by-turn":
                        # Turn-by-turn format for OpenAI evaluation
                        turn_examples = format_conversation_turn_by_turn(session, messages)
                        if turn_examples:
                            for turn_example in turn_examples:
                                f.write(json.dumps(turn_example, ensure_ascii=False) + '\n')
                            exported_count += 1
                            total_examples += len(turn_examples)
                            print(f"✅ Exported {session_id} ({len(turn_examples)} turns from {len(messages)} messages)")
                        else:
                            print(f"⏭️  Skipped {session_id}: couldn't generate turns")
                            skipped_count += 1
        
        # Print completion summary
        print(f"\n🎉 Export complete!")
        if format_type == "txt":
            print(f"📄 Exported {exported_count} conversations to {len(created_files)} separate files:")
            for filename in created_files[:5]:  # Show first 5 files
                print(f"   - {filename}")
            if len(created_files) > 5:
                print(f"   ... and {len(created_files) - 5} more files")
        elif format_type == "turn-by-turn":
            print(f"📄 Exported {exported_count} conversations ({total_examples} total turns) to {output_file}")
        else:
            print(f"📄 Exported {exported_count} conversations to {output_file}")
        print(f"⏭️  Skipped {skipped_count} conversations")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()


def generate_txt_filename(base_output_file: str, session_id: str) -> str:
    """Generate individual filename for TXT format using session ID"""
    # Split the filename into base and extension
    if base_output_file.endswith('.txt'):
        base_name = base_output_file[:-4]  # Remove .txt
        return f"{base_name}_{session_id}.txt"
    else:
        # If no .txt extension, add it
        return f"{base_output_file}_{session_id}.txt"


def detect_format_from_filename(filename: str) -> str:
    """Auto-detect format from file extension"""
    if filename.endswith('.txt'):
        return 'txt'
    elif filename.endswith('.jsonl'):
        return 'full'  # Default JSONL format
    else:
        return 'full'  # Default format


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Export conversation history from Supabase in multiple formats",
        epilog="""
Format options:
  full        Complete conversation as single training example (JSONL)
  turn-by-turn  Each user-AI exchange as separate example (JSONL)
  txt         Human-readable format for annotation (TXT)
        """
    )
    
    parser.add_argument(
        "output_file",
        help="Output file path (.jsonl or .txt)"
    )
    
    parser.add_argument(
        "--format",
        choices=["full", "turn-by-turn", "txt"],
        help="Export format (auto-detected from file extension if not specified)"
    )
    
    parser.add_argument(
        "--start-date",
        help="Start date filter (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date", 
        help="End date filter (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--session-ids",
        nargs="+",
        help="Specific session IDs to export"
    )
    
    parser.add_argument(
        "--min-rating",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Minimum session rating (1-5)"
    )
    
    parser.add_argument(
        "--status",
        choices=["active", "ended"],
        help="Session status filter"
    )
    
    parser.add_argument(
        "--min-messages",
        type=int,
        default=4,
        help="Minimum number of messages required (default: 4)"
    )
    
    parser.add_argument(
        "--recent",
        type=int,
        help="Export conversations from last N days"
    )
    
    args = parser.parse_args()
    
    # Determine format (explicit or auto-detect)
    format_type = args.format
    if not format_type:
        format_type = detect_format_from_filename(args.output_file)
        print(f"🔍 Auto-detected format: {format_type}")
    
    # Handle recent filter
    start_date = args.start_date
    if args.recent:
        start_date = (datetime.now() - timedelta(days=args.recent)).strftime('%Y-%m-%d')
        print(f"📅 Using recent filter: conversations from {start_date}")
    
    # Check if database is available
    try:
        db_service.debug_get_all_sessions()
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        print("💡 Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are set")
        sys.exit(1)
    
    # Run export
    export_conversations(
        output_file=args.output_file,
        format_type=format_type,
        start_date=start_date,
        end_date=args.end_date,
        session_ids=args.session_ids,
        min_rating=args.min_rating,
        status=args.status,
        min_messages=args.min_messages
    )


if __name__ == "__main__":
    main()