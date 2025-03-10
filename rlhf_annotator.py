import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
import re
import shutil

class RLHFAnnotator:
    """
    A tool for annotating conversation logs for Reinforcement Learning from Human Feedback (RLHF).
    
    This tool:
    1. Reads conversation logs from files
    2. Displays one round of conversation at a time
    3. Allows marking responses as good, neutral, or bad (with preferred alternative)
    4. Exports annotated data in DPO format
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("RLHF Annotation Tool")
        
        # Set fixed window size that fits all components
        self.root.geometry("800x700")
        
        # State variables
        self.conversations = []
        self.current_index = 0
        self.annotated_data = []
        
        # Path for auto-export (kept in the code but not displayed)
        self.auto_export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           f"rlhf_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Create a custom style for buttons
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        
        # Create custom styles for colored buttons that maintain text visibility
        self.style.map("Green.TButton",
                      foreground=[('active', 'black'), ('!active', 'black')],
                      background=[('active', '#90EE90'), ('!active', '#90EE90')])
        
        # Create the UI
        self.create_ui()
        
        # Default log directory
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversation_logs")
        
        # Auto-load logs if directory exists
        if os.path.exists(self.log_dir):
            self.load_logs_from_directory(self.log_dir)
    
    def create_ui(self):
        """Create the user interface."""
        # Main frame with minimal padding
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons at the top with reduced padding
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Button(control_frame, text="Open Log File", command=self.open_log_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(control_frame, text="Open Log Directory", command=self.open_log_directory).pack(side=tk.LEFT, padx=3)
        ttk.Button(control_frame, text="Export Annotated Data", command=self.export_data).pack(side=tk.LEFT, padx=3)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.RIGHT, padx=3)
        
        # Progress indicator with reduced padding
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=2)
        
        self.progress_var = tk.StringVar(value="")
        ttk.Label(progress_frame, textvariable=self.progress_var, 
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=3)
        
        # Conversation display area - LARGER HEIGHT
        self.conversation_frame = ttk.LabelFrame(main_frame, text="Conversation", padding=5)
        self.conversation_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Conversation ID and navigation info
        self.conversation_info_var = tk.StringVar(value="No conversations loaded")
        ttk.Label(self.conversation_frame, textvariable=self.conversation_info_var).pack(anchor=tk.W)
        
        # Scrollable conversation display
        conversation_scroll = ttk.Scrollbar(self.conversation_frame)
        conversation_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.conversation_display = tk.Text(self.conversation_frame, wrap=tk.WORD, height=10, 
                                           yscrollcommand=conversation_scroll.set)
        self.conversation_display.pack(fill=tk.BOTH, expand=True, pady=2)
        conversation_scroll.config(command=self.conversation_display.yview)
        
        # Configure tags for styling
        self.conversation_display.tag_configure("user", background="#e1f5fe")
        self.conversation_display.tag_configure("assistant", background="#f1f8e9")
        self.conversation_display.config(state=tk.DISABLED)
        
        # Annotation form with reduced padding
        annotation_frame = ttk.LabelFrame(main_frame, text="Annotation", padding=5)
        annotation_frame.pack(fill=tk.BOTH, pady=2)
        
        # Quality assessment
        ttk.Label(annotation_frame, text="Is this conversation good?").pack(anchor=tk.W)
        
        # Button frame with reduced padding
        button_frame = ttk.Frame(annotation_frame)
        button_frame.pack(fill=tk.X, pady=2)
        
        # Create annotation buttons with custom style and equal width
        self.yes_button = ttk.Button(button_frame, text="Yes (Good)", 
                                   command=lambda: self.save_annotation("good"), width=15)
        self.yes_button.pack(side=tk.LEFT, padx=3, pady=2)
        
        self.normal_button = ttk.Button(button_frame, text="Normal (Neutral)", 
                                      command=lambda: self.save_annotation("neutral"), width=15)
        self.normal_button.pack(side=tk.LEFT, padx=3, pady=2)
        
        self.no_button = ttk.Button(button_frame, text="No (Needs Improvement)", 
                                  command=lambda: self.save_annotation("bad"), width=20)
        self.no_button.pack(side=tk.LEFT, padx=3, pady=2)
        
        # Alternative response
        ttk.Label(annotation_frame, text="Better Response (only needed for 'No' option):").pack(anchor=tk.W, pady=(2, 0))
        
        self.alternative_response = tk.Text(annotation_frame, wrap=tk.WORD, height=3)
        self.alternative_response.pack(fill=tk.X, pady=2)
        
        # Feedback notes
        ttk.Label(annotation_frame, text="Feedback Notes:").pack(anchor=tk.W, pady=(2, 0))
        
        self.feedback = tk.Text(annotation_frame, wrap=tk.WORD, height=2)
        self.feedback.pack(fill=tk.X, pady=2)
        
        # Navigation controls directly below feedback section
        nav_frame = ttk.Frame(annotation_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        # Navigation buttons with same style as other buttons
        self.prev_button = ttk.Button(nav_frame, text="← Previous", 
                                    command=self.previous_conversation, width=15)
        self.prev_button.pack(side=tk.LEFT, padx=3, pady=2)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", 
                                    command=self.next_conversation, width=15)
        self.next_button.pack(side=tk.LEFT, padx=3, pady=2)
    
    def open_log_file(self):
        """Open a single log file."""
        file_path = filedialog.askopenfilename(
            title="Select Log File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir=self.log_dir if os.path.exists(self.log_dir) else "."
        )
        
        if file_path:
            self.load_log_file(file_path)
    
    def open_log_directory(self):
        """Open a directory of log files."""
        dir_path = filedialog.askdirectory(
            title="Select Log Directory",
            initialdir=self.log_dir if os.path.exists(self.log_dir) else "."
        )
        
        if dir_path:
            self.load_logs_from_directory(dir_path)
    
    def load_logs_from_directory(self, dir_path):
        """Load all log files from a directory."""
        log_files = [f for f in os.listdir(dir_path) if f.endswith('.txt') and f.startswith('conversation_')]
        
        if not log_files:
            self.status_var.set(f"No log files found in {dir_path}")
            return
        
        self.conversations = []
        for file_name in log_files:
            file_path = os.path.join(dir_path, file_name)
            self.load_log_file(file_path, append=True)
        
        self.status_var.set(f"Loaded {len(self.conversations)} exchanges from {len(log_files)} files")
        self.current_index = 0
        self.display_current_conversation()
    
    def load_log_file(self, file_path, append=False):
        """Load a single log file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the conversation
            conversation_id = os.path.basename(file_path).replace('conversation_', '').replace('.txt', '')
            exchanges = self.parse_conversation_log(content)
            
            if not append:
                self.conversations = []
            
            if exchanges:
                # Split into individual exchanges instead of grouping by conversation
                for i, exchange in enumerate(exchanges):
                    self.conversations.append({
                        'id': f"{conversation_id}_{i}",
                        'file_path': file_path,
                        'user': exchange['user'],
                        'assistant': exchange['assistant'],
                        'is_annotated': False,
                        'annotation': None,  # Track which annotation was selected
                        'alternative': "",   # Store alternative response
                        'feedback': ""       # Store feedback
                    })
                
                if not append:
                    self.status_var.set(f"Loaded {len(exchanges)} exchanges from {file_path}")
                    self.current_index = 0
                    self.display_current_conversation()
        except Exception as e:
            self.status_var.set(f"Error loading {file_path}: {str(e)}")
    
    def parse_conversation_log(self, content):
        """Parse the conversation log content."""
        # Split by the separator line
        sections = content.split('-' * 50)
        
        exchanges = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Extract user and coach messages
            user_match = re.search(r'User: (.*?)(?=\nCoach:|$)', section, re.DOTALL)
            coach_match = re.search(r'Coach: (.*?)$', section, re.DOTALL)
            
            if user_match and coach_match:
                user_message = user_match.group(1).strip()
                coach_message = coach_match.group(1).strip()
                
                exchanges.append({
                    'user': user_message,
                    'assistant': coach_message
                })
        
        return exchanges
    
    def display_current_conversation(self):
        """Display the current conversation."""
        if not self.conversations or self.current_index >= len(self.conversations):
            self.conversation_info_var.set("No conversations to display")
            self.conversation_display.config(state=tk.NORMAL)
            self.conversation_display.delete(1.0, tk.END)
            self.conversation_display.config(state=tk.DISABLED)
            
            # Clear and disable annotation fields
            self.alternative_response.config(state=tk.NORMAL)
            self.alternative_response.delete(1.0, tk.END)
            self.alternative_response.config(state=tk.DISABLED)
            
            self.feedback.config(state=tk.NORMAL)
            self.feedback.delete(1.0, tk.END)
            self.feedback.config(state=tk.DISABLED)
            
            # Reset button styles
            self._reset_button_styles()
            
            # Update navigation buttons
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            return
        
        conversation = self.conversations[self.current_index]
        self.conversation_info_var.set(f"Exchange {self.current_index + 1}/{len(self.conversations)} (ID: {conversation['id']})")
        
        # Clear and update the display
        self.conversation_display.config(state=tk.NORMAL)
        self.conversation_display.delete(1.0, tk.END)
        
        # Display a single turn of conversation
        self.conversation_display.insert(tk.END, f"User: {conversation['user']}\n", "user")
        self.conversation_display.insert(tk.END, f"\nAssistant: {conversation['assistant']}\n\n", "assistant")
        
        self.conversation_display.config(state=tk.DISABLED)
        
        # Enable and clear annotation fields
        self.alternative_response.config(state=tk.NORMAL)
        self.alternative_response.delete(1.0, tk.END)
        
        self.feedback.config(state=tk.NORMAL)
        self.feedback.delete(1.0, tk.END)
        
        # Reset button styles before potentially highlighting selected button
        self._reset_button_styles()
        
        # If this conversation was already annotated, populate the fields and highlight the button
        if conversation['is_annotated'] and conversation['annotation']:
            # Restore previous inputs based on what's stored in the conversation
            if conversation['alternative']:
                self.alternative_response.delete(1.0, tk.END)
                self.alternative_response.insert(tk.END, conversation['alternative'])
            
            if conversation['feedback']:
                self.feedback.delete(1.0, tk.END)
                self.feedback.insert(tk.END, conversation['feedback'])
            
            # Highlight the previously selected button
            if conversation['annotation'] == 'good':
                self.yes_button.configure(style='Green.TButton')
            elif conversation['annotation'] == 'neutral':
                self.normal_button.configure(style='Green.TButton')
            elif conversation['annotation'] == 'bad':
                self.no_button.configure(style='Green.TButton')
        
        # Update navigation button states
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        
        # Next button is enabled only if current conversation is annotated or we're at the end
        next_state = tk.NORMAL if conversation['is_annotated'] or self.current_index >= len(self.conversations) - 1 else tk.DISABLED
        self.next_button.config(state=next_state)
    
    def _reset_button_styles(self):
        """Reset all annotation button styles to default."""
        self.yes_button.configure(style='TButton')
        self.normal_button.configure(style='TButton')
        self.no_button.configure(style='TButton')
    
    def _save_current_inputs(self):
        """Save any changes to the current conversation without changing annotation status."""
        if not self.conversations or self.current_index >= len(self.conversations):
            return
            
        conversation = self.conversations[self.current_index]
        
        # Save the current text inputs
        conversation['alternative'] = self.alternative_response.get(1.0, tk.END).strip()
        conversation['feedback'] = self.feedback.get(1.0, tk.END).strip()
    
    def _validate_better_response_usage(self):
        """Validate that Better Response is only used with 'No' annotation."""
        # Get the current better response text
        alternative = self.alternative_response.get(1.0, tk.END).strip()
        
        # If there's text in the better response field
        if alternative:
            # Check if the current conversation is annotated
            if self.conversations[self.current_index]['is_annotated']:
                # If it's annotated but not as 'bad', show warning
                if self.conversations[self.current_index]['annotation'] != 'bad':
                    messagebox.showwarning(
                        "Invalid Combination", 
                        "You've entered text in the 'Better Response' field, but selected an option other than 'No'.\n\n"
                        "The 'Better Response' field should only be used with the 'No (Needs Improvement)' option.\n\n"
                        "Please either:\n"
                        "- Clear the Better Response field, or\n"
                        "- Change your annotation to 'No'"
                    )
                    return False
            else:
                # If not annotated yet, just inform the user
                messagebox.showinfo(
                    "Better Response Note", 
                    "You've entered text in the 'Better Response' field.\n\n"
                    "Please note that this field should only be used with the 'No (Needs Improvement)' option."
                )
                # Don't block navigation in this case since they haven't made a choice yet
        # Check if the conversation is annotated as 'bad' but has no alternative
        elif self.conversations[self.current_index]['is_annotated'] and self.conversations[self.current_index]['annotation'] == 'bad':
            messagebox.showwarning(
                "Alternative Required", 
                "You've selected 'No (Needs Improvement)' but haven't provided a better alternative response.\n\n"
                "Please provide a better alternative response when selecting 'No'."
            )
            return False
        
        return True
    
    def save_annotation(self, rating):
        """Save the annotation for the current conversation."""
        if not self.conversations or self.current_index >= len(self.conversations):
            return
        
        conversation = self.conversations[self.current_index]
        
        # Get the alternative response
        alternative = self.alternative_response.get(1.0, tk.END).strip()
        
        # Check if user entered alternative response but selected Yes or Normal
        if alternative and rating != "bad":
            messagebox.showwarning(
                "Invalid Combination", 
                "You've entered text in the 'Better Response' field, but selected '{}' instead of 'No'.\n\n"
                "The 'Better Response' field should only be used with the 'No (Needs Improvement)' option.\n\n"
                "Please either:\n"
                "- Clear the Better Response field, or\n"
                "- Change your annotation to 'No'".format(
                    "Yes" if rating == "good" else "Normal"
                )
            )
            return  # Don't proceed with saving
        
        # If marking as bad, require an alternative
        if rating == "bad" and not alternative:
            messagebox.showwarning("Alternative Required", 
                                  "Please provide a better alternative response when selecting 'No'.")
            return
        
        # Get feedback
        feedback = self.feedback.get(1.0, tk.END).strip()
        
        # Store the annotation data in the conversation object
        conversation['is_annotated'] = True
        conversation['annotation'] = rating
        conversation['alternative'] = alternative
        conversation['feedback'] = feedback
        
        # Format in DPO structure
        if rating == "bad":
            # Only create DPO item for "bad" ratings with alternatives
            dpo_item = {
                'input': {
                    'messages': [{
                        'role': 'user',
                        'content': conversation['user']
                    }],
                    'tools': [],
                    'parallel_tool_calls': True
                },
                'preferred_output': [{
                    'role': 'assistant',
                    'content': alternative
                }],
                'non_preferred_output': [{
                    'role': 'assistant',
                    'content': conversation['assistant']
                }],
                'metadata': {
                    'conversation_id': conversation['id'],
                    'file_path': conversation['file_path'],
                    'feedback': feedback,
                    'rating': rating,
                    'annotation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # Add to data for export
            self.annotated_data.append(dpo_item)
        
        # Highlight the selected button
        self._reset_button_styles()
        if rating == "good":
            self.yes_button.configure(style='Green.TButton')
        elif rating == "neutral":
            self.normal_button.configure(style='Green.TButton')
        elif rating == "bad":
            self.no_button.configure(style='Green.TButton')
        
        self.status_var.set(f"Annotated {self.current_index + 1}/{len(self.conversations)} exchanges")
        
        # Move to next conversation
        self.next_conversation()
    
    def previous_conversation(self):
        """Go to the previous conversation."""
        if not self.conversations or self.current_index <= 0:
            return
            
        # First validate the current state
        if not self._validate_better_response_usage():
            return
            
        # Save any changes to current conversation
        self._save_current_inputs()
        
        self.current_index -= 1
        self.display_current_conversation()
    
    def next_conversation(self):
        """Go to the next conversation but only if current is annotated."""
        if not self.conversations or self.current_index >= len(self.conversations):
            return
            
        # First validate the current state
        if not self._validate_better_response_usage():
            return
            
        # Save any changes to current conversation
        self._save_current_inputs()
            
        # Check if current conversation is annotated
        current_conversation = self.conversations[self.current_index]
        if not current_conversation['is_annotated']:
            messagebox.showinfo(
                "Annotation Required", 
                "Please annotate this conversation before moving to the next one.\n\n"
                "Your feedback is valuable and helps improve the system. Thank you for your contribution!"
            )
            return
            
        # Move to the next conversation if annotated
        if self.current_index < len(self.conversations) - 1:
            self.current_index += 1
            self.display_current_conversation()
        else:
            self.status_var.set("Reached the end of conversations")
            messagebox.showinfo("Complete", "You have reached the end of all conversations.")
    
    def export_data(self):
        """Manually export the annotated data."""
        if not self.annotated_data:
            messagebox.showinfo("No Data", "No annotated data to export.")
            return
        
        # Get unique log files in the annotated data
        log_files = set()
        for item in self.annotated_data:
            if 'metadata' in item and 'file_path' in item['metadata']:
                log_files.add(item['metadata']['file_path'])
        
        if not log_files:
            messagebox.showinfo("No Source Files", "Could not determine source files for export.")
            return
        
        # Create a base export directory in the same location as the script
        base_export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rlhf_exports")
        os.makedirs(base_export_dir, exist_ok=True)
        
        # Create a timestamp for the export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Collect all supervised learning data
        all_supervised_data = []
        
        # Collect all feedback for the notes file
        all_feedback = []
        
        # Process each log file
        for log_file_path in log_files:
            if not os.path.exists(log_file_path):
                continue
            
            # Get the log file name without extension to use as folder name
            log_file_name = os.path.basename(log_file_path)
            folder_name = log_file_name.replace('.txt', '')
            
            # Create a folder for this conversation
            export_dir = os.path.join(base_export_dir, f"{folder_name}_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)
            
            # Copy the original log file to the export directory
            destination = os.path.join(export_dir, log_file_name)
            shutil.copy2(log_file_path, destination)
            
            # Filter annotations for this log file
            file_annotations = []
            
            # Get all conversations for this file
            file_conversations = [conv for conv in self.conversations if conv['file_path'] == log_file_path and conv['is_annotated']]
            
            # Sort conversations by their ID to maintain the original order
            file_conversations.sort(key=lambda x: x['id'])
            
            # Create a single supervised learning item with all exchanges
            if file_conversations:
                # Build a multi-turn conversation
                messages = []
                
                # Create human-readable annotated log
                human_readable_log = []
                human_readable_log.append(f"ANNOTATED CONVERSATION LOG: {log_file_name}")
                human_readable_log.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                human_readable_log.append("=" * 80)
                human_readable_log.append("")
                
                # Collect feedback from this file
                file_feedback = []
                
                for i, conversation in enumerate(file_conversations):
                    # Add user message
                    messages.append({
                        "role": "user",
                        "content": conversation['user']
                    })
                    
                    # Add assistant message with weight
                    weight = 1 if conversation['annotation'] == 'good' else 0
                    messages.append({
                        "role": "assistant",
                        "content": conversation['assistant'],
                        "weight": weight
                    })
                    
                    # Add to human-readable log
                    human_readable_log.append(f"EXCHANGE #{i+1}")
                    human_readable_log.append("-" * 80)
                    human_readable_log.append(f"USER: {conversation['user']}")
                    human_readable_log.append("")
                    human_readable_log.append(f"ASSISTANT: {conversation['assistant']}")
                    human_readable_log.append("")
                    
                    rating_text = "Yes (Good)" if conversation['annotation'] == 'good' else "Normal" if conversation['annotation'] == 'neutral' else "No (Needs Improvement)"
                    human_readable_log.append(f"RATING: {rating_text} [weight={weight}]")
                    
                    if conversation['feedback']:
                        human_readable_log.append(f"FEEDBACK: {conversation['feedback']}")
                        # Add to feedback collections
                        file_feedback.append(f"Exchange #{i+1}: {conversation['feedback']}")
                        all_feedback.append(f"File: {log_file_name}, Exchange #{i+1}: {conversation['feedback']}")
                    
                    if conversation['alternative']:
                        human_readable_log.append(f"BETTER RESPONSE: {conversation['alternative']}")
                    
                    human_readable_log.append("")
                    human_readable_log.append("-" * 80)
                    human_readable_log.append("")
                
                # Create the supervised learning item with all messages
                if messages:
                    supervised_item = {
                        "messages": messages
                    }
                    all_supervised_data.append(supervised_item)
                    
                    # Export the supervised learning data to JSON for this file
                    supervised_file_path = os.path.join(export_dir, f"supervised_{timestamp}.json")
                    with open(supervised_file_path, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(supervised_item, ensure_ascii=False, indent=2))
                
                # Export the human-readable log
                human_readable_path = os.path.join(export_dir, f"annotated_conversation_{timestamp}.txt")
                with open(human_readable_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(human_readable_log))
                
                # Export the feedback notes for this file
                if file_feedback:
                    feedback_path = os.path.join(export_dir, f"feedback_notes_{timestamp}.txt")
                    with open(feedback_path, 'w', encoding='utf-8') as f:
                        f.write('\n\n'.join(file_feedback))
            
            # Create DPO format items for bad ratings
            for conversation in file_conversations:
                if conversation['annotation'] == 'bad' and conversation['alternative']:
                    dpo_item = {
                        'input': {
                            'messages': [{
                                'role': 'user',
                                'content': conversation['user']
                            }],
                            'tools': [],
                            'parallel_tool_calls': True
                        },
                        'preferred_output': [{
                            'role': 'assistant',
                            'content': conversation['alternative']
                        }],
                        'non_preferred_output': [{
                            'role': 'assistant',
                            'content': conversation['assistant']
                        }]
                    }
                    file_annotations.append(dpo_item)
            
            # Export the DPO annotations to JSON
            if file_annotations:
                dpo_file_path = os.path.join(export_dir, f"dpo_{timestamp}.json")
                with open(dpo_file_path, 'w', encoding='utf-8') as f:
                    json.dump(file_annotations, f, indent=2, ensure_ascii=False)
        
        # Create combined export with all supervised data
        if all_supervised_data:
            combined_supervised_path = os.path.join(base_export_dir, f"all_supervised_{timestamp}.json")
            with open(combined_supervised_path, 'w', encoding='utf-8') as f:
                for item in all_supervised_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Also create a combined DPO export
        all_dpo_data = []
        for item in self.annotated_data:
            if 'preferred_output' in item and 'non_preferred_output' in item:
                dpo_item = {
                    'input': item['input'],
                    'preferred_output': item['preferred_output'],
                    'non_preferred_output': item['non_preferred_output']
                }
                all_dpo_data.append(dpo_item)
        
        if all_dpo_data:
            combined_dpo_path = os.path.join(base_export_dir, f"all_dpo_{timestamp}.json")
            with open(combined_dpo_path, 'w', encoding='utf-8') as f:
                json.dump(all_dpo_data, f, indent=2, ensure_ascii=False)
        
        # Export all feedback notes to a single file
        if all_feedback:
            all_feedback_path = os.path.join(base_export_dir, f"all_feedback_{timestamp}.txt")
            with open(all_feedback_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(all_feedback))
        
        self.status_var.set(f"Exported annotations to {base_export_dir}")
        messagebox.showinfo(
            "Export Complete", 
            f"Successfully exported annotations to separate folders in:\n{base_export_dir}\n\n"
            f"Total supervised conversations: {len(all_supervised_data)}\n"
            f"Total DPO examples: {len(all_dpo_data)}\n"
            f"Total feedback entries: {len(all_feedback)}"
        )

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = RLHFAnnotator(root)
    root.mainloop()

if __name__ == "__main__":
    main() 