#!/usr/bin/env python3
"""
Garmin Data Analysis App - GUI
Graphical user interface for downloading, analyzing, and visualizing Garmin data.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from io import StringIO
from pathlib import Path
import os
from PIL import Image, ImageTk

# Import the analysis modules
import download_data
import analyze_data
import visualize_data


class OutputRedirector:
    """Redirect stdout to GUI text widget."""
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
        self.root.geometry("1200x800")
        
        # Variables
        self.is_running = False
        self.current_image_index = 0
        self.image_files = []
        self.photo_image = None
        
        # Setup UI
        self.setup_ui()
        
        # Redirect stdout
        self.output_redirector = OutputRedirector(self.output_text)
        
        # Load existing visualizations
        self.load_visualizations()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container - use PanedWindow for resizable sections
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls and Output
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        # Right panel - Image Viewer
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=1)
        
        # Configure left frame grid
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            left_frame, 
            text="🏃 Garmin Data Analyzer 🚴",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        button_frame.columnconfigure((0, 1), weight=1)
        
        # Buttons
        self.download_btn = ttk.Button(
            button_frame,
            text="📥 Download",
            command=self.download_data,
            width=15
        )
        self.download_btn.grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        self.analyze_btn = ttk.Button(
            button_frame,
            text="📊 Analyze",
            command=self.analyze_data,
            width=15
        )
        self.analyze_btn.grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        self.visualize_btn = ttk.Button(
            button_frame,
            text="📈 Visualize",
            command=self.visualize_data,
            width=15
        )
        self.visualize_btn.grid(row=1, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        self.all_btn = ttk.Button(
            button_frame,
            text="⚡ Run All",
            command=self.run_all,
            width=15,
            style="Accent.TButton"
        )
        self.all_btn.grid(row=1, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_output,
            width=15
        )
        self.clear_btn.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        # Output text area
        output_frame = ttk.LabelFrame(left_frame, text="Output", padding="5")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=("Courier", 9)
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            left_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Right panel - Image Viewer
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Image viewer title
        viewer_title = ttk.Label(
            right_frame,
            text="📊 Visualizations",
            font=("Arial", 14, "bold")
        )
        viewer_title.grid(row=0, column=0, pady=(0, 10))
        load_visualizations(self):
        """Load visualization images from the data directory."""
        viz_dir = Path("./data/visualizations")
        if not viz_dir.exists():
            self.image_files = []
            self.current_image_index = 0
            self.display_no_images()
            return
        
        # Get all PNG files
        self.image_files = sorted(list(viz_dir.glob("*.png")))
        
        if not self.image_files:
            self.display_no_images()
        else:
            self.current_image_index = 0
            self.display_current_image()
    
    def display_no_images(self):
        """Display message when no images are available."""
        self.image_canvas.delete("all")
        self.image_info_var.set("No visualizations found - Create some first!")
        self.prev_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
    
    def display_current_image(self):
        """Display the current image in the canvas."""
        if not self.image_files:
            self.display_no_images()
            return
        
        # Get current image file
        image_path = self.image_files[self.current_image_index]
        
        # Load and resize image
        try:
            image = Image.open(image_path)
            
            # Get canvas size
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            # Use default size if canvas hasn't been drawn yet
            if canvas_width <= 1:
                canvas_width = 600
            if canvas_height <= 1:
                canvas_height = 500
            
            # Calculate scaling to fit canvas while maintaining aspect ratio
            img_width, img_height = image.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale * 0.95)  # 95% to add padding
            new_height = int(img_height * scale * 0.95)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(image)
            
            # Clear canvas and display image
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.photo_image,
                anchor=tk.CENTER
            )
            
            # Update info label
            image_name = image_path.name
            self.image_info_var.set(
                f"📊 {image_name} ({self.current_image_index + 1}/{len(self.image_files)})"
        
        def run_and_refresh():
            visualize_data.main()
            # Refresh the image viewer after creating visualizations
            self.root.after(1000, self.load_visualizations)
        
        self.run_in_thread(run_and_refresh
            
            # Update button states
            self.prev_btn.config(state='normal' if self.current_image_index > 0 else 'disabled')
            self.next_btn.config(state='normal' if self.current_image_index < len(self.image_files) - 1 else 'disabled')
            
        except Exception as e:
            self.image_canvas.delete("all")
            self.image_info_var.set(f"Error loading image: {str(e)}")
        # Refresh the image viewer after creating visualizations
            self.root.after(1000, self.load_visualizations)
        
    def prev_image(self):
        """Show previous image."""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
    
    def next_image(self):
        """Show next image."""
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.display_current_image()
    
    def 
        # Image canvas frame
        canvas_frame = ttk.Frame(right_frame, relief=tk.SUNKEN, borderwidth=2)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.image_canvas = tk.Canvas(canvas_frame, bg='white')
        self.image_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Image info label
        self.image_info_var = tk.StringVar(value="No visualizations found")
        self.image_info_label = ttk.Label(
            right_frame,
            textvariable=self.image_info_var,
            font=("Arial", 10)
        )
        self.image_info_label.grid(row=2, column=0, pady=(0, 5))
        
        # Navigation buttons
        nav_frame = ttk.Frame(right_frame)
        nav_frame.grid(row=3, column=0)
        
        self.prev_btn = ttk.Button(
            nav_frame,
            text="⬅ Previous",
            command=self.prev_image,
            width=15
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(
            nav_frame,
            text="Next ➡",
            command=self.next_image,
            width=15
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(
            nav_frame,
            text="🔄 Refresh",
            command=self.load_visualizations,
            width=15
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def set_buttons_state(self, state):
        """Enable or disable all buttons."""
        buttons = [
            self.download_btn,
            self.analyze_btn,
            self.visualize_btn,
            self.all_btn,
            self.clear_btn
        ]
        for btn in buttons:
            btn.config(state=state)
    
    def run_in_thread(self, func, *args):
        """Run a function in a separate thread."""
        if self.is_running:
            messagebox.showwarning("Busy", "An operation is already running. Please wait.")
            return
        
        def wrapper():
            self.is_running = True
            self.set_buttons_state('disabled')
            old_stdout = sys.stdout
            
            try:
                sys.stdout = self.output_redirector
                func(*args)
                self.status_var.set("✓ Complete")
            except Exception as e:
                self.output_text.insert(tk.END, f"\n\n✗ Error: {str(e)}\n")
                self.status_var.set("✗ Error occurred")
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            finally:
                sys.stdout = old_stdout
                self.is_running = False
                self.set_buttons_state('normal')
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    def download_data(self):
        """Download data from Garmin Connect."""
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Downloading data from Garmin Connect...")
        self.run_in_thread(download_data.main)
    
    def analyze_data(self):
        """Analyze downloaded data."""
        # Check if data exists
        data_file = Path("./data/activities.csv")
        if not data_file.exists():
            messagebox.showwarning(
                "No Data",
                "No data found. Please download data first."
            )
            return
        
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Analyzing data...")
        self.run_in_thread(analyze_data.main)
    
    def visualize_data(self):
        """Create visualizations."""
        # Check if data exists
        data_file = Path("./data/activities.csv")
        if not data_file.exists():
            messagebox.showwarning(
                "No Data",
                "No data found. Please download data first."
            )
            return
        
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.status_var.set("⏳ Creating visualizations...")
        self.run_in_thread(visualize_data.main)
    
    def run_all(self):
        """Run complete pipeline."""
        self.output_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.output_text.insert(tk.END, "Starting complete pipeline...\n")
        self.output_text.insert(tk.END, "="*70 + "\n")
        self.status_var.set("⏳ Running complete pipeline...")
        
        def run_pipeline():
            download_data.main()
            self.output_text.insert(tk.END, "\n")
            analyze_data.main()
            self.output_text.insert(tk.END, "\n")
            visualize_data.main()
        
        self.run_in_thread(run_pipeline)
    
    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Ready")


def main():
    """Main entry point for GUI."""
    # Check if .env file exists
    if not Path(".env").exists():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Configuration Missing",
            "No .env file found!\n\n"
            "Please create a .env file with your Garmin credentials:\n"
            "  GARMIN_EMAIL=your.email@example.com\n"
            "  GARMIN_PASSWORD=your_password\n\n"
            "You can copy .env.example to .env and edit it."
        )
        response = messagebox.askyesno(
            "Continue anyway?",
            "Do you want to continue without credentials?\n"
            "(You won't be able to download data)"
        )
        if not response:
            return
    
    root = tk.Tk()
    app = GarminAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
