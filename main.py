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
        from PySide6.QtWidgets import QApplication, QMessageBox
        from utils.config_manager import ConfigManager
        from core.translation_engine import TranslationEngine
        
        print("Creating QApplication...")
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("AIsCopy")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AIsCopy")
        
        # API 키 검증
        print("Validating API key...")
        config_manager = ConfigManager()
        config = config_manager.load_config()
        api_key = config.get("api", {}).get("gemini_api_key", "")
        
        if not api_key:
            QMessageBox.critical(None, "API 키 오류", 
                               "API 키가 설정되지 않았습니다.\n설정에서 API 키를 입력해주세요.")
            sys.exit(1)
        
        # API 키 유효성 검증
        try:
            translation_engine = TranslationEngine(api_key)
            if not translation_engine.test_api_connection():
                QMessageBox.critical(None, "API 연결 오류", 
                                   "API 키가 유효하지 않습니다.\n올바른 API 키를 입력해주세요.")
                sys.exit(1)
            print("API key validation successful")
        except Exception as e:
            QMessageBox.critical(None, "API 연결 오류", 
                               f"API 연결에 실패했습니다:\n{str(e)}")
            sys.exit(1)
        
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
