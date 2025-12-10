"""
Screen Reader Module for AI-Reading-Assistant

This module handles screenshot capture with OCR text extraction.
It provides functionality to hide the application window during screenshot
capture to avoid capturing the app interface itself.
"""

import logging
import os
import time
from typing import Optional, Tuple
from pathlib import Path
import subprocess
import platform

try:
    import pytesseract
    from PIL import ImageGrab
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None
    ImageGrab = None

try:
    import tkinter as tk
except ImportError:
    tk = None


logger = logging.getLogger(__name__)


class ScreenReader:
    """
    Handles screenshot capture and OCR text extraction with window hiding capability.
    
    This class provides methods to:
    - Hide/show the parent application window
    - Capture screenshots while the app is hidden
    - Extract text from screenshots using OCR (Tesseract)
    """
    
    def __init__(self, parent_window: Optional[tk.Tk] = None, 
                 tesseract_path: Optional[str] = None):
        """
        Initialize the ScreenReader.
        
        Args:
            parent_window: The parent Tkinter window to hide/show (optional)
            tesseract_path: Path to Tesseract OCR executable (optional)
        """
        self.parent_window = parent_window
        self.tesseract_path = tesseract_path
        self.is_hidden = False
        self.screenshot_dir = Path.home() / ".ai-reading-assistant" / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Tesseract if path provided
        if tesseract_path and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
        
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        """
        Validate that required dependencies are available.
        
        Raises:
            ImportError: If required packages are not installed
        """
        if not TESSERACT_AVAILABLE:
            logger.warning(
                "PIL/Pillow or pytesseract not available. "
                "Install with: pip install pillow pytesseract"
            )
        
        if TESSERACT_AVAILABLE and pytesseract:
            try:
                pytesseract.get_tesseract_version()
            except pytesseract.TesseractNotFoundError:
                logger.warning(
                    "Tesseract OCR not found. Please install Tesseract-OCR. "
                    "Visit: https://github.com/UB-Mannheim/tesseract/wiki"
                )
    
    def hide_window(self) -> bool:
        """
        Hide the parent application window.
        
        Returns:
            bool: True if window was hidden successfully, False otherwise
        """
        if not self.parent_window:
            logger.debug("No parent window set, skipping hide operation")
            return False
        
        try:
            self.parent_window.withdraw()
            self.is_hidden = True
            # Give the window a moment to fully hide
            time.sleep(0.1)
            logger.debug("Parent window hidden successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to hide parent window: {e}")
            return False
    
    def show_window(self) -> bool:
        """
        Show the parent application window.
        
        Returns:
            bool: True if window was shown successfully, False otherwise
        """
        if not self.parent_window:
            logger.debug("No parent window set, skipping show operation")
            return False
        
        try:
            self.parent_window.deiconify()
            self.is_hidden = False
            time.sleep(0.1)
            logger.debug("Parent window shown successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to show parent window: {e}")
            return False
    
    def capture_screenshot(self, 
                          bbox: Optional[Tuple[int, int, int, int]] = None,
                          save_image: bool = False) -> Optional['ImageGrab.Image']:
        """
        Capture a screenshot with optional bounding box.
        
        Args:
            bbox: Bounding box as (left, top, right, bottom), or None for full screen
            save_image: Whether to save the captured image to disk
        
        Returns:
            PIL Image object if successful, None otherwise
        """
        if not TESSERACT_AVAILABLE or ImageGrab is None:
            logger.error("PIL/Pillow not available for screenshot capture")
            return None
        
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            
            if save_image:
                timestamp = int(time.time())
                filename = self.screenshot_dir / f"screenshot_{timestamp}.png"
                screenshot.save(filename)
                logger.debug(f"Screenshot saved to {filename}")
            
            logger.debug("Screenshot captured successfully")
            return screenshot
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def extract_text(self, image=None, 
                    language: str = 'eng',
                    config: str = '') -> Optional[str]:
        """
        Extract text from an image using Tesseract OCR.
        
        Args:
            image: PIL Image object. If None, captures a new screenshot
            language: Tesseract language code (default: 'eng')
            config: Additional Tesseract configuration string
        
        Returns:
            Extracted text string, or None if OCR fails
        """
        if not TESSERACT_AVAILABLE or pytesseract is None:
            logger.error("pytesseract not available for OCR")
            return None
        
        try:
            if image is None:
                image = self.capture_screenshot()
                if image is None:
                    return None
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=language, config=config)
            logger.debug(f"OCR completed, extracted {len(text)} characters")
            return text.strip() if text else None
        except pytesseract.TesseractNotFoundError:
            logger.error(
                "Tesseract not found. Please install: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )
            return None
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return None
    
    def capture_and_read(self, 
                        bbox: Optional[Tuple[int, int, int, int]] = None,
                        language: str = 'eng',
                        save_image: bool = False) -> Optional[str]:
        """
        Perform complete workflow: hide window, capture screenshot, extract text.
        
        Args:
            bbox: Bounding box for screenshot (left, top, right, bottom)
            language: Tesseract language code
            save_image: Whether to save captured image
        
        Returns:
            Extracted text, or None if operation fails
        """
        # Hide window
        self.hide_window()
        
        try:
            # Capture screenshot
            screenshot = self.capture_screenshot(bbox=bbox, save_image=save_image)
            if screenshot is None:
                return None
            
            # Extract text
            text = self.extract_text(image=screenshot, language=language)
            return text
        finally:
            # Always show window again
            self.show_window()
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get the current screen dimensions.
        
        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            if platform.system() == 'Windows':
                import ctypes
                user32 = ctypes.windll.user32
                return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
            else:
                # For Linux/Mac, try using tkinter
                if tk:
                    root = tk.Tk()
                    root.withdraw()
                    width = root.winfo_screenwidth()
                    height = root.winfo_screenheight()
                    root.destroy()
                    return (width, height)
                else:
                    logger.warning("Cannot determine screen dimensions")
                    return (0, 0)
        except Exception as e:
            logger.error(f"Failed to get screen dimensions: {e}")
            return (0, 0)
    
    def cleanup(self) -> None:
        """
        Perform cleanup operations.
        Ensures window is visible before cleanup.
        """
        try:
            if self.is_hidden:
                self.show_window()
            logger.debug("ScreenReader cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Convenience function for quick screenshot reading without class instantiation
def read_screen(bbox: Optional[Tuple[int, int, int, int]] = None,
                language: str = 'eng',
                tesseract_path: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to read text from screen without instantiating the class.
    
    Args:
        bbox: Bounding box for screenshot
        language: Tesseract language code
        tesseract_path: Path to Tesseract executable
    
    Returns:
        Extracted text or None if operation fails
    """
    reader = ScreenReader(tesseract_path=tesseract_path)
    try:
        text = reader.capture_and_read(bbox=bbox, language=language)
        return text
    finally:
        reader.cleanup()
