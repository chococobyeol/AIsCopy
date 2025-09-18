#!/usr/bin/env python3
"""
AIsCopy 디버그 버전
상세한 로그와 함께 실행
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for AIsCopy application with debug logging"""
    try:
        print("=== AIsCopy 디버그 모드 시작 ===")
        
        # 로거 초기화
        from utils.logger import logger
        logger.info("AIsCopy 디버그 모드 시작")
        
        # PySide6 테스트
        logger.info("PySide6 모듈 로드 시도...")
        from PySide6.QtWidgets import QApplication
        logger.info("PySide6 모듈 로드 성공")
        
        # 메인 윈도우 로드
        logger.info("메인 윈도우 모듈 로드 시도...")
        from ui.main_window import MainWindow
        logger.info("메인 윈도우 모듈 로드 성공")
        
        # QApplication 생성
        logger.info("QApplication 생성 중...")
        app = QApplication(sys.argv)
        app.setApplicationName("AIsCopy")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AIsCopy")
        logger.info("QApplication 생성 완료")
        
        # 메인 윈도우 생성
        logger.info("메인 윈도우 생성 중...")
        window = MainWindow()
        logger.info("메인 윈도우 생성 완료")
        
        # 윈도우 표시
        logger.info("메인 윈도우 표시 중...")
        window.show()
        logger.info("메인 윈도우 표시 완료")
        
        # 이벤트 루프 시작
        logger.info("이벤트 루프 시작...")
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"모듈 import 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"애플리케이션 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
