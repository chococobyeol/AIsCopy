"""
오버레이 창 UI 모듈
PySide6를 사용한 투명 오버레이 창 구현
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QApplication)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
import sys

class OverlayWindow(QWidget):
    """기본 오버레이 창 클래스"""
    
    # 시그널 정의
    position_changed = Signal(int, int)  # x, y
    size_changed = Signal(int, int)      # width, height
    mode_changed = Signal(bool)          # click_through_mode
    
    def __init__(self, window_type: str, parent=None):
        """
        Args:
            window_type: "source" 또는 "output"
        """
        super().__init__(parent)
        self.window_type = window_type
        self.click_through_mode = False
        self.is_dragging = False
        self.drag_position = None
        self.is_resizing = False
        self.resize_start_pos = None
        self.resize_start_size = None
        
        self.setup_window()
        self.setup_ui()
        self.setup_style()
    
    def setup_window(self):
        """창 기본 설정"""
        # 항상 위에 표시
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Window
        )
        
        # 투명 배경
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 기본 크기 (최소 크기로 설정)
        self.setMinimumSize(300, 200)
        self.resize(300, 200)
        
        # 창 제목
        title = "번역 대상" if self.window_type == "source" else "번역 출력"
        self.setWindowTitle(title)
    
    def setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        if self.window_type == "source":
            # 번역 대상 창은 제목 표시줄과 내용 모두
            title_bar = self.create_title_bar()
            layout.addWidget(title_bar)
            
            content_area = self.create_content_area()
            layout.addWidget(content_area)
        else:
            # 번역 출력 창은 제목 표시줄과 내용 모두
            title_bar = self.create_title_bar()
            layout.addWidget(title_bar)
            
            content_area = self.create_content_area()
            layout.addWidget(content_area)
        
        self.setLayout(layout)
    
    def create_title_bar(self) -> QFrame:
        """제목 표시줄 생성"""
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 200);
                border-radius: 5px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 제목
        title_text = "번역 대상" if self.window_type == "source" else "번역 출력"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 최소화 버튼
        min_btn = QPushButton("−")
        min_btn.setFixedSize(20, 20)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)
        
        title_bar.setLayout(layout)
        return title_bar
    
    def create_content_area(self) -> QFrame:
        """내용 영역 생성"""
        content_area = QFrame()
        if self.window_type == "source":
            # 번역 대상 창은 명확한 테두리
            content_area.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border: 3px solid rgba(255, 255, 255, 255);
                    border-radius: 5px;
                }
            """)
        else:
            # 번역 출력 창은 반투명
            content_area.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 50);
                    border: 2px dashed rgba(255, 255, 255, 100);
                    border-radius: 5px;
                }
            """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        if self.window_type == "source":
            # 번역 대상 창 - 제목 표시
            self.source_label = QLabel("번역 대상 영역")
            self.source_label.setAlignment(Qt.AlignCenter)
            self.source_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
            layout.addWidget(self.source_label)
        else:
            # 번역 출력 창
            self.output_label = QLabel("번역 결과가 여기에 표시됩니다")
            self.output_label.setAlignment(Qt.AlignCenter)
            self.output_label.setStyleSheet("color: white; font-size: 14px;")
            self.output_label.setWordWrap(True)
            layout.addWidget(self.output_label)
        
        content_area.setLayout(layout)
        return content_area
    
    def setup_style(self):
        """스타일 설정"""
        if self.window_type == "source":
            # 번역 대상 창은 반투명 배경에 명확한 테두리
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 100);
                }
                QFrame {
                    background-color: transparent;
                    border: 3px solid rgba(255, 255, 255, 255);
                    border-radius: 5px;
                }
                QLabel {
                    color: white;
                    background-color: transparent;
                }
            """)
        else:
            # 번역 출력 창은 반투명
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 80);
                }
            """)
    
    def set_click_through_mode(self, enabled: bool):
        """클릭-스루 모드 설정"""
        self.click_through_mode = enabled
        
        if enabled:
            # 마우스 이벤트 무시
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            # 더 투명하게
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 30);
                }
            """)
        else:
            # 마우스 이벤트 활성화
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            # 원래 투명도로
            self.setup_style()
        
        self.mode_changed.emit(enabled)
    
    def set_opacity(self, opacity: float):
        """투명도 설정 (0.0 ~ 1.0)"""
        self.setWindowOpacity(opacity)
    
    def update_translation_result(self, text: str):
        """번역 결과 업데이트 (출력 창만)"""
        if self.window_type == "output" and hasattr(self, 'output_label'):
            self.output_label.setText(text)
    
    def is_resize_area(self, pos):
        """크기 조절 영역인지 확인"""
        margin = 20
        return (pos.x() >= self.width() - margin and 
                pos.y() >= self.height() - margin)
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.LeftButton and not self.click_through_mode:
            if self.is_resize_area(event.pos()):
                self.is_resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.is_dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            # 클릭-스루 모드가 아닐 때도 이벤트 처리
            event.accept()
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if not self.click_through_mode:
            if self.is_dragging:
                new_pos = event.globalPosition().toPoint() - self.drag_position
                self.move(new_pos)
                self.position_changed.emit(self.x(), self.y())
                event.accept()
            elif self.is_resizing:
                delta = event.globalPosition().toPoint() - self.resize_start_pos
                # QSize 객체 직접 연산 대신 width, height로 계산
                new_width = self.resize_start_size.width() + delta.x()
                new_height = self.resize_start_size.height() + delta.y()
                
                # 최소 크기 보장
                new_width = max(new_width, self.minimumSize().width())
                new_height = max(new_height, self.minimumSize().height())
                
                # 최대 크기 제한 (화면 크기의 80%)
                from PySide6.QtWidgets import QApplication
                screen = QApplication.primaryScreen().geometry()
                max_width = int(screen.width() * 0.8)
                max_height = int(screen.height() * 0.8)
                new_width = min(new_width, max_width)
                new_height = min(new_height, max_height)
                
                self.resize(new_width, new_height)
                # 리사이즈 중에는 시그널 발생하지 않음 (resizeEvent에서 처리)
                event.accept()
            elif self.is_resize_area(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        else:
            # 클릭-스루 모드일 때도 이벤트 처리
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트"""
        if event.button() == Qt.LeftButton:
            if self.is_resizing:
                # 리사이즈 완료 시 시그널 발생
                self.size_changed.emit(self.width(), self.height())
            self.is_dragging = False
            self.is_resizing = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
    
    def resizeEvent(self, event):
        """크기 변경 이벤트"""
        super().resizeEvent(event)
        # 리사이즈 중이 아닐 때만 시그널 발생 (중복 방지)
        if not self.is_resizing:
            self.size_changed.emit(self.width(), self.height())
    
    def paintEvent(self, event):
        """그리기 이벤트"""
        super().paintEvent(event)
        
        if self.window_type == "source":
            # 번역 대상 창에 명확한 테두리 그리기
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 255, 255, 255), 3, Qt.SolidLine))
            painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
            painter.end()  # QPainter 명시적 종료
    
    def get_window_rect(self):
        """창의 위치와 크기 반환"""
        return (self.x(), self.y(), self.width(), self.height())
    
    def set_window_rect(self, x: int, y: int, width: int, height: int):
        """창의 위치와 크기 설정"""
        self.move(x, y)
        self.resize(width, height)

class SourceWindow(OverlayWindow):
    """번역 대상 창"""
    
    def __init__(self, parent=None):
        super().__init__("source", parent)

class OutputWindow(OverlayWindow):
    """번역 출력 창"""
    
    def __init__(self, parent=None):
        super().__init__("output", parent)
