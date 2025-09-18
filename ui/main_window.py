"""
메인 윈도우 모듈
앱의 메인 진입점 및 전체 제어
"""

from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                               QLabel, QPushButton, QMessageBox, QApplication, QDialog)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont

from utils.config_manager import ConfigManager
from utils.hotkey_manager import HotkeyManager
from utils.logger import logger
from core.screen_capture import ScreenCapture
from core.image_processor import ImageProcessor
from core.translation_engine import TranslationEngine
from ui.overlay_windows import SourceWindow, OutputWindow
from ui.settings_dialog import SettingsDialog

class TranslationWorker(QThread):
    """번역 작업을 위한 별도 스레드"""
    translation_completed = Signal(str)
    translation_failed = Signal(str)
    
    def __init__(self, translation_engine, image):
        super().__init__()
        self.translation_engine = translation_engine
        self.image = image
    
    def run(self):
        try:
            translated_text = self.translation_engine.translate_image(self.image)
            if translated_text:
                self.translation_completed.emit(translated_text)
            else:
                self.translation_failed.emit("번역 결과가 없습니다.")
        except Exception as e:
            self.translation_failed.emit(f"번역 오류: {str(e)}")

class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""
    
    def __init__(self):
        super().__init__()
        logger.info("메인 윈도우 초기화 시작")
        
        try:
            # 설정 관리자
            self.config_manager = ConfigManager()
            logger.info("설정 관리자 초기화 완료")
            
            # 핵심 모듈들
            self.screen_capture = ScreenCapture()
            logger.info("화면 캡처 모듈 초기화 완료")
            
            self.image_processor = ImageProcessor()
            logger.info("이미지 처리 모듈 초기화 완료")
            
            self.translation_engine = None
            self.hotkey_manager = HotkeyManager()
            logger.info("단축키 관리 모듈 초기화 완료")
            
            # 오버레이 창들
            self.source_window = None
            self.output_window = None
            
            # 타이머
            self.capture_timer = QTimer()
            self.capture_timer.timeout.connect(self.capture_and_translate)
            
            # 상태
            self.is_running = False
            self.click_through_mode = False
            self.translation_worker = None
            
            # 번역 엔진 초기화 시도
            self.initialize_translation_engine()
            
            # 첫 실행 확인
            if self.config_manager.is_first_run():
                logger.info("첫 실행 - 초기 설정 화면 표시")
                self.show_initial_setup()
            else:
                logger.info("일반 실행 - 메인 인터페이스 표시")
                self.show_main_interface()
                
        except Exception as e:
            logger.error(f"메인 윈도우 초기화 실패: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            raise
    
    def initialize_translation_engine(self):
        """번역 엔진 초기화"""
        logger.info("번역 엔진 초기화 시도")
        try:
            config = self.config_manager.load_config()
            api_key = config.get("api", {}).get("gemini_api_key", "")
            
            if api_key:
                logger.info("API 키 발견 - 번역 엔진 초기화")
                self.translation_engine = TranslationEngine(api_key)
                
                target_lang = config.get("translation", {}).get("target_language", "ko")
                self.translation_engine.set_target_language(target_lang)
                
                model = config.get("translation", {}).get("model", "gemini-2.5-flash")
                self.translation_engine.set_model(model)
                logger.info(f"번역 엔진 초기화 완료 - 언어: {target_lang}, 모델: {model}")
            else:
                logger.warning("API 키가 설정되지 않음 - 번역 엔진 초기화 건너뜀")
                
        except Exception as e:
            logger.error(f"번역 엔진 초기화 실패: {e}")
    
    def show_initial_setup(self):
        """초기 설정 화면 표시"""
        self.setWindowTitle("AIsCopy - 초기 설정")
        self.setFixedSize(500, 400)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 제목
        title_label = QLabel("AIsCopy 초기 설정")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # 설명
        desc_label = QLabel("번역 도구를 사용하기 위해 필요한 설정을 완료해주세요.")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # 설정 버튼
        setup_button = QPushButton("설정 시작")
        setup_button.clicked.connect(self.start_setup)
        setup_button.setMinimumHeight(40)
        layout.addWidget(setup_button)
        
        # 취소 버튼
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.close)
        cancel_button.setMinimumHeight(40)
        layout.addWidget(cancel_button)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # 설정 대화상자 열기
        self.open_settings()
    
    def start_setup(self):
        """설정 시작"""
        self.open_settings()
    
    def show_main_interface(self):
        """메인 인터페이스 표시"""
        logger.info("메인 인터페이스 표시 시작")
        self.setWindowTitle("AIsCopy")
        self.setFixedSize(400, 200)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # 상태 표시
        status_label = QLabel("번역 도구가 준비되었습니다")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFont(QFont("Arial", 14))
        layout.addWidget(status_label)
        
        # 현재 설정 표시
        config = self.config_manager.load_config()
        settings_text = f"""
현재 설정:
• 목표 언어: {config.get('translation', {}).get('target_language', 'ko')}
• 모델: {config.get('translation', {}).get('model', 'gemini-2.5-flash')}
• 호출 모드: {config.get('ui', {}).get('api_call_mode', 'manual')}
        """
        
        settings_label = QLabel(settings_text.strip())
        settings_label.setAlignment(Qt.AlignCenter)
        settings_label.setWordWrap(True)
        layout.addWidget(settings_label)
        
        layout.addStretch()
        
        # 버튼들
        button_layout = QHBoxLayout()
        
        start_button = QPushButton("시작하기")
        start_button.clicked.connect(self.start_translation)
        start_button.setMinimumHeight(40)
        button_layout.addWidget(start_button)
        
        settings_button = QPushButton("설정")
        settings_button.clicked.connect(self.open_settings)
        settings_button.setMinimumHeight(40)
        button_layout.addWidget(settings_button)
        
        exit_button = QPushButton("종료")
        exit_button.clicked.connect(self.close)
        exit_button.setMinimumHeight(40)
        button_layout.addWidget(exit_button)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # 단축키 등록
        self.register_hotkeys()
        
        # 이미지 처리기 설정
        threshold = 0.95  # 기본값
        self.image_processor.set_threshold(threshold)
        
        logger.info("메인 인터페이스 표시 완료")
    
    
    def register_hotkeys(self):
        """단축키 등록"""
        config = self.config_manager.load_config()
        hotkeys = config.get("hotkeys", {})
        
        # 클릭-스루 토글
        click_through_key = hotkeys.get("toggle_click_through", "Ctrl+Alt+T")
        self.hotkey_manager.register_hotkey(
            click_through_key, 
            self.toggle_click_through_mode,
            "클릭-스루 모드 토글"
        )
        
        # 번역 실행
        translate_key = hotkeys.get("manual_translate", "Ctrl+Shift+T")
        self.hotkey_manager.register_hotkey(
            translate_key,
            self.manual_translate,
            "수동 번역 실행"
        )
        
        # 설정 열기
        settings_key = hotkeys.get("open_settings", "Ctrl+,")
        self.hotkey_manager.register_hotkey(
            settings_key,
            self.open_settings,
            "설정 열기"
        )
        
        # 단축키 리스너 시작
        self.hotkey_manager.start_listening()
    
    def open_settings(self):
        """설정 대화상자 열기"""
        logger.info("설정 대화상자 열기 요청 - Ctrl+, 단축키 감지됨")
        try:
            # 번역 중지
            if self.capture_timer.isActive():
                self.capture_timer.stop()
                logger.info("설정창 열기 - 번역 중지")
            
            # 번역 워커 중지
            if self.translation_worker and self.translation_worker.isRunning():
                self.translation_worker.terminate()
                self.translation_worker.wait()
                logger.info("설정창 열기 - 번역 워커 중지")
            
            dialog = SettingsDialog(self.config_manager, self)
            dialog.settings_changed.connect(self.on_settings_changed)
            result = dialog.exec()
            
            # 설정 완료 후 메인 인터페이스로 전환
            if result == QDialog.Accepted:
                logger.info("설정 저장 완료 - 메인 인터페이스로 전환")
                self.show_main_interface()
            else:
                logger.info("설정 취소됨")
                # 설정 취소 시 번역 재시작
                if self.is_running:
                    config = self.config_manager.load_config()
                    interval = config.get("translation", {}).get("capture_interval", 3) * 1000
                    self.capture_timer.start(interval)
                    logger.info("설정 취소 - 번역 재시작")
        except Exception as e:
            logger.error(f"설정 대화상자 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
    def on_settings_changed(self, config):
        """설정 변경 시 호출"""
        # 번역 엔진 재초기화
        api_key = config.get("api", {}).get("gemini_api_key", "")
        if api_key:
            self.translation_engine = TranslationEngine(api_key)
            
            target_lang = config.get("translation", {}).get("target_language", "ko")
            self.translation_engine.set_target_language(target_lang)
            
            model = config.get("translation", {}).get("model", "gemini-2.5-flash")
            self.translation_engine.set_model(model)
        
        # 단축키 재등록
        self.hotkey_manager.stop_listening()
        self.hotkey_manager.clear_all_hotkeys()
        self.register_hotkeys()
        
        # 번역이 실행 중이었다면 재시작
        if self.is_running:
            # 기존 타이머 중지
            if self.capture_timer.isActive():
                self.capture_timer.stop()
            
            # 새로운 간격으로 타이머 재시작
            interval = config.get("translation", {}).get("capture_interval", 3) * 1000
            logger.info(f"설정 변경 후 번역 재시작 - 간격: {interval}ms")
            self.capture_timer.start(interval)
    
    def start_translation(self):
        """번역 시작"""
        logger.info("번역 시작 요청")
        
        try:
            if not self.translation_engine:
                logger.warning("번역 엔진이 초기화되지 않음 - API 키 설정 필요")
                QMessageBox.warning(self, "번역 엔진 오류", "API 키가 설정되지 않았습니다.\n설정에서 API 키를 입력해주세요.")
                return
            
            logger.info("오버레이 창 생성 시작")
            # 오버레이 창 생성
            self.create_overlay_windows()
            
            # 캡처 타이머 시작
            config = self.config_manager.load_config()
            interval = config.get("translation", {}).get("capture_interval", 3) * 1000
            api_mode = config.get("ui", {}).get("api_call_mode", "manual")
            logger.info(f"번역 시작 - 간격: {interval}ms, API 모드: {api_mode}")
            self.capture_timer.start(interval)
            
            self.is_running = True
            logger.info("메인 창 최소화")
            self.showMinimized()  # 메인 창 최소화 (숨기지 않음)
            
            logger.info("번역 시작 완료")
            
        except Exception as e:
            logger.error(f"번역 시작 실패: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            QMessageBox.critical(self, "번역 시작 오류", f"번역을 시작할 수 없습니다:\n{e}")
    
    def create_overlay_windows(self):
        """오버레이 창 생성"""
        logger.info("오버레이 창 생성 시작")
        config = self.config_manager.load_config()
        
        # 번역 대상 창
        logger.info("번역 대상 창 생성 중...")
        self.source_window = SourceWindow()
        source_config = config.get("windows", {}).get("source", {})
        self.source_window.set_window_rect(
            source_config.get("x", 100),
            source_config.get("y", 100),
            source_config.get("width", 300),
            source_config.get("height", 200)
        )
        self.source_window.show()
        logger.info("번역 대상 창 표시 완료")
        
        # 번역 출력 창
        logger.info("번역 출력 창 생성 중...")
        self.output_window = OutputWindow()
        output_config = config.get("windows", {}).get("output", {})
        self.output_window.set_window_rect(
            output_config.get("x", 450),
            output_config.get("y", 100),
            output_config.get("width", 300),
            output_config.get("height", 200)
        )
        
        # 투명도 설정
        opacity = config.get("ui", {}).get("output_window_opacity", 0.8)
        self.output_window.set_opacity(opacity)
        logger.info(f"번역 출력 창 투명도 설정: {opacity}")
        
        self.output_window.show()
        logger.info("번역 출력 창 표시 완료")
        
        # 창이 제대로 표시되는지 확인 및 강제 표시
        if not self.source_window.isVisible():
            logger.warning("번역 대상 창이 표시되지 않음 - 강제 표시")
            self.source_window.setVisible(True)
            self.source_window.raise_()
            self.source_window.activateWindow()
            self.source_window.setWindowState(Qt.WindowActive)
        
        if not self.output_window.isVisible():
            logger.warning("번역 출력 창이 표시되지 않음 - 강제 표시")
            self.output_window.setVisible(True)
            self.output_window.raise_()
            self.output_window.activateWindow()
            self.output_window.setWindowState(Qt.WindowActive)
        
        # 창을 화면 중앙에 강제 배치
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        
        # 번역 대상 창을 화면 왼쪽에
        self.source_window.move(50, 50)
        self.source_window.raise_()
        
        # 번역 출력 창을 화면 오른쪽에
        self.output_window.move(screen.width() - 350, 50)
        self.output_window.raise_()
        
        logger.info(f"창 위치 강제 설정 - 소스: {self.source_window.pos()}, 출력: {self.output_window.pos()}")
        
        # 창 위치 변경 시 설정 저장
        self.source_window.position_changed.connect(self.save_window_positions)
        self.source_window.size_changed.connect(self.save_window_positions)
        self.output_window.position_changed.connect(self.save_window_positions)
        self.output_window.size_changed.connect(self.save_window_positions)
        
        logger.info("오버레이 창 생성 및 표시 완료")
    
    def save_window_positions(self):
        """창 위치 저장"""
        if not self.source_window or not self.output_window:
            return
        
        config = self.config_manager.load_config()
        
        # 번역 대상 창 위치 저장
        source_rect = self.source_window.get_window_rect()
        config["windows"]["source"] = {
            "x": source_rect[0],
            "y": source_rect[1],
            "width": source_rect[2],
            "height": source_rect[3],
            "visible": True
        }
        
        # 번역 출력 창 위치 저장
        output_rect = self.output_window.get_window_rect()
        config["windows"]["output"] = {
            "x": output_rect[0],
            "y": output_rect[1],
            "width": output_rect[2],
            "height": output_rect[3],
            "visible": True
        }
        
        self.config_manager.save_config(config)
    
    def capture_and_translate(self):
        """화면 캡처 및 번역"""
        if not self.source_window or not self.translation_engine:
            return
        
        # API 호출 모드 확인
        config = self.config_manager.load_config()
        api_call_mode = config.get("ui", {}).get("api_call_mode", "manual")
        
        logger.debug(f"API 호출 모드 확인: {api_call_mode}")
        logger.debug(f"전체 설정: {config}")
        
        if api_call_mode == "manual":
            logger.debug("수동 모드 - 자동 번역 건너뜀")
            return
        
        # 창이 드래그 중이거나 리사이즈 중이면 캡처 건너뛰기
        if self.source_window.is_dragging:
            logger.debug("창 드래그 중 - 캡처 건너뜀")
            return
            
        if self.source_window.is_resizing:
            logger.debug("창 리사이즈 중 - 캡처 건너뜀")
            return
        
        # 번역 대상 영역 캡처
        source_rect = self.source_window.get_window_rect()
        image = self.screen_capture.capture_window_region(source_rect)
        
        if image is None:
            return
        
        # 변화 감지
        if not self.image_processor.has_changed(image):
            return
        
        # 비동기 번역 실행
        if self.translation_engine:
            self.start_translation_worker(image)
    
    def start_translation_worker(self, image):
        """번역 워커 시작"""
        if self.translation_worker and self.translation_worker.isRunning():
            return  # 이미 번역 중이면 건너뛰기
        
        self.translation_worker = TranslationWorker(self.translation_engine, image)
        self.translation_worker.translation_completed.connect(self.on_translation_completed)
        self.translation_worker.translation_failed.connect(self.on_translation_failed)
        self.translation_worker.start()
    
    def on_translation_completed(self, translated_text):
        """번역 완료 처리"""
        if self.output_window:
            self.output_window.update_translation_result(translated_text)
        logger.info(f"번역 완료: {translated_text}")
    
    def on_translation_failed(self, error_message):
        """번역 실패 처리"""
        logger.error(f"번역 실패: {error_message}")
    
    def toggle_click_through_mode(self):
        """클릭-스루 모드 토글"""
        self.click_through_mode = not self.click_through_mode
        logger.info(f"클릭-스루 모드 토글: {self.click_through_mode} - Ctrl+Alt+T 단축키 감지됨")
        
        if self.source_window:
            self.source_window.set_click_through_mode(self.click_through_mode)
        if self.output_window:
            self.output_window.set_click_through_mode(self.click_through_mode)
    
    def manual_translate(self):
        """수동 번역 실행"""
        logger.info("수동 번역 실행 요청 - Ctrl+Shift+T 단축키 감지됨")
        
        try:
            if not self.source_window:
                logger.warning("수동 번역 실패 - 번역 대상 창이 없음")
                return
                
            if not self.translation_engine:
                logger.warning("수동 번역 실패 - 번역 엔진이 없음")
                return
            
            # 번역 대상 영역 캡처
            source_rect = self.source_window.get_window_rect()
            logger.debug(f"수동 번역 - 캡처 영역: {source_rect}")
            image = self.screen_capture.capture_window_region(source_rect)
            
            if image is None:
                logger.warning("수동 번역 실패 - 이미지 캡처 실패")
                return
            
            logger.info("수동 번역 - 이미지 캡처 성공, 번역 시작")
            # 비동기 번역 실행
            self.start_translation_worker(image)
                
        except Exception as e:
            logger.error(f"수동 번역 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        # 리소스 정리
        if self.capture_timer.isActive():
            self.capture_timer.stop()
        
        if self.hotkey_manager:
            self.hotkey_manager.stop_listening()
        
        if self.screen_capture:
            self.screen_capture.close()
        
        # 번역 워커 중지
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.terminate()
            self.translation_worker.wait()
        
        # 창 위치 저장
        self.save_window_positions()
        
        # 오버레이 창 닫기
        if self.source_window:
            self.source_window.close()
        if self.output_window:
            self.output_window.close()
        
        event.accept()
