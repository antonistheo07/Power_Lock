"""
Order Management System - Main Entry Point

A comprehensive order management application for tracking customers,
inventory, and orders with a clean, modern interface.

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - No external dependencies (uses Python stdlib only)
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow
from utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def main():
    """Main application entry point."""
    try:
        logger.info("="*60)
        logger.info("Starting Order Management System")
        logger.info("="*60)
        
        # Create and run application
        app = MainWindow()
        app.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        
        # Try to show error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Fatal Error",
                f"Application failed to start:\n\n{e}\n\n"
                "Please check app.log for details."
            )
        except:
            print(f"FATAL ERROR: {e}", file=sys.stderr)
        
        sys.exit(1)


if __name__ == "__main__":
    main()