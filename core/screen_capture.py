"""
화면 캡처 모듈
mss 라이브러리를 사용한 고성능 화면 캡처
"""

import mss
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import time
from utils.logger import logger

class ScreenCapture:
    """화면 캡처 클래스"""
    
    def __init__(self):
        logger.info("화면 캡처 모듈 초기화 시작")
        try:
            self.sct = mss.mss()
            self.last_capture = None
            self.last_capture_time = 0
            logger.info("화면 캡처 모듈 초기화 완료")
        except Exception as e:
            logger.error(f"화면 캡처 모듈 초기화 실패: {e}")
            raise
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        지정된 영역을 캡처
        
        Args:
            x, y: 캡처할 영역의 좌상단 좌표
            width, height: 캡처할 영역의 크기
        
        Returns:
            캡처된 이미지 (numpy array) 또는 None
        """
        logger.debug(f"화면 캡처 시도: x={x}, y={y}, width={width}, height={height}")
        try:
            # mss는 1부터 시작하는 좌표를 사용
            monitor = {
                "top": y,
                "left": x,
                "width": width,
                "height": height
            }
            
            logger.debug(f"모니터 설정: {monitor}")
            
            # 스레드 안전을 위해 새로운 mss 인스턴스 생성
            with mss.mss() as sct:
                # 화면 캡처
                screenshot = sct.grab(monitor)
                logger.debug(f"스크린샷 크기: {screenshot.size}")
                
                # PIL Image로 변환
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # numpy array로 변환
            img_array = np.array(img)
            
            # 캡처 정보 저장
            self.last_capture = img_array
            self.last_capture_time = time.time()
            
            logger.debug(f"화면 캡처 성공: {img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"화면 캡처 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            return None
    
    def capture_window_region(self, window_rect: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        창 영역을 캡처 (x, y, width, height)
        
        Args:
            window_rect: (x, y, width, height) 튜플
        
        Returns:
            캡처된 이미지 (numpy array) 또는 None
        """
        x, y, width, height = window_rect
        return self.capture_region(x, y, width, height)
    
    def get_last_capture(self) -> Optional[np.ndarray]:
        """마지막 캡처된 이미지 반환"""
        return self.last_capture
    
    def get_last_capture_time(self) -> float:
        """마지막 캡처 시간 반환"""
        return self.last_capture_time
    
    def capture_all_monitors(self) -> list:
        """모든 모니터 캡처"""
        screenshots = []
        for monitor in self.sct.monitors[1:]:  # 첫 번째는 모든 모니터 정보
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            screenshots.append(np.array(img))
        return screenshots
    
    def get_monitor_info(self) -> list:
        """모니터 정보 반환"""
        return self.sct.monitors[1:]  # 첫 번째는 모든 모니터 정보
    
    def close(self):
        """리소스 정리"""
        if hasattr(self, 'sct'):
            self.sct.close()
