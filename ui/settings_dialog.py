"""
설정 대화상자 모듈
통합 설정 UI 구현
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
                               QSlider, QRadioButton, QGroupBox, QFormLayout,
                               QSpinBox, QCheckBox, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from utils.config_manager import ConfigManager
from core.translation_engine import TranslationEngine
from utils.logger import logger

class SettingsDialog(QDialog):
    """설정 대화상자"""
    
    # 시그널 정의
    settings_changed = Signal(dict)  # 설정 변경 시그널
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.translation_engine = None
        
        self.setup_ui()
        self.load_settings()
        self.setup_connections()
    
    def setup_ui(self):
        """UI 구성"""
        self.setWindowTitle("AIsCopy 설정")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_api_tab(), "API")
        self.tab_widget.addTab(self.create_translation_tab(), "번역")
        self.tab_widget.addTab(self.create_window_tab(), "창")
        self.tab_widget.addTab(self.create_hotkey_tab(), "단축키")
        
        layout.addWidget(self.tab_widget)
        
        # 버튼
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.test_button = QPushButton("API 테스트")
        self.test_button.clicked.connect(self.test_api)
        button_layout.addWidget(self.test_button)
        
        self.reset_button = QPushButton("초기화")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        self.apply_button = QPushButton("적용")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("확인")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("취소")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_api_tab(self) -> QWidget:
        """API 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # API 키 설정
        api_group = QGroupBox("Google Gemini API 설정")
        api_layout = QFormLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("API 키를 입력하세요")
        api_layout.addRow("API 키:", self.api_key_edit)
        
        self.test_api_button = QPushButton("연결 테스트")
        self.test_api_button.clicked.connect(self.test_api)
        api_layout.addRow("", self.test_api_button)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # API 상태
        self.api_status_label = QLabel("API 상태: 연결되지 않음")
        self.api_status_label.setStyleSheet("color: red;")
        layout.addWidget(self.api_status_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_translation_tab(self) -> QWidget:
        """번역 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 번역 설정
        translation_group = QGroupBox("번역 설정")
        translation_layout = QFormLayout()
        
        # 목표 언어
        self.target_language_combo = QComboBox()
        languages = {
            "ko": "한국어",
            "en": "영어",
            "ja": "일본어",
            "zh": "중국어",
            "es": "스페인어",
            "fr": "프랑스어",
            "de": "독일어",
            "ru": "러시아어"
        }
        for code, name in languages.items():
            self.target_language_combo.addItem(name, code)
        translation_layout.addRow("목표 언어:", self.target_language_combo)
        
        # 모델 선택
        self.model_group = QGroupBox("번역 모델")
        model_layout = QVBoxLayout()
        
        self.flash_radio = QRadioButton("gemini-2.5-flash (빠름)")
        self.flash_lite_radio = QRadioButton("gemini-2.5-flash-lite (더 빠름)")
        self.flash_radio.setChecked(True)
        
        model_layout.addWidget(self.flash_radio)
        model_layout.addWidget(self.flash_lite_radio)
        self.model_group.setLayout(model_layout)
        translation_layout.addRow("", self.model_group)
        
        # 캡처 간격
        self.capture_interval_spin = QSpinBox()
        self.capture_interval_spin.setRange(1, 60)
        self.capture_interval_spin.setSuffix(" 초")
        self.capture_interval_spin.setValue(3)
        translation_layout.addRow("캡처 간격:", self.capture_interval_spin)
        
        translation_group.setLayout(translation_layout)
        layout.addWidget(translation_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_window_tab(self) -> QWidget:
        """창 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 창 설정
        window_group = QGroupBox("창 설정")
        window_layout = QFormLayout()
        
        # 출력창 투명도
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        
        self.opacity_label = QLabel("80%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        window_layout.addRow("출력창 투명도:", opacity_layout)
        
        # API 호출 모드
        self.api_mode_group = QGroupBox("API 호출 모드")
        mode_layout = QVBoxLayout()
        
        self.auto_mode_radio = QRadioButton("자동 모드 (주기적 번역)")
        self.manual_mode_radio = QRadioButton("수동 모드 (단축키로만 번역)")
        self.manual_mode_radio.setChecked(True)
        
        mode_layout.addWidget(self.auto_mode_radio)
        mode_layout.addWidget(self.manual_mode_radio)
        self.api_mode_group.setLayout(mode_layout)
        window_layout.addRow("", self.api_mode_group)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_hotkey_tab(self) -> QWidget:
        """단축키 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 단축키 설정
        hotkey_group = QGroupBox("단축키 설정")
        hotkey_layout = QFormLayout()
        
        # 클릭-스루 토글
        self.click_through_hotkey_edit = QLineEdit()
        self.click_through_hotkey_edit.setText("Ctrl+Alt+T")
        hotkey_layout.addRow("클릭-스루 토글:", self.click_through_hotkey_edit)
        
        # 번역 실행
        self.translate_hotkey_edit = QLineEdit()
        self.translate_hotkey_edit.setText("Ctrl+Shift+T")
        hotkey_layout.addRow("번역 실행:", self.translate_hotkey_edit)
        
        # 설정 열기
        self.settings_hotkey_edit = QLineEdit()
        self.settings_hotkey_edit.setText("Ctrl+,")
        hotkey_layout.addRow("설정 열기:", self.settings_hotkey_edit)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_connections(self):
        """시그널 연결"""
        pass
    
    def load_settings(self):
        """설정 로드"""
        config = self.config_manager.load_config()
        
        # API 설정
        api_key = config.get("api", {}).get("gemini_api_key", "")
        self.api_key_edit.setText(api_key)
        
        # API 상태 업데이트
        if api_key:
            try:
                from core.translation_engine import TranslationEngine
                engine = TranslationEngine(api_key)
                if engine.test_api_connection():
                    self.api_status_label.setText("API 상태: 연결됨")
                    self.api_status_label.setStyleSheet("color: green;")
                else:
                    self.api_status_label.setText("API 상태: 연결 실패")
                    self.api_status_label.setStyleSheet("color: red;")
            except:
                self.api_status_label.setText("API 상태: 오류")
                self.api_status_label.setStyleSheet("color: red;")
        else:
            self.api_status_label.setText("API 상태: 설정되지 않음")
            self.api_status_label.setStyleSheet("color: orange;")
        
        # 번역 설정
        target_lang = config.get("translation", {}).get("target_language", "ko")
        index = self.target_language_combo.findData(target_lang)
        if index >= 0:
            self.target_language_combo.setCurrentIndex(index)
        
        model = config.get("translation", {}).get("model", "gemini-2.5-flash")
        if model == "gemini-2.5-flash-lite":
            self.flash_lite_radio.setChecked(True)
        else:
            self.flash_radio.setChecked(True)
        
        capture_interval = config.get("translation", {}).get("capture_interval", 3)
        self.capture_interval_spin.setValue(capture_interval)
        
        # 창 설정
        opacity = int(config.get("ui", {}).get("output_window_opacity", 0.8) * 100)
        self.opacity_slider.setValue(opacity)
        
        api_mode = config.get("ui", {}).get("api_call_mode", "manual")
        if api_mode == "auto":
            self.auto_mode_radio.setChecked(True)
        else:
            self.manual_mode_radio.setChecked(True)
        
        # 단축키 설정
        hotkeys = config.get("hotkeys", {})
        self.click_through_hotkey_edit.setText(hotkeys.get("toggle_click_through", "Ctrl+Alt+T"))
        self.translate_hotkey_edit.setText(hotkeys.get("manual_translate", "Ctrl+Shift+T"))
        self.settings_hotkey_edit.setText(hotkeys.get("open_settings", "Ctrl+,"))
    
    def test_api(self):
        """API 연결 테스트"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "경고", "API 키를 입력해주세요.")
            return
        
        try:
            # 번역 엔진 생성 및 테스트
            self.translation_engine = TranslationEngine(api_key)
            if self.translation_engine.test_api_connection():
                self.api_status_label.setText("API 상태: 연결됨")
                self.api_status_label.setStyleSheet("color: green;")
                QMessageBox.information(self, "성공", "API 연결이 성공했습니다!")
            else:
                self.api_status_label.setText("API 상태: 연결 실패")
                self.api_status_label.setStyleSheet("color: red;")
                QMessageBox.warning(self, "실패", "API 연결에 실패했습니다.")
        except Exception as e:
            self.api_status_label.setText("API 상태: 오류")
            self.api_status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "오류", f"API 테스트 중 오류가 발생했습니다:\n{str(e)}")
    
    def apply_settings(self):
        """설정 적용"""
        self.save_settings()
        config = self.config_manager.load_config()
        self.settings_changed.emit(config)
        logger.info("설정 적용 완료")
    
    def accept_settings(self):
        """확인 버튼 클릭"""
        self.apply_settings()
        self.accept()
    
    def save_settings(self):
        """설정 저장"""
        config = self.config_manager.load_config()
        
        # API 설정
        config["api"]["gemini_api_key"] = self.api_key_edit.text().strip()
        
        # 번역 설정
        target_lang = self.target_language_combo.currentData()
        config["translation"]["target_language"] = target_lang
        
        model = "gemini-2.5-flash-lite" if self.flash_lite_radio.isChecked() else "gemini-2.5-flash"
        config["translation"]["model"] = model
        
        config["translation"]["capture_interval"] = self.capture_interval_spin.value()
        
        # 창 설정
        config["ui"]["output_window_opacity"] = self.opacity_slider.value() / 100.0
        
        api_mode = "auto" if self.auto_mode_radio.isChecked() else "manual"
        config["ui"]["api_call_mode"] = api_mode
        
        # 단축키 설정
        config["hotkeys"]["toggle_click_through"] = self.click_through_hotkey_edit.text()
        config["hotkeys"]["manual_translate"] = self.translate_hotkey_edit.text()
        config["hotkeys"]["open_settings"] = self.settings_hotkey_edit.text()
        
        # 설정 저장
        self.config_manager.save_config(config)
    
    def reset_settings(self):
        """설정 초기화"""
        reply = QMessageBox.question(self, "설정 초기화", 
                                   "모든 설정을 기본값으로 초기화하시겠습니까?\n"
                                   "이 작업은 되돌릴 수 없습니다.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # 설정 파일 삭제
                self.config_manager.reset_config()
                
                # UI를 기본값으로 설정
                self.load_default_settings()
                
                QMessageBox.information(self, "초기화 완료", 
                                      "설정이 기본값으로 초기화되었습니다.\n"
                                      "프로그램을 재시작하면 적용됩니다.")
                
            except Exception as e:
                QMessageBox.critical(self, "초기화 오류", 
                                   f"설정 초기화 중 오류가 발생했습니다:\n{str(e)}")
    
    def load_default_settings(self):
        """기본 설정으로 UI 업데이트"""
        # API 설정
        self.api_key_edit.clear()
        
        # 번역 설정
        self.target_language_combo.setCurrentIndex(0)  # 한국어
        self.flash_radio.setChecked(True)
        self.capture_interval_spin.setValue(3)
        
        # 창 설정
        self.opacity_slider.setValue(80)
        self.manual_mode_radio.setChecked(True)
        
        # 단축키 설정
        self.click_through_hotkey_edit.setText("Ctrl+T")
        self.translate_hotkey_edit.setText("Ctrl+Shift+T")
        self.settings_hotkey_edit.setText("Ctrl+,")
