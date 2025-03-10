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
                    'annotation_time': datetime.now().isoformat()
                }
            }
            
            # Add to data for export
            self.annotated_data.append(dpo_item)
            
            # Auto-export when selecting "No" with a preferred alternative
            try:
                self.auto_export()
            except Exception as e:
                messagebox.showwarning("Export Warning", f"Failed to auto-export: {str(e)}")
        
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
    
    def auto_export(self):
        """Automatically export annotated data after clicking 'No'."""
        if not self.conversations or self.current_index >= len(self.conversations):
            return
        
        # Create a folder for export based on the original log file name
        conversation = self.conversations[self.current_index]
        log_file_path = conversation['file_path']
        log_file_name = os.path.basename(log_file_path)
        
        # Create export directory name based on the original log file
        export_dir_name = log_file_name.replace('.txt', '')  # Remove extension
        export_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_dir_name)
        
        # Create the directory if it doesn't exist
        os.makedirs(export_dir_path, exist_ok=True)
        
        # Update export path to the new directory (no longer displayed but still used)
        self.auto_export_path = os.path.join(export_dir_path, f"rlhf_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Only export items with both preferred and non-preferred outputs
        dpo_data = []
        
        for item in self.annotated_data:
            if 'preferred_output' in item and 'non_preferred_output' in item:
                dpo_item = {
                    'input': item['input'],
                    'preferred_output': item['preferred_output'],
                    'non_preferred_output': item['non_preferred_output']
                }
                dpo_data.append(dpo_item)
        
        # Export the annotated data to JSON
        with open(self.auto_export_path, 'w', encoding='utf-8') as f:
            json.dump(dpo_data, f, indent=2, ensure_ascii=False)
        
        # Copy the original log file to the export directory
        destination = os.path.join(export_dir_path, log_file_name)
        if not os.path.exists(destination):
            shutil.copy2(log_file_path, destination)
        
        self.status_var.set(f"Auto-exported {len(dpo_data)} annotations to {export_dir_path}")
    
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
        
        # Ask for export file path
        file_path = filedialog.asksaveasfilename(
            title="Export Annotated Data",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir="."
        )
        
        if not file_path:
            return
        
        try:
            # Get the directory for the export
            export_dir = os.path.dirname(file_path)
            
            # If it's a new directory, create it
            if not os.path.exists(export_dir):
                os.makedirs(export_dir, exist_ok=True)
            
            # Format the data for DPO
            dpo_data = []
            
            for item in self.annotated_data:
                # Only include items with both preferred and non-preferred outputs
                if 'preferred_output' in item and 'non_preferred_output' in item:
                    dpo_item = {
                        'input': item['input'],
                        'preferred_output': item['preferred_output'],
                        'non_preferred_output': item['non_preferred_output']
                    }
                    dpo_data.append(dpo_item)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(dpo_data, f, indent=2, ensure_ascii=False)
            
            # Find unique log files in the annotated data
            log_files = set()
            for item in self.annotated_data:
                if 'metadata' in item and 'file_path' in item['metadata']:
                    log_files.add(item['metadata']['file_path'])
            
            # Copy each unique log file to the export directory
            for log_file in log_files:
                if os.path.exists(log_file):
                    destination = os.path.join(export_dir, os.path.basename(log_file))
                    if not os.path.exists(destination):
                        shutil.copy2(log_file, destination)
            
            self.status_var.set(f"Exported {len(dpo_data)} annotations to {file_path}")
            messagebox.showinfo("Export Complete", f"Successfully exported {len(dpo_data)} annotations.\nOriginal log files were also copied to the export directory.")
        except Exception as e:
            self.status_var.set(f"Error exporting data: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = RLHFAnnotator(root)
    root.mainloop()

if __name__ == "__main__":
    main() 