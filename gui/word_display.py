"""
Word Display Panel for AI Reading Assistant

This module provides a GUI panel for displaying words during reading sessions.
It includes word presentation, pronunciation controls, and definition display.
"""

import tkinter as tk
from tkinter import ttk
import tts
from typing import Optional, Callable


class WordDisplayPanel(ttk.Frame):
    """
    A GUI panel for displaying and managing word presentation during reading.
    
    Features:
    - Display current word with formatting
    - Show word definitions and pronunciation
    - Control playback and navigation
    - Visual feedback for reading progress
    """
    
    def __init__(self, parent, on_word_selected: Optional[Callable] = None, **kwargs):
        """
        Initialize the Word Display Panel.
        
        Args:
            parent: Parent widget
            on_word_selected: Callback function when word is selected
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.on_word_selected = on_word_selected
        self.current_word = None
        self.current_definition = None
        self.tts_enabled = True
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface components."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Top control bar
        self._create_control_bar()
        
        # Main word display area
        self._create_word_display()
        
        # Definition and details area
        self._create_details_area()
        
        # Bottom navigation bar
        self._create_navigation_bar()
    
    def _create_control_bar(self) -> None:
        """Create the top control bar with audio controls."""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        control_frame.columnconfigure(1, weight=1)
        
        # Pronunciation button
        self.pronounce_btn = ttk.Button(
            control_frame,
            text="🔊 Pronounce",
            command=self._on_pronounce
        )
        self.pronounce_btn.grid(row=0, column=0, padx=2)
        
        # Spacer
        ttk.Label(control_frame, text="").grid(row=0, column=1)
        
        # TTS toggle button
        self.tts_btn = ttk.Button(
            control_frame,
            text="🔔 TTS On",
            command=self._toggle_tts
        )
        self.tts_btn.grid(row=0, column=2, padx=2)
        
        # Settings button
        settings_btn = ttk.Button(
            control_frame,
            text="⚙️ Settings",
            command=self._on_settings
        )
        settings_btn.grid(row=0, column=3, padx=2)
    
    def _create_word_display(self) -> None:
        """Create the main word display area."""
        display_frame = ttk.LabelFrame(self, text="Current Word", padding=10)
        display_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(1, weight=1)
        
        # Word text display
        self.word_label = tk.Label(
            display_frame,
            text="—",
            font=("Helvetica", 48, "bold"),
            fg="#2c3e50"
        )
        self.word_label.grid(row=0, column=0, sticky='ew', pady=10)
        
        # Phonetic transcription
        self.phonetic_label = tk.Label(
            display_frame,
            text="",
            font=("Helvetica", 16, "italic"),
            fg="#7f8c8d"
        )
        self.phonetic_label.grid(row=1, column=0, sticky='ew', pady=5)
        
        # Part of speech and additional info
        self.info_label = tk.Label(
            display_frame,
            text="",
            font=("Helvetica", 12),
            fg="#34495e"
        )
        self.info_label.grid(row=2, column=0, sticky='ew', pady=5)
    
    def _create_details_area(self) -> None:
        """Create the area for word definitions and examples."""
        details_frame = ttk.LabelFrame(self, text="Definition & Examples", padding=10)
        details_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Scrollable text widget for definitions
        text_frame = ttk.Frame(details_frame)
        text_frame.grid(row=0, column=0, sticky='nsew')
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.definition_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 11),
            height=6
        )
        self.definition_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.config(command=self.definition_text.yview)
        
        # Configure text tags for formatting
        self.definition_text.tag_config('definition', foreground='#2c3e50', font=("Helvetica", 11, "bold"))
        self.definition_text.tag_config('example', foreground='#7f8c8d', font=("Helvetica", 10, "italic"))
        self.definition_text.config(state=tk.DISABLED)
    
    def _create_navigation_bar(self) -> None:
        """Create the bottom navigation bar."""
        nav_frame = ttk.Frame(self)
        nav_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        nav_frame.columnconfigure(1, weight=1)
        
        # Previous word button
        prev_btn = ttk.Button(
            nav_frame,
            text="← Previous",
            command=self._on_previous
        )
        prev_btn.grid(row=0, column=0, padx=2)
        
        # Word count and progress
        self.progress_label = tk.Label(
            nav_frame,
            text="Word: 0 / 0",
            font=("Helvetica", 10),
            fg="#7f8c8d"
        )
        self.progress_label.grid(row=0, column=1, padx=5)
        
        # Next word button
        next_btn = ttk.Button(
            nav_frame,
            text="Next →",
            command=self._on_next
        )
        next_btn.grid(row=0, column=2, padx=2)
    
    def display_word(self, word: str, phonetic: str = "", part_of_speech: str = "", 
                    definition: str = "", examples: list = None) -> None:
        """
        Display a word with its details.
        
        Args:
            word: The word to display
            phonetic: Phonetic transcription
            part_of_speech: Part of speech (noun, verb, etc.)
            definition: Word definition
            examples: List of example sentences
        """
        self.current_word = word
        self.current_definition = definition
        
        # Update word display
        self.word_label.config(text=word)
        
        # Update phonetic transcription
        self.phonetic_label.config(text=f"/{phonetic}/" if phonetic else "")
        
        # Update part of speech and additional info
        self.info_label.config(text=part_of_speech)
        
        # Update definitions and examples
        self._update_definition_display(definition, examples or [])
        
        # Pronounce if TTS is enabled
        if self.tts_enabled:
            self._pronounce_word(word)
    
    def _update_definition_display(self, definition: str, examples: list) -> None:
        """Update the definition and examples display."""
        self.definition_text.config(state=tk.NORMAL)
        self.definition_text.delete(1.0, tk.END)
        
        if definition:
            self.definition_text.insert(tk.END, "Definition:\n", "definition")
            self.definition_text.insert(tk.END, definition + "\n\n")
        
        if examples:
            self.definition_text.insert(tk.END, "Examples:\n", "definition")
            for i, example in enumerate(examples, 1):
                self.definition_text.insert(tk.END, f"{i}. ", "example")
                self.definition_text.insert(tk.END, example + "\n")
        
        self.definition_text.config(state=tk.DISABLED)
    
    def update_progress(self, current: int, total: int) -> None:
        """
        Update the progress display.
        
        Args:
            current: Current word index
            total: Total number of words
        """
        self.progress_label.config(text=f"Word: {current} / {total}")
    
    def _on_pronounce(self) -> None:
        """Handle pronunciation button click."""
        if self.current_word:
            self._pronounce_word(self.current_word)
    
    def _pronounce_word(self, word: str) -> None:
        """
        Pronounce the given word using TTS.
        
        Args:
            word: Word to pronounce
        """
        try:
            tts.speak(word)
        except Exception as e:
            print(f"Error pronouncing word '{word}': {e}")
    
    def _toggle_tts(self) -> None:
        """Toggle TTS on/off."""
        self.tts_enabled = not self.tts_enabled
        status = "TTS On" if self.tts_enabled else "TTS Off"
        self.tts_btn.config(text=f"🔔 {status}")
    
    def _on_settings(self) -> None:
        """Handle settings button click."""
        # Placeholder for settings functionality
        pass
    
    def _on_previous(self) -> None:
        """Handle previous word button click."""
        if self.on_word_selected:
            self.on_word_selected(-1)
    
    def _on_next(self) -> None:
        """Handle next word button click."""
        if self.on_word_selected:
            self.on_word_selected(1)
    
    def clear(self) -> None:
        """Clear the word display."""
        self.current_word = None
        self.current_definition = None
        self.word_label.config(text="—")
        self.phonetic_label.config(text="")
        self.info_label.config(text="")
        self.definition_text.config(state=tk.NORMAL)
        self.definition_text.delete(1.0, tk.END)
        self.definition_text.config(state=tk.DISABLED)
        self.progress_label.config(text="Word: 0 / 0")
    
    def get_current_word(self) -> Optional[str]:
        """Get the currently displayed word."""
        return self.current_word
    
    def set_tts_enabled(self, enabled: bool) -> None:
        """
        Set TTS enabled state.
        
        Args:
            enabled: True to enable TTS, False to disable
        """
        self.tts_enabled = enabled
        status = "TTS On" if enabled else "TTS Off"
        self.tts_btn.config(text=f"🔔 {status}")


if __name__ == "__main__":
    # Demo application
    root = tk.Tk()
    root.title("Word Display Panel Demo")
    root.geometry("600x700")
    
    def on_word_selected(direction):
        print(f"Navigation: {direction}")
    
    panel = WordDisplayPanel(root, on_word_selected=on_word_selected)
    panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Display sample word
    panel.display_word(
        word="Serendipity",
        phonetic="ser-uh n-dip-i-tee",
        part_of_speech="noun",
        definition="The occurrence of events by chance in a happy or beneficial way.",
        examples=[
            "It was pure serendipity that we met at the coffee shop.",
            "Finding that old photograph was a happy serendipity."
        ]
    )
    panel.update_progress(1, 50)
    
    root.mainloop()
