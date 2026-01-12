#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
from pathlib import Path
from PIL import Image, ImageTk
from datetime import datetime
import download_data
import analyze_data
import triathlon_analysis
import visualize_data
import coaching_brief

class OutputRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update()
    def flush(self):
        pass

class GarminAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Garmin Data Analyzer")
        self.root.geometry("1400x900")  # Larger default size
        self.is_running = False
        self.current_image_index = 0
        self.image_files = []
        self.photo_image = None
        self.fullscreen_window = None
        self.setup_ui()
        self.output_redirector = OutputRedirector(self.output_text)
        self.load_visualizations()
    
    def setup_ui(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)
        
        title_frame = ttk.Frame(left_frame)
        title_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        title_frame.columnconfigure(0, weight=1)
        ttk.Label(title_frame, text="🏃 Garmin Data Analyzer 🚴", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="⚙️ Settings", command=self.open_settings, width=10).pack(side=tk.RIGHT, padx=5)
        
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        button_frame.columnconfigure((0, 1), weight=1)
        self.download_btn = ttk.Button(button_frame, text="📥 Download", command=self.download_data, width=15)
        self.download_btn.grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.analyze_btn = ttk.Button(button_frame, text="📊 Analyze", command=self.analyze_data, width=15)
        self.analyze_btn.grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.triathlon_btn = ttk.Button(button_frame, text="🏊🚴🏃 Triathlon", command=self.triathlon_analysis, width=15)
        self.triathlon_btn.grid(row=1, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.coach_btn = ttk.Button(button_frame, text="🏆 Coach Brief", command=self.coach_brief, width=15)
        self.coach_btn.grid(row=1, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.visualize_btn = ttk.Button(button_frame, text="📈 Visualize", command=self.visualize_data, width=15)
        self.visualize_btn.grid(row=2, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.all_btn = ttk.Button(button_frame, text="⚡ Run All", command=self.run_all, width=15)
        self.all_btn.grid(row=2, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.save_output_btn = ttk.Button(button_frame, text="💾 Save Output", command=self.save_output, width=15)
        self.save_output_btn.grid(row=3, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_output, width=15)
        self.clear_btn.grid(row=3, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        self.quit_btn = ttk.Button(button_frame, text="❌ Quit", command=self.quit_app, width=15)
        self.quit_btn.grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky=(tk.W, tk.E))
        output_frame = ttk.LabelFrame(left_frame, text="Output", padding="5")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=50, height=20, font=("Courier", 14))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(left_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).grid(row=3, column=0, sticky=(tk.W, tk.E))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        ttk.Label(right_frame, text="📊 Visualizations", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(0, 10))
        canvas_frame = ttk.Frame(right_frame, relief=tk.SUNKEN, borderwidth=2)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.image_canvas = tk.Canvas(canvas_frame, bg='white')
        self.image_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.image_info_var = tk.StringVar(value="No visualizations found")
        ttk.Label(right_frame, textvariable=self.image_info_var, font=("Arial", 10)).grid(row=2, column=0, pady=(0, 5))
        nav_frame = ttk.Frame(right_frame)
        nav_frame.grid(row=3, column=0)
        self.prev_btn = ttk.Button(nav_frame, text="⬅ Previous", command=self.prev_image, width=12)
        self.prev_btn.pack(side=tk.LEFT, padx=3)
        self.next_btn = ttk.Button(nav_frame, text="Next ➡", command=self.next_image, width=12)
        self.next_btn.pack(side=tk.LEFT, padx=3)
        self.refresh_btn = ttk.Button(nav_frame, text="🔄 Refresh", command=self.load_visualizations, width=12)
        self.refresh_btn.pack(side=tk.LEFT, padx=3)
        self.fullscreen_btn = ttk.Button(nav_frame, text="🔍 Fullscreen", command=self.show_fullscreen, width=12)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=3)
    
    def load_visualizations(self):
        viz_dir = Path("./data/visualizations")
        if not viz_dir.exists():
            self.image_files = []
            self.current_image_index = 0
            self.display_no_images()
            return
        self.image_files = sorted(list(viz_dir.glob("*.png")))
        if not self.image_files:
            self.display_no_images()
        else:
            self.current_image_index = 0
            self.display_current_image()
    
    def display_no_images(self):
        self.image_canvas.delete("all")
        self.image_info_var.set("No visualizations found - Create some first!")
        self.prev_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
    
    def display_current_image(self):
        if not self.image_files:
            self.display_no_images()
            return
        image_path = self.image_files[self.current_image_index]
        try:
            image = Image.open(image_path)
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            if canvas_width <= 1:
                canvas_width = 600
            if canvas_height <= 1:
                canvas_height = 500
            img_width, img_height = image.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale * 0.95)
            new_height = int(img_height * scale * 0.95)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(image)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo_image, anchor=tk.CENTER)
            self.image_info_var.set(f"📊 {image_path.name} ({self.current_image_index + 1}/{len(self.image_files)})")
            self.prev_btn.config(state='normal' if self.current_image_index > 0 else 'disabled')
            self.next_btn.config(state='normal' if self.current_image_index < len(self.image_files) - 1 else 'disabled')
        except Exception as e:
            self.image_canvas.delete("all")
            self.image_info_var.set(f"Error loading image: {str(e)}")
    
    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
    
    def next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.display_current_image()
    
    def set_buttons_state(self, state):
        for btn in [self.download_btn, self.analyze_btn, self.triathlon_btn, self.coach_btn, self.visualize_btn, self.all_btn, self.save_output_btn, self.clear_btn]:
            btn.config(state=state)
    
    def run_in_thread(self, func, *args):
        if self.is_running:
            messagebox.showwarning("Busy", "An operation is already running. Please wait.")
            return
        def wrapper():
            self.is_running = True
            self.root.after(0, lambda: self.set_buttons_state('disabled'))
            old_stdout = sys.stdout
            try:
                sys.stdout = self.output_redirector
                func(*args)
                self.root.after(0, lambda: self.status_var.set("✓ Complete"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.output_text.insert(tk.END, f"\n\n✗ Error: {error_msg}\n"))
                self.root.after(0, lambda: self.status_var.set("✗ Error occurred"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{error_msg}"))
            finally:
                sys.stdout = old_stdout
                self.is_running = False
                self.root.after(0, lambda: self.set_buttons_state('normal'))
        threading.Thread(target=wrapper, daemon=True).start()
    
    def download_data(self):
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Downloading data from Garmin Connect...")
        self.run_in_thread(download_data.main)
    
    def analyze_data(self):
        if not Path("./data/activities.csv").exists():
            messagebox.showwarning("No Data", "No data found. Please download data first.")
            return
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Analyzing data...")
        self.run_in_thread(analyze_data.main)
    
    def triathlon_analysis(self):
        if not Path("./data/activities.csv").exists():
            messagebox.showwarning("No Data", "No data found. Please download data first.")
            return
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Running triathlon analysis...")
        self.run_in_thread(triathlon_analysis.main)
    
    def coach_brief(self):
        if not Path("./data/activities.csv").exists():
            messagebox.showwarning("No Data", "No data found. Please download data first.")
            return
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Generating coaching brief...")
        
        def run_and_save_prompt():
            coaching_brief.main()
            # After generating, save AI prompt to file
            output_file = self.save_ai_prompt_to_file()
            if output_file:
                # Show success message from main thread
                self.root.after(0, lambda: messagebox.showinfo(
                    "✓ AI Prompt Saved!", 
                    f"Coach brief prompt saved to:\n\n{output_file}\n\n"
                    f"You can now:\n"
                    f"1. Open the file\n"
                    f"2. Copy all text (Ctrl+A, Ctrl+C)\n"
                    f"3. Paste into Gemini/ChatGPT/Claude"
                ))
        
        self.run_in_thread(run_and_save_prompt)
    
    def save_ai_prompt_to_file(self):
        """Save AI coach prompt to a text file in ~/Documents/coaches_brief/"""
        # Read the coaching brief JSON to extract AI prompt
        brief_path = Path("./data/coaching_brief.json")
        if not brief_path.exists():
            return
        
        import json
        from datetime import datetime
        
        with open(brief_path, 'r') as f:
            brief_data = json.load(f)
        
        ai_prompt = brief_data.get('ai_coach_prompt', '')
        if not ai_prompt:
            return
        
        # Create output directory
        import os
        output_dir = Path(os.path.expanduser('~/Documents/coaches_brief'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = output_dir / f"ai_coach_prompt_{timestamp}.txt"
        
        # Write prompt to file
        with open(output_file, 'w') as f:
            f.write(ai_prompt)
        
        # Return the file path for display (will be shown from main thread)
        return str(output_file)
    
    def show_ai_prompt_dialog(self):
        """Show dialog with AI coach prompt and copy button"""
        # Read the coaching brief JSON to extract AI prompt
        brief_path = Path("./data/coaching_brief.json")
        if not brief_path.exists():
            return
        
        import json
        with open(brief_path, 'r') as f:
            brief_data = json.load(f)
        
        ai_prompt = brief_data.get('ai_coach_prompt', '')
        if not ai_prompt:
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("🤖 AI Coach Prompt")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📋 Copy this prompt to Gemini/ChatGPT/Claude", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Text widget with prompt
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        prompt_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=90, height=30, 
                                                 font=("Courier", 9))
        prompt_text.pack(fill=tk.BOTH, expand=True)
        prompt_text.insert(1.0, ai_prompt)
        # Make text selectable but not editable
        prompt_text.config(state='normal')
        
        # Enable standard copy shortcuts
        def copy_selection(event=None):
            try:
                selected_text = prompt_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
            except tk.TclError:
                # No selection, copy all
                copy_to_clipboard()
            return "break"
        
        # Bind Ctrl+C and Ctrl+A
        prompt_text.bind('<Control-c>', copy_selection)
        prompt_text.bind('<Control-C>', copy_selection)
        prompt_text.bind('<Control-a>', lambda e: (select_all(), "break")[1])
        prompt_text.bind('<Control-A>', lambda e: (select_all(), "break")[1])
        
        # Make text read-only by preventing edits but allowing selection
        def on_key(event):
            # Allow selection shortcuts
            if event.state & 0x4:  # Control key
                if event.keysym in ('c', 'C', 'a', 'A'):
                    return
            # Block all other keys
            return "break"
        
        prompt_text.bind('<Key>', on_key)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(ai_prompt)
            self.root.update()  # Force clipboard update
            messagebox.showinfo("Copied!", "✓ Prompt copied to clipboard!\n\nYou can now paste (Ctrl+V) into:\n• Gemini\n• ChatGPT\n• Claude")
        
        def select_all():
            prompt_text.tag_add('sel', '1.0', 'end-1c')
            prompt_text.mark_set('insert', '1.0')
            prompt_text.see('insert')
            prompt_text.focus_set()
        
        # Instructions label
        info_label = ttk.Label(main_frame, 
                              text="💡 Tip: Use Ctrl+A to select all, Ctrl+C to copy, or click the button below",
                              foreground='gray', font=("Arial", 9, "italic"))
        info_label.pack(pady=(0, 5))
        
        ttk.Button(button_frame, text="📋 Copy All to Clipboard", command=copy_to_clipboard, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ Select All", command=select_all, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Close", command=dialog.destroy, width=10).pack(side=tk.RIGHT, padx=5)
    
    def visualize_data(self):
        if not Path("./data/activities.csv").exists():
            messagebox.showwarning("No Data", "No data found. Please download data first.")
            return
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Creating visualizations...")
        def run_and_refresh():
            visualize_data.main()
            self.root.after(1000, self.load_visualizations)
        self.run_in_thread(run_and_refresh)
    
    def run_all(self):
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.output_text.insert(tk.END, "Starting complete pipeline...\n")
        self.output_text.insert(tk.END, "="*70 + "\n")
        self.status_var.set("⏳ Running complete pipeline...")
        def run_pipeline():
            download_data.main()
            self.output_text.insert(tk.END, "\n")
            analyze_data.main()
            self.output_text.insert(tk.END, "\n")
            triathlon_analysis.main()
            self.output_text.insert(tk.END, "\n")
            coaching_brief.main()
            self.output_text.insert(tk.END, "\n")
            visualize_data.main()
            self.root.after(1000, self.load_visualizations)
        self.run_in_thread(run_pipeline)
    
    def save_output(self):
        """Save the entire output text to a file"""
        from datetime import datetime
        import os
        
        output_content = self.output_text.get(1.0, tk.END).strip()
        if not output_content:
            messagebox.showinfo("No Output", "There is no output to save.")
            return
        
        # Create output directory
        output_dir = Path(os.path.expanduser('~/Documents/garmin_analysis_output'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = output_dir / f"analysis_output_{timestamp}.txt"
        
        # Write output to file
        with open(output_file, 'w') as f:
            f.write(output_content)
        
        messagebox.showinfo(
            "✓ Output Saved!",
            f"Analysis output saved to:\n\n{output_file}\n\n"
            f"File size: {len(output_content)} characters"
        )
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
    
    def quit_app(self):
        """Quit the application"""
        if self.is_running:
            response = messagebox.askyesno(
                "Operation Running",
                "An operation is currently running. Are you sure you want to quit?"
            )
            if not response:
                return
        self.root.quit()
        self.root.destroy()
    
    def show_fullscreen(self):
        """Show current visualization in fullscreen window"""
        if not self.image_files or self.fullscreen_window:
            return
        
        image_path = self.image_files[self.current_image_index]
        
        # Create fullscreen window
        self.fullscreen_window = tk.Toplevel(self.root)
        self.fullscreen_window.title(f"Fullscreen: {image_path.name}")
        self.fullscreen_window.attributes('-fullscreen', True)
        self.fullscreen_window.configure(bg='black')
        
        # Bind Escape to exit fullscreen
        self.fullscreen_window.bind('<Escape>', lambda e: self.close_fullscreen())
        self.fullscreen_window.bind('<Button-1>', lambda e: self.close_fullscreen())
        
        # Create canvas
        canvas = tk.Canvas(self.fullscreen_window, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Force window update and wait for it to be fully rendered
        self.fullscreen_window.update()
        
        # Now get actual canvas dimensions after window is rendered
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Load and display image at full screen size
        image = Image.open(image_path)
        
        # Scale to fit canvas - use 0.95 to leave small margin
        img_width, img_height = image.size
        scale = min(canvas_width / img_width, canvas_height / img_height) * 0.95
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo, anchor=tk.CENTER)
        canvas.image = photo  # Keep reference
        
        # Add instructions
        canvas.create_text(screen_width // 2, screen_height - 30, 
                         text="Press ESC or click to exit fullscreen", 
                         fill='white', font=('Arial', 14))
    
    def close_fullscreen(self):
        """Close fullscreen window"""
        if self.fullscreen_window:
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
    
    def open_settings(self):
        """Open settings dialog for Garmin account and race configuration"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("600x650")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Load current .env values
        from dotenv import load_dotenv
        load_dotenv()
        
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # ===== GARMIN ACCOUNT TAB =====
        account_tab = ttk.Frame(notebook, padding="10")
        notebook.add(account_tab, text="🔐 Garmin Account")
        
        ttk.Label(account_tab, text="Garmin Connect Credentials", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Email
        email_frame = ttk.Frame(account_tab)
        email_frame.pack(fill=tk.X, pady=5)
        ttk.Label(email_frame, text="Email:", width=15).pack(side=tk.LEFT)
        garmin_email_var = tk.StringVar(value=os.getenv('GARMIN_EMAIL', ''))
        email_entry = ttk.Entry(email_frame, textvariable=garmin_email_var, width=35)
        email_entry.pack(side=tk.LEFT, padx=5)
        
        # Password
        password_frame = ttk.Frame(account_tab)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="Password:", width=15).pack(side=tk.LEFT)
        garmin_password_var = tk.StringVar(value=os.getenv('GARMIN_PASSWORD', ''))
        password_entry = ttk.Entry(password_frame, textvariable=garmin_password_var, width=35, show='•')
        password_entry.pack(side=tk.LEFT, padx=5)
        
        # Show password checkbox
        show_password_var = tk.BooleanVar(value=False)
        def toggle_password():
            password_entry.config(show='' if show_password_var.get() else '•')
        ttk.Checkbutton(password_frame, text="Show", variable=show_password_var, 
                       command=toggle_password).pack(side=tk.LEFT, padx=5)
        
        # Help text for Garmin account
        account_help = ttk.LabelFrame(account_tab, text="ℹ️ Important Information", padding="10")
        account_help.pack(fill=tk.BOTH, expand=True, pady=15)
        
        help_text = """Garmin Connect Account:
• Use your Garmin Connect login credentials
• Password is stored in plain text in .env file
• Keep your .env file secure (already in .gitignore)
• Required for downloading activity data

Security Tips:
• Don't share your .env file
• Don't commit .env to version control
• Consider using a dedicated Garmin account if security is a concern"""
        
        ttk.Label(account_help, text=help_text, justify=tk.LEFT, wraplength=520).pack()
        
        # ===== RACE PLANNING TAB =====
        race_tab = ttk.Frame(notebook, padding="10")
        notebook.add(race_tab, text="🏁 Race Planning")
        
        ttk.Label(race_tab, text="Race Configuration", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Race Date
        date_frame = ttk.Frame(race_tab)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="Race Date:", width=15).pack(side=tk.LEFT)
        race_date_var = tk.StringVar(value=os.getenv('RACE_DATE', ''))
        race_date_entry = ttk.Entry(date_frame, textvariable=race_date_var, width=20)
        race_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="(YYYY-MM-DD)", foreground='gray').pack(side=tk.LEFT)
        
        # Race Type
        type_frame = ttk.Frame(race_tab)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Race Type:", width=15).pack(side=tk.LEFT)
        race_type_var = tk.StringVar(value=os.getenv('RACE_TYPE', ''))
        race_type_combo = ttk.Combobox(type_frame, textvariable=race_type_var, width=18,
                                       values=['sprint', 'olympic', 'half_ironman', 'full_ironman', 'triple_t'])
        race_type_combo.pack(side=tk.LEFT, padx=5)
        
        # Race Priority
        priority_frame = ttk.Frame(race_tab)
        priority_frame.pack(fill=tk.X, pady=5)
        ttk.Label(priority_frame, text="Priority:", width=15).pack(side=tk.LEFT)
        race_priority_var = tk.StringVar(value=os.getenv('RACE_PRIORITY', 'A'))
        priority_combo = ttk.Combobox(priority_frame, textvariable=race_priority_var, width=18,
                                      values=['A', 'B', 'C'])
        priority_combo.pack(side=tk.LEFT, padx=5)
        
        # Help text for race planning
        race_help = ttk.LabelFrame(race_tab, text="ℹ️ Race Planning Guide", padding="10")
        race_help.pack(fill=tk.BOTH, expand=True, pady=15)
        
        race_help_text = """Race Types:
• sprint - Sprint distance triathlon
• olympic - Olympic distance triathlon
• half_ironman - 70.3 distance
• full_ironman - Full Ironman distance
• triple_t - Triple T (4 races in 3 days)
  Friday: Super Sprint
  Saturday AM: Sprint
  Saturday PM: Sprint
  Sunday: Olympic

Race Priority:
• A - Main goal race (full taper and peak)
• B - Tune-up race (reduced taper)
• C - Training race (no taper)

Off-Season:
• Leave race date empty for off-season training
• Focus on base building and technique work"""
        
        ttk.Label(race_help, text=race_help_text, justify=tk.LEFT, wraplength=520).pack()
        
        # ===== ANALYSIS PERIOD TAB =====
        analysis_tab = ttk.Frame(notebook, padding="10")
        notebook.add(analysis_tab, text="📊 Analysis Period")
        
        ttk.Label(analysis_tab, text="Performance Analysis Settings", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Analysis Period Section
        period_frame = ttk.LabelFrame(analysis_tab, text="Analysis Period (Performance Metrics)", padding="15")
        period_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Read current value from .env
        current_days = os.getenv('ANALYSIS_DAYS', '60')
        
        ttk.Label(period_frame, text="Select how many days of training data to analyze:").pack(anchor=tk.W, pady=(0, 10))
        
        # Radio buttons for analysis period
        analysis_days_var = tk.StringVar(value=current_days)
        
        periods = [
            ("7", "7 days - Recent trends (returning from break)"),
            ("30", "30 days - Monthly view (current training block)"),
            ("60", "60 days - Long-term patterns (RECOMMENDED)"),
            ("90", "90 days - Seasonal view (full build)")
        ]
        
        for value, label in periods:
            rb = ttk.Radiobutton(period_frame, text=label, variable=analysis_days_var, value=value)
            rb.pack(anchor=tk.W, pady=2)
        
        # Analysis help text
        analysis_help = ttk.LabelFrame(analysis_tab, text="ℹ️ Analysis Period Guide", padding="10")
        analysis_help.pack(fill=tk.BOTH, expand=True, pady=15)
        
        analysis_help_text = """Performance Metrics (Configurable):
• HR Zone Distribution (Z1-Z2, Z3, Z4-Z5)
• Run Aerobic Decoupling
• Swim SWOLF efficiency
• Bike Efficiency Factor trends

Recovery Metrics (Always 7 days):
• Resting Heart Rate (RHR)
• Body Battery levels
• Sleep Score
• Stress levels

Training Load (Fixed windows):
• ACWR: 7-day acute / 28-day chronic

Recommendations:
• Use 60 days (default) for most training analysis
• Use 7 days when returning from a break
• Use 30 days for mid-block assessments
• Use 90 days for full season reviews"""
        
        ttk.Label(analysis_help, text=analysis_help_text, justify=tk.LEFT, wraplength=520).pack()
        
        # Buttons at the bottom of the window
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def save_settings():
            # Read current .env
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update settings
            new_lines = []
            found_email = found_password = False
            found_date = found_type = found_priority = False
            found_analysis_days = False
            
            for line in lines:
                if line.startswith('GARMIN_EMAIL='):
                    new_lines.append(f"GARMIN_EMAIL={garmin_email_var.get()}\n")
                    found_email = True
                elif line.startswith('GARMIN_PASSWORD='):
                    new_lines.append(f"GARMIN_PASSWORD={garmin_password_var.get()}\n")
                    found_password = True
                elif line.startswith('RACE_DATE='):
                    new_lines.append(f"RACE_DATE={race_date_var.get()}\n")
                    found_date = True
                elif line.startswith('RACE_TYPE='):
                    new_lines.append(f"RACE_TYPE={race_type_var.get()}\n")
                    found_type = True
                elif line.startswith('RACE_PRIORITY='):
                    new_lines.append(f"RACE_PRIORITY={race_priority_var.get()}\n")
                    found_priority = True
                elif line.startswith('ANALYSIS_DAYS='):
                    new_lines.append(f"ANALYSIS_DAYS={analysis_days_var.get()}\n")
                    found_analysis_days = True
                else:
                    new_lines.append(line)
            
            # Add if not found
            if not found_email:
                new_lines.append(f"GARMIN_EMAIL={garmin_email_var.get()}\n")
            if not found_password:
                new_lines.append(f"GARMIN_PASSWORD={garmin_password_var.get()}\n")
            if not found_date:
                new_lines.append(f"RACE_DATE={race_date_var.get()}\n")
            if not found_type:
                new_lines.append(f"RACE_TYPE={race_type_var.get()}\n")
            if not found_priority:
                new_lines.append(f"RACE_PRIORITY={race_priority_var.get()}\n")
            if not found_analysis_days:
                new_lines.append(f"ANALYSIS_DAYS={analysis_days_var.get()}\n")
            if not found_priority:
                new_lines.append(f"RACE_PRIORITY={race_priority_var.get()}\n")
            
            # Write back
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
            
            # Show success message
            save_message = "Settings saved successfully!\n\n"
            if garmin_email_var.get() and garmin_password_var.get():
                save_message += "✓ Garmin credentials updated\n"
            if race_date_var.get():
                save_message += f"✓ Race date: {race_date_var.get()}\n"
                save_message += "\nRun Coach Brief to see updated periodization."
            
            messagebox.showinfo("Success", save_message)
            settings_window.destroy()
        
        def test_garmin_connection():
            """Test Garmin Connect credentials"""
            if not garmin_email_var.get() or not garmin_password_var.get():
                messagebox.showwarning("Missing Credentials", "Please enter both email and password first.")
                return
            
            # Show testing message
            test_button.config(state='disabled', text="Testing...")
            settings_window.update()
            
            try:
                from garminconnect import Garmin
                client = Garmin(garmin_email_var.get(), garmin_password_var.get())
                client.login()
                messagebox.showinfo("Success", "✓ Connection successful!\n\nGarmin credentials are valid.")
                test_button.config(state='normal', text="🔌 Test Connection")
            except Exception as e:
                messagebox.showerror("Connection Failed", f"✗ Could not connect to Garmin:\n\n{str(e)}\n\nPlease check your credentials.")
                test_button.config(state='normal', text="🔌 Test Connection")
        
        # Test connection button (only visible in account tab)
        test_button = ttk.Button(account_tab, text="🔌 Test Connection", command=test_garmin_connection)
        test_button.pack(pady=10)
        
        # Save and Cancel buttons
        ttk.Button(button_frame, text="💾 Save All Settings", command=save_settings, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=settings_window.destroy, width=15).pack(side=tk.RIGHT, padx=5)

def main():
    if not Path(".env").exists():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Configuration Missing", "No .env file found!\n\nPlease create a .env file with your Garmin credentials:\n  GARMIN_EMAIL=your.email@example.com\n  GARMIN_PASSWORD=your_password\n\nYou can copy .env.example to .env and edit it.")
        response = messagebox.askyesno("Continue anyway?", "Do you want to continue without credentials?\n(You won't be able to download data)")
        if not response:
            return
    root = tk.Tk()
    app = GarminAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
