#!/usr/bin/env python3
"""
AIsCopy - 실시간 화면 번역 도구
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for AIsCopy application"""
    try:
        print("Starting AIsCopy...")
        from ui.main_window import MainWindow
        from PySide6.QtWidgets import QApplication
        
        print("Creating QApplication...")
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("AIsCopy")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AIsCopy")
        
        print("Creating main window...")
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("Starting event loop...")
        # Start event loop
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please install required packages with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
