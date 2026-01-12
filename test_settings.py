#!/usr/bin/env python3
"""Test the settings dialog functionality"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

def test_settings_dialog():
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("400x300")
    
    def open_settings():
        """Open settings dialog for analysis period"""
        settings_window = tk.Toplevel(root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("500x350")
        settings_window.transient(root)
        settings_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="⚙️ Analysis Settings", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Analysis Period Section
        period_frame = ttk.LabelFrame(main_frame, text="Analysis Period (Performance Metrics)", padding="15")
        period_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Read current value from .env
        env_path = Path(".env")
        current_days = "60"  # default
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ANALYSIS_DAYS='):
                        current_days = line.split('=')[1].strip()
                        break
        
        ttk.Label(period_frame, text="Select how many days of training data to analyze:").pack(anchor=tk.W, pady=(0, 10))
        
        # Radio buttons for analysis period
        period_var = tk.StringVar(value=current_days)
        
        periods = [
            ("7", "7 days - Recent trends (returning from break)"),
            ("30", "30 days - Monthly view (current training block)"),
            ("60", "60 days - Long-term patterns (RECOMMENDED)"),
            ("90", "90 days - Seasonal view (full build)")
        ]
        
        for value, label in periods:
            rb = ttk.Radiobutton(period_frame, text=label, variable=period_var, value=value)
            rb.pack(anchor=tk.W, pady=2)
        
        # Info label
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        info_text = "ℹ️ Recovery metrics (RHR, Sleep, Body Battery) always use 7 days\n   Training load (ACWR) always uses 7d/28d windows"
        ttk.Label(info_frame, text=info_text, font=("Arial", 9), foreground="gray").pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_settings():
            new_days = period_var.get()
            
            # Update .env file
            if env_path.exists():
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                # Find and update ANALYSIS_DAYS line
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('ANALYSIS_DAYS='):
                        lines[i] = f'ANALYSIS_DAYS={new_days}\n'
                        updated = True
                        break
                
                # Write back
                with open(env_path, 'w') as f:
                    f.writelines(lines)
                
                messagebox.showinfo(
                    "✓ Settings Saved",
                    f"Analysis period set to {new_days} days\n\n"
                    f"This will apply to your next Coach Brief generation."
                )
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Could not find .env file")
        
        def cancel():
            settings_window.destroy()
        
        ttk.Button(button_frame, text="💾 Save", command=save_settings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✖ Cancel", command=cancel, width=15).pack(side=tk.LEFT, padx=5)
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (settings_window.winfo_width() // 2)
        y = (settings_window.winfo_screenheight() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f'+{x}+{y}')
    
    # Main window content
    ttk.Label(root, text="Settings Dialog Test", font=("Arial", 16, "bold")).pack(pady=20)
    ttk.Button(root, text="⚙️ Open Settings", command=open_settings, width=20).pack(pady=10)
    
    # Show current setting
    env_path = Path(".env")
    current_days = "60"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('ANALYSIS_DAYS='):
                    current_days = line.split('=')[1].strip()
                    break
    
    status_label = ttk.Label(root, text=f"Current: {current_days} days", font=("Arial", 12))
    status_label.pack(pady=10)
    
    def refresh_status():
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ANALYSIS_DAYS='):
                        current_days = line.split('=')[1].strip()
                        status_label.config(text=f"Current: {current_days} days")
                        break
        root.after(1000, refresh_status)
    
    refresh_status()
    
    root.mainloop()

if __name__ == "__main__":
    test_settings_dialog()
