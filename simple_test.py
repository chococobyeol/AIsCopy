#!/usr/bin/env python3
"""
AIsCopy 간단 테스트 버전
기본 기능만 테스트
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """간단한 테스트"""
    try:
        print("=== AIsCopy 간단 테스트 ===")
        
        # PySide6 테스트
        print("1. PySide6 로드 테스트...")
        from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
        from PySide6.QtCore import Qt
        print("   ✓ PySide6 로드 성공")
        
        # 기본 창 생성
        print("2. 기본 창 생성 테스트...")
        app = QApplication(sys.argv)
        
        window = QWidget()
        window.setWindowTitle("AIsCopy 테스트")
        window.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        label = QLabel("AIsCopy 테스트 창")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        button = QPushButton("테스트 버튼")
        layout.addWidget(button)
        
        window.setLayout(layout)
        window.show()
        
        print("   ✓ 창 생성 및 표시 성공")
        
        # 단축키 테스트
        print("3. 단축키 테스트...")
        from utils.hotkey_manager import HotkeyManager
        
        hotkey_manager = HotkeyManager()
        
        def test_callback():
            print("   ✓ 단축키 작동!")
        
        hotkey_manager.register_hotkey("ctrl+alt+t", test_callback, "테스트 단축키")
        hotkey_manager.start_listening()
        
        print("   ✓ 단축키 등록 완료 (Ctrl+Alt+T 눌러보세요)")
        
        print("\n=== 테스트 완료 ===")
        print("Ctrl+Alt+T를 눌러서 단축키가 작동하는지 확인하세요!")
        print("창을 닫으면 프로그램이 종료됩니다.")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
