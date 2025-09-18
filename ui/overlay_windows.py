"""
오버레이 창 UI 모듈
PySide6를 사용한 투명 오버레이 창 구현
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QApplication, QMenu, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QFont
import sys
from utils.logger import logger

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
        self._drag_pos = None
        self._resizing = False
        self._resize_direction = None
        self._border_width = 15
        
        self.setup_window()
        self.setup_ui()
        self.setup_style()
    
    def setup_window(self):
        """창 기본 설정"""
        # 항상 위에 표시 + 프레임리스 + 크기 조절 가능
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.Window
        )
        
        # 투명 배경
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 마우스 추적 활성화 (크기 조절을 위해)
        self.setMouseTracking(True)
        logger.debug("마우스 추적 활성화됨")
        
        # 기본 크기 (최소 크기로 설정)
        self.setMinimumSize(300, 200)
        self.resize(300, 200)
        
        # 크기 조절 가능하도록 설정 (프레임리스 창에서)
        self.setSizePolicy(
            QSizePolicy.Expanding, 
            QSizePolicy.Expanding
        )
        
        # 창 제목
        title = "번역 대상" if self.window_type == "source" else "번역 출력"
        self.setWindowTitle(title)
    
    def setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 마진 제거
        
        if self.window_type == "source":
            # 번역 대상 창은 제목 표시줄과 내용 모두
            self.title_bar = self.create_title_bar()
            layout.addWidget(self.title_bar)
            
            content_area = self.create_content_area()
            layout.addWidget(content_area)
        else:
            # 번역 출력 창은 제목 표시줄과 내용 모두
            self.title_bar = self.create_title_bar()
            layout.addWidget(self.title_bar)
            
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
        
        title_bar.setLayout(layout)
        
        # 제목 표시줄에서도 드래그 가능하도록 마우스 이벤트 전파
        title_bar.mousePressEvent = self.mousePressEvent
        title_bar.mouseMoveEvent = self.mouseMoveEvent
        title_bar.mouseReleaseEvent = self.mouseReleaseEvent
        
        return title_bar
    
    def create_content_area(self) -> QFrame:
        """내용 영역 생성"""
        content_area = QFrame()
        content_area.setObjectName("content_area")  # CSS 선택자를 위해 objectName 설정
        if self.window_type == "source":
            # 번역 대상 창은 명확한 테두리 (더 얇고 대비가 좋은 색상)
            content_area.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border: 2px solid rgba(0, 150, 255, 200);
                    border-radius: 5px;
                }
            """)
        else:
            # 번역 출력 창은 반투명
            content_area.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 80);
                    border: 1px solid rgba(100, 100, 100, 150);
                    border-radius: 5px;
                }
            """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        if self.window_type == "source":
            # 번역 대상 창 - 텍스트 제거 (번역 결과에 포함되지 않도록)
            # self.source_label = QLabel("번역 대상 영역")
            # self.source_label.setAlignment(Qt.AlignCenter)
            # self.source_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
            # layout.addWidget(self.source_label)
            pass  # 들여쓰기 오류 방지
        else:
            # 번역 출력 창 - 텍스트 색상을 검은색으로 변경
            self.output_label = QLabel("번역 결과가 여기에 표시됩니다")
            self.output_label.setAlignment(Qt.AlignCenter)
            self.output_label.setStyleSheet("color: black; font-size: 14px; font-weight: bold; background-color: rgba(255, 255, 255, 0.8); padding: 5px; border-radius: 3px;")
            self.output_label.setWordWrap(True)
            layout.addWidget(self.output_label)
        
        content_area.setLayout(layout)
        
        # 내용 영역에서도 드래그 가능하도록 마우스 이벤트 전파
        content_area.mousePressEvent = self.mousePressEvent
        content_area.mouseMoveEvent = self.mouseMoveEvent
        content_area.mouseReleaseEvent = self.mouseReleaseEvent
        
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
                    border: 2px solid rgba(0, 150, 255, 200);
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
            # 완전 투명하게 (테두리만 보이도록)
            if self.window_type == "source":
                self.setStyleSheet("""
                    QWidget {
                        background-color: transparent;
                    }
                    QFrame#content_area {
                        background-color: transparent;
                        border: 2px solid rgba(0, 150, 255, 150);
                        border-radius: 5px;
                    }
                """)
                # 제목 표시줄 숨기기
                if hasattr(self, 'title_bar'):
                    self.title_bar.hide()
            else:
                self.setStyleSheet("""
                    QWidget {
                        background-color: transparent;
                    }
                    QFrame#content_area {
                        background-color: rgba(0, 0, 0, 30);
                        border: 1px solid rgba(100, 100, 100, 100);
                        border-radius: 5px;
                    }
                """)
                # 제목 표시줄 숨기기
                if hasattr(self, 'title_bar'):
                    self.title_bar.hide()
        else:
            # 마우스 이벤트 활성화
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            # 원래 투명도로
            self.setup_style()
            # 제목 표시줄 다시 보이기
            if hasattr(self, 'title_bar'):
                self.title_bar.show()
        
        self.mode_changed.emit(enabled)
    
    def set_opacity(self, opacity: float):
        """투명도 설정 (0.0 ~ 1.0)"""
        self.setWindowOpacity(opacity)
    
    def update_translation_result(self, text: str):
        """번역 결과 업데이트 (출력 창만)"""
        if self.window_type == "output" and hasattr(self, 'output_label'):
            self.output_label.setText(text)
            # 텍스트 색상 유지
            self.output_label.setStyleSheet("color: black; font-size: 14px; font-weight: bold; background-color: rgba(255, 255, 255, 0.8); padding: 5px; border-radius: 3px;")
    
    
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.LeftButton and not self.click_through_mode:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._resize_direction = self._get_resize_direction(event.pos())
            self._resizing = self._resize_direction is not None
            
            logger.debug(f"마우스 클릭: pos={event.pos()}, resize_direction={self._resize_direction}, resizing={self._resizing}")
            event.accept()
        elif event.button() == Qt.RightButton and not self.click_through_mode:
            # 오른쪽 클릭 메뉴
            self.show_context_menu(event.globalPosition().toPoint())
            event.accept()
        else:
            # 클릭-스루 모드가 아닐 때도 이벤트 처리
            event.accept()
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if not self.click_through_mode:
            if self._resizing and self._resize_direction:
                self._resize_window(event.globalPosition().toPoint())
            elif self._drag_pos:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                self.position_changed.emit(self.x(), self.y())
            else:
                self._update_cursor(event.pos())
            event.accept()
        else:
            # 클릭-스루 모드일 때도 이벤트 처리
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            self._resizing = False
            self._resize_direction = None
            self.setCursor(Qt.ArrowCursor)
            logger.debug("마우스 릴리즈")
            event.accept()
    
    def resizeEvent(self, event):
        """크기 변경 이벤트"""
        super().resizeEvent(event)
        # 크기 변경 시 시그널 발생
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
    
    def get_content_rect(self):
        """내용 영역의 위치와 크기 반환 (제목 표시줄 제외)"""
        if self.window_type == "source":
            # 제목 표시줄 높이(30px)를 제외한 내용 영역만
            title_height = 30
            content_y = self.y() + title_height
            content_height = self.height() - title_height
            return (self.x(), content_y, self.width(), content_height)
        else:
            # 출력 창은 번역 대상에 포함되지 않음
            return None
    
    def _get_resize_direction(self, pos):
        """크기 조절 방향 감지 (꼭지점 4개 + 모서리 4개)"""
        rect = self.rect()
        x, y = pos.x(), pos.y()
        w, h = rect.width(), rect.height()
        
        logger.debug(f"크기 조절 감지: pos=({x}, {y}), size=({w}, {h}), border={self._border_width}")
        
        # 꼭지점 감지 (우선순위) - 정확한 조건
        if x < self._border_width and y < self._border_width:
            return 'top_left'
        elif x > w - self._border_width and y < self._border_width:
            return 'top_right'
        elif x < self._border_width and y > h - self._border_width:
            return 'bottom_left'
        elif x > w - self._border_width and y > h - self._border_width:
            return 'bottom_right'
        # 모서리 감지
        elif x < self._border_width:
            return 'left'
        elif x > w - self._border_width:
            return 'right'
        elif y < self._border_width:
            return 'top'
        elif y > h - self._border_width:
            return 'bottom'
        else:
            return None
    
    def set_window_rect(self, x: int, y: int, width: int, height: int):
        """창의 위치와 크기 설정"""
        self.move(x, y)
        self.resize(width, height)
    
    def _resize_window(self, global_pos):
        """창 크기 조절 (예제 코드 기반)"""
        rect = self.geometry()
        logger.debug(f"크기 조절 중: {self._resize_direction}, global_pos={global_pos}")
        
        if self._resize_direction == 'top_left':
            rect.setTopLeft(global_pos)
        elif self._resize_direction == 'top_right':
            rect.setTopRight(global_pos)
        elif self._resize_direction == 'bottom_left':
            rect.setBottomLeft(global_pos)
        elif self._resize_direction == 'bottom_right':
            rect.setBottomRight(global_pos)
        elif self._resize_direction == 'left':
            rect.setLeft(global_pos.x())
        elif self._resize_direction == 'right':
            rect.setRight(global_pos.x())
        elif self._resize_direction == 'top':
            rect.setTop(global_pos.y())
        elif self._resize_direction == 'bottom':
            rect.setBottom(global_pos.y())
        
        # 최소 크기 보장
        if rect.width() >= self.minimumWidth() and rect.height() >= self.minimumHeight():
            self.setGeometry(rect)
            logger.debug(f"크기 조절 적용: {rect}")
        else:
            logger.debug(f"최소 크기 미달로 크기 조절 무시: {rect.width()}x{rect.height()}")
    
    def _update_cursor(self, pos):
        """커서 모양 업데이트 (예제 코드 기반)"""
        direction = self._get_resize_direction(pos)
        logger.debug(f"커서 업데이트: {direction} at {pos}")
        
        if direction in ['top_left', 'bottom_right']:
            self.setCursor(Qt.SizeFDiagCursor)
        elif direction in ['top_right', 'bottom_left']:
            self.setCursor(Qt.SizeBDiagCursor)
        elif direction in ['left', 'right']:
            self.setCursor(Qt.SizeHorCursor)
        elif direction in ['top', 'bottom']:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def show_context_menu(self, pos):
        """오른쪽 클릭 메뉴 표시"""
        menu = QMenu(self)
        
        # 메뉴 스타일 설정 (흰색 배경, 검은색 텍스트)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                background-color: white;
                color: black;
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ddd;
                margin: 5px 0;
            }
        """)
        
        # 투명 모드 토글
        toggle_action = menu.addAction("투명 모드 토글")
        toggle_action.triggered.connect(self.toggle_click_through)
        
        menu.addSeparator()
        
        # 설정 열기
        settings_action = menu.addAction("설정 열기")
        settings_action.triggered.connect(self.open_settings)
        
        # 최소화
        minimize_action = menu.addAction("최소화")
        minimize_action.triggered.connect(self.showMinimized)
        
        menu.addSeparator()
        
        # 종료
        exit_action = menu.addAction("종료")
        exit_action.triggered.connect(self.exit_application)
        
        menu.exec(pos)
    
    def toggle_click_through(self):
        """투명 모드 토글"""
        self.set_click_through_mode(not self.click_through_mode)
    
    def open_settings(self):
        """설정 열기"""
        logger.info("설정 열기 요청 - 오버레이 창에서")
        try:
            # 부모 창의 설정 열기 함수 호출
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                # 메인 윈도우 찾기
                for widget in app.allWidgets():
                    if hasattr(widget, 'open_settings') and hasattr(widget, 'config_manager'):
                        logger.info("메인 윈도우 발견 - 설정 열기")
                        widget.open_settings()
                        return
                logger.error("메인 윈도우를 찾을 수 없음")
        except Exception as e:
            logger.error(f"설정 열기 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
    def exit_application(self):
        """애플리케이션 종료"""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.quit()

class SourceWindow(OverlayWindow):
    """번역 대상 창"""
    
    def __init__(self, parent=None):
        super().__init__("source", parent)

class OutputWindow(OverlayWindow):
    """번역 출력 창"""
    
    def __init__(self, parent=None):
        super().__init__("output", parent)
