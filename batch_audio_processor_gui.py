#!/usr/bin/env python3
"""
Batch Audio Processor GUI
A simple GUI for batch processing audio files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from batch_audio_processor import (
    find_audio_files,
    process_audio_file,
    aufs_normalize,
    check_ffmpeg_available
)


class AudioProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Audio Processor")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.target_lufs = tk.StringVar(value="-23.0")
        self.is_processing = False
        
        # Check FFmpeg availability
        self.ffmpeg_available = check_ffmpeg_available()
        
        self.setup_ui()
        
        # Show warning if FFmpeg not available
        if not self.ffmpeg_available:
            messagebox.showwarning(
                "FFmpeg Not Found",
                "FFmpeg is not found in your system PATH.\n\n"
                "FFmpeg is REQUIRED to process audio files (especially FLAC, MP3, M4A, etc.).\n\n"
                "Please install FFmpeg and add it to your system PATH.\n"
                "Download from: https://ffmpeg.org/download.html\n\n"
                "Processing will fail for most file formats without FFmpeg."
            )
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Batch Audio Processor",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input directory
        ttk.Label(main_frame, text="Input Directory:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.input_dir, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_input_dir
        ).grid(row=1, column=2, pady=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_output_dir
        ).grid(row=2, column=2, pady=5)
        
        # Auto-set output directory checkbox
        self.auto_output = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Auto-set output directory (input/processed)",
            variable=self.auto_output,
            command=self.toggle_auto_output
        ).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Target LUFS
        ttk.Label(main_frame, text="Target LUFS:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        lufs_frame = ttk.Frame(main_frame)
        lufs_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(lufs_frame, textvariable=self.target_lufs, width=10).grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Label(lufs_frame, text="(default: -23.0)").grid(
            row=0, column=1, sticky=tk.W, padx=5
        )
        
        # Process button
        self.process_button = ttk.Button(
            main_frame,
            text="Start Processing",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=("Arial", 10)
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Log text area
        ttk.Label(main_frame, text="Processing Log:").grid(
            row=8, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=10, column=0, columnspan=3, pady=10)
        
        self.results_label = ttk.Label(
            results_frame,
            text="",
            font=("Arial", 10, "bold")
        )
        self.results_label.pack()
        
    def browse_input_dir(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.set(directory)
            if self.auto_output.get():
                self.output_dir.set(str(Path(directory) / "processed"))
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def toggle_auto_output(self):
        if self.auto_output.get() and self.input_dir.get():
            self.output_dir.set(str(Path(self.input_dir.get()) / "processed"))
    
    def log(self, message):
        """Add a message to the log text area."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """Validate user inputs."""
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory.")
            return False
        
        input_path = Path(self.input_dir.get())
        if not input_path.exists():
            messagebox.showerror("Error", f"Input directory does not exist:\n{input_path}")
            return False
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory.")
            return False
        
        # Check FFmpeg availability
        if not check_ffmpeg_available():
            response = messagebox.askyesno(
                "FFmpeg Not Found",
                "FFmpeg is not found in your system PATH.\n\n"
                "FFmpeg is REQUIRED to process most audio formats (FLAC, MP3, M4A, etc.).\n\n"
                "Processing will likely fail. Continue anyway?",
                icon='warning'
            )
            if not response:
                return False
        
        try:
            lufs = float(self.target_lufs.get())
            if lufs > 0:
                messagebox.showerror("Error", "Target LUFS should be a negative value (e.g., -23.0)")
                return False
        except ValueError:
            messagebox.showerror("Error", "Target LUFS must be a valid number.")
            return False
        
        return True
    
    def process_files(self):
        """Process audio files in a separate thread."""
        input_path = Path(self.input_dir.get())
        output_path = Path(self.output_dir.get())
        target_lufs = float(self.target_lufs.get())
        
        # Find audio files
        self.log("Searching for audio files...")
        self.update_status("Searching for audio files...")
        audio_files = find_audio_files(input_path)
        
        if not audio_files:
            self.log("No audio files found in the input directory.")
            self.update_status("No audio files found.")
            messagebox.showwarning("Warning", "No audio files found in the input directory.")
            self.is_processing = False
            self.process_button.config(text="Start Processing", state=tk.NORMAL)
            return
        
        self.log(f"Found {len(audio_files)} unique audio file(s) to process.\n")
        self.update_status(f"Found {len(audio_files)} file(s)")
        
        # Process each file (track processed files to avoid duplicates)
        successful = 0
        failed = 0
        processed_files = set()  # Track processed files to prevent duplicates
        processed_count = 0  # Count of actually processed files (excluding duplicates)
        
        for idx, audio_file in enumerate(audio_files):
            if not self.is_processing:
                self.log("\nProcessing cancelled by user.")
                break
            
            # Normalize path to handle case-insensitive filesystems
            normalized_input = audio_file.resolve()
            
            # Skip if already processed
            if normalized_input in processed_files:
                self.log(f"[{idx + 1}/{len(audio_files)}] Skipping duplicate: {audio_file.name}")
                continue
            
            # Mark as processed
            processed_files.add(normalized_input)
            processed_count += 1
            
            # Calculate relative path to preserve directory structure
            relative_path = audio_file.relative_to(input_path)
            output_file = output_path / relative_path
            
            # Update progress based on actually processed files
            progress = (processed_count / len(audio_files)) * 100
            self.update_progress(progress)
            self.update_status(f"Processing {processed_count}/{len(audio_files)}: {audio_file.name}")
            self.log(f"[{processed_count}/{len(audio_files)}] Processing: {audio_file.name}")
            
            if process_audio_file(audio_file, output_file, target_lufs):
                successful += 1
                self.log(f"  ✓ Success: {audio_file.name}")
            else:
                failed += 1
                self.log(f"  ✗ Failed: {audio_file.name}")
        
        # Final results
        self.update_progress(100)
        self.log("\n" + "=" * 60)
        self.log("Processing complete!")
        self.log(f"  Successful: {successful}")
        self.log(f"  Failed: {failed}")
        self.log(f"  Total: {len(audio_files)}")
        
        self.results_label.config(
            text=f"Complete! Successful: {successful}, Failed: {failed}, Total: {len(audio_files)}"
        )
        self.update_status("Processing complete!")
        
        # Show completion message
        messagebox.showinfo(
            "Processing Complete",
            f"Processing complete!\n\nSuccessful: {successful}\nFailed: {failed}\nTotal: {len(audio_files)}"
        )
        
        self.is_processing = False
        self.process_button.config(text="Start Processing", state=tk.NORMAL)
    
    def start_processing(self):
        """Start the processing in a separate thread."""
        if not self.validate_inputs():
            return
        
        if self.is_processing:
            # Cancel processing
            self.is_processing = False
            self.process_button.config(text="Start Processing", state=tk.NORMAL)
            self.log("\nCancelling processing...")
            return
        
        # Clear previous results
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.results_label.config(text="")
        self.update_progress(0)
        
        # Start processing
        self.is_processing = True
        self.process_button.config(text="Cancel Processing", state=tk.NORMAL)
        
        self.log("=" * 60)
        self.log("Batch Audio Processor")
        self.log("=" * 60)
        self.log(f"Input directory: {self.input_dir.get()}")
        self.log(f"Output directory: {self.output_dir.get()}")
        self.log(f"Target LUFS: {self.target_lufs.get()}")
        self.log("=" * 60)
        self.log("")
        
        # Run processing in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    app = AudioProcessorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

