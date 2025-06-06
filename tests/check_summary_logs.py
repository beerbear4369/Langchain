"""
Script to check and analyze summary logs generated by the conversation system.

This is useful for verifying that:
1. The summarization is happening at appropriate thresholds
2. The quality of summaries is good
3. The system is properly tracking conversation history
"""

import os
import glob
from datetime import datetime
import sys

# Add parent directory to path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Analyze the most recent summary log files."""
    # Find the conversation logs directory (in parent directory)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "conversation_logs")
    
    # Get the most recent summary log
    summary_logs = glob.glob(os.path.join(log_dir, "summary_*.txt"))
    
    if not summary_logs:
        print("No summary logs found. Please run the test_conversation_memory.py script first.")
        return
    
    # Sort by creation time (newest first)
    summary_logs.sort(key=os.path.getctime, reverse=True)
    most_recent_log = summary_logs[0]
    
    print(f"Analyzing most recent summary log: {most_recent_log}")
    print("-" * 80)
    
    # Read and analyze the file
    with open(most_recent_log, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count summary updates
    summary_updates = content.count("=== Summary Update at ")
    print(f"Number of summary updates: {summary_updates}")
    
    # Extract timestamps to calculate when summarization happened
    timestamps = []
    for line in content.split("\n"):
        if "=== Summary Update at " in line:
            # Extract timestamp string
            timestamp_str = line.replace("=== Summary Update at ", "").replace(" ===", "")
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamps.append(timestamp)
    
    # Calculate intervals between summarizations
    if len(timestamps) >= 2:
        print("\nTime between summarizations:")
        for i in range(1, len(timestamps)):
            delta = timestamps[i] - timestamps[i-1]
            print(f"  Update {i}: {delta.total_seconds():.2f} seconds")
    
    # Print summary progression (first 100 chars of each)
    print("\nSummary progression:")
    summaries = []
    current_summary = ""
    capture_next = False
    
    for line in content.split("\n"):
        if capture_next:
            if line.startswith("---"):  # End of summary section
                capture_next = False
                summaries.append(current_summary)
                current_summary = ""
            else:
                current_summary += line
        elif line == "New summary:":
            capture_next = True
    
    # Print the evolution of summaries
    for i, summary in enumerate(summaries, 1):
        # Print first 100 chars with ellipsis if longer
        preview = summary[:100] + ("..." if len(summary) > 100 else "")
        print(f"  Summary {i}: {preview}")
    
    print("\nAnalysis complete. Check the full summary log for more details.")

if __name__ == "__main__":
    main() 