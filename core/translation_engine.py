"""
번역 엔진 모듈
Google Gemini API를 사용한 이미지 번역
"""

import google.generativeai as genai
from PIL import Image
import numpy as np
from typing import Optional, Dict, Any

class TranslationEngine:
    """Gemini API를 사용한 번역 엔진"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Google Gemini API 키
        """
        self.api_key = api_key
        self.model_name = "gemini-2.5-flash"
        self.target_language = "ko"
        
        # Gemini API 설정
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def set_model(self, model_name: str):
        """사용할 모델 설정"""
        if model_name in ["gemini-2.5-flash", "gemini-2.5-flash-lite"]:
            self.model_name = model_name
            self.model = genai.GenerativeModel(model_name)
    
    def set_target_language(self, language: str):
        """목표 언어 설정"""
        self.target_language = language
    
    def numpy_to_pil(self, image_array: np.ndarray) -> Image.Image:
        """numpy array를 PIL Image로 변환"""
        return Image.fromarray(image_array.astype(np.uint8))
    
    def translate_image(self, image: np.ndarray, prompt: str = None) -> Optional[str]:
        """
        이미지를 번역
        
        Args:
            image: 번역할 이미지 (numpy array)
            prompt: 사용자 정의 프롬프트 (선택사항)
        
        Returns:
            번역된 텍스트 또는 None
        """
        try:
            # numpy array를 PIL Image로 변환
            pil_image = self.numpy_to_pil(image)
            
            # 기본 프롬프트 설정
            if prompt is None:
                prompt = f"이 이미지의 모든 텍스트를 {self.target_language}로 번역해주세요. UI 요소나 창 제목은 무시하고 실제 콘텐츠 텍스트만 번역해주세요. 번역 결과만 반환해주세요."
            
            # Gemini API 호출
            response = self.model.generate_content([prompt, pil_image])
            
            if response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            from utils.logger import logger
            logger.error(f"번역 엔진 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
            return None
    
    
    def test_api_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            # 간단한 텍스트 생성으로 API 연결 테스트
            response = self.model.generate_content("Hello")
            return response.text is not None
        except Exception as e:
            return False
    
    def get_supported_languages(self) -> Dict[str, str]:
        """지원하는 언어 목록 반환"""
        return {
            "ko": "한국어",
            "en": "영어",
            "ja": "일본어",
            "zh": "중국어",
            "es": "스페인어",
            "fr": "프랑스어",
            "de": "독일어",
            "ru": "러시아어",
            "ar": "아랍어",
            "pt": "포르투갈어"
        }
    
    def create_custom_prompt(self, source_language: str = "auto", 
                           target_language: str = None, 
                           context: str = "") -> str:
        """
        사용자 정의 프롬프트 생성
        
        Args:
            source_language: 원본 언어 (auto는 자동 감지)
            target_language: 목표 언어
            context: 추가 컨텍스트
        
        Returns:
            생성된 프롬프트
        """
        if target_language is None:
            target_language = self.target_language
        
        prompt = f"이 이미지의 모든 텍스트를 {target_language}로 번역해주세요."
        
        if source_language != "auto":
            prompt += f" 원본 언어는 {source_language}입니다."
        
        if context:
            prompt += f" 컨텍스트: {context}"
        
        prompt += " 텍스트만 추출하고 번역 결과만 반환해주세요."
        
        return prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """현재 모델 정보 반환"""
        return {
            "model_name": self.model_name,
            "target_language": self.target_language,
            "api_key_set": bool(self.api_key),
            "supported_languages": list(self.get_supported_languages().keys())
        }
