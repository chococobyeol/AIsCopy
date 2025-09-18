#!/usr/bin/env python3
"""
AIsCopy 간단한 테스트 버전
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """간단한 테스트"""
    try:
        print("AIsCopy 테스트 시작...")
        
        # PySide6 테스트
        from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
        from PySide6.QtCore import Qt
        
        print("PySide6 로드 성공!")
        
        # 간단한 창 생성
        app = QApplication(sys.argv)
        
        window = QMainWindow()
        window.setWindowTitle("AIsCopy 테스트")
        window.setFixedSize(400, 300)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("AIsCopy가 정상적으로 실행됩니다!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        button = QPushButton("종료")
        button.clicked.connect(app.quit)
        layout.addWidget(button)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        window.show()
        
        print("창이 표시되었습니다. '종료' 버튼을 눌러주세요.")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
