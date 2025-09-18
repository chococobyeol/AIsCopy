"""
이미지 처리 및 변화 감지 모듈
OpenCV를 사용한 이미지 비교 및 변화 감지
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from skimage.metrics import structural_similarity as ssim

class ImageProcessor:
    """이미지 처리 및 변화 감지 클래스"""
    
    def __init__(self, threshold: float = 0.95):
        """
        Args:
            threshold: 변화 감지 임계값 (0.0 ~ 1.0, 높을수록 민감)
        """
        self.threshold = threshold
        self.previous_image = None
    
    def calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        두 이미지 간의 구조적 유사성 지수(SSIM) 계산
        
        Args:
            img1, img2: 비교할 이미지 (numpy array)
        
        Returns:
            유사성 점수 (0.0 ~ 1.0, 1.0이 완전 동일)
        """
        try:
            # 이미지 크기 통일
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 그레이스케일 변환
            gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            
            # SSIM 계산
            similarity = ssim(gray1, gray2)
            return similarity
            
        except Exception as e:
            return 0.0
    
    def has_changed(self, current_image: np.ndarray) -> bool:
        """
        이전 이미지와 비교하여 변화가 있는지 확인
        
        Args:
            current_image: 현재 이미지 (numpy array)
        
        Returns:
            변화가 있으면 True, 없으면 False
        """
        from utils.logger import logger
        
        if self.previous_image is None:
            self.previous_image = current_image.copy()
            logger.info("첫 번째 이미지 - 변화 감지됨 (API 호출)")
            return True  # 첫 번째 이미지는 항상 변화가 있다고 간주
        
        similarity = self.calculate_similarity(self.previous_image, current_image)
        
        # 임계값보다 낮으면 변화가 있다고 판단
        has_change = similarity < self.threshold
        
        if has_change:
            self.previous_image = current_image.copy()
            logger.info(f"이미지 변화 감지됨 - 유사도: {similarity:.3f} (임계값: {self.threshold}) - API 호출")
        else:
            logger.debug(f"이미지 변화 없음 - 유사도: {similarity:.3f} (임계값: {self.threshold}) - API 호출 건너뜀")
        
        return has_change
    
    def calculate_pixel_difference(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        픽셀 단위 차이 계산
        
        Args:
            img1, img2: 비교할 이미지 (numpy array)
        
        Returns:
            차이 비율 (0.0 ~ 1.0)
        """
        try:
            # 이미지 크기 통일
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 절대 차이 계산
            diff = cv2.absdiff(img1, img2)
            
            # 차이가 있는 픽셀 수 계산
            diff_pixels = np.sum(diff > 30)  # 임계값 30
            
            # 전체 픽셀 수
            total_pixels = img1.shape[0] * img1.shape[1]
            
            # 차이 비율 반환
            return diff_pixels / total_pixels
            
        except Exception as e:
            return 1.0
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        이미지 전처리 (노이즈 제거, 대비 향상 등)
        
        Args:
            image: 전처리할 이미지 (numpy array)
        
        Returns:
            전처리된 이미지 (numpy array)
        """
        try:
            # 가우시안 블러로 노이즈 제거
            blurred = cv2.GaussianBlur(image, (3, 3), 0)
            
            # 대비 향상 (CLAHE)
            lab = cv2.cvtColor(blurred, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            return enhanced
            
        except Exception as e:
            return image
    
    def set_threshold(self, threshold: float):
        """변화 감지 임계값 설정"""
        self.threshold = max(0.0, min(1.0, threshold))
    
    def reset(self):
        """이전 이미지 초기화"""
        self.previous_image = None
    
    def get_image_info(self, image: np.ndarray) -> dict:
        """이미지 정보 반환"""
        if image is None:
            return {}
        
        return {
            "shape": image.shape,
            "dtype": str(image.dtype),
            "min_value": float(np.min(image)),
            "max_value": float(np.max(image)),
            "mean_value": float(np.mean(image))
        }
