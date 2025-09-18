"""
설정 관리 모듈
JSON 파일을 통한 설정 저장 및 로드
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64

class ConfigManager:
    """설정 파일 관리 클래스"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.key_file = Path("config.key")
        self._cipher = None
        self._load_or_create_key()
    
    def _load_or_create_key(self):
        """암호화 키 로드 또는 생성"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        self._cipher = Fernet(key)
    
    def _encrypt_data(self, data: str) -> str:
        """데이터 암호화"""
        return self._cipher.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        return self._cipher.decrypt(encrypted_data.encode()).decode()
    
    def get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            "api": {
                "gemini_api_key": ""
            },
            "windows": {
                "source": {
                    "x": 100, "y": 100,
                    "width": 300, "height": 200,
                    "visible": True
                },
                "output": {
                    "x": 450, "y": 100,
                    "width": 300, "height": 200,
                    "visible": True
                }
            },
            "translation": {
                "target_language": "ko",
                "capture_interval": 3,
                "model": "gemini-2.5-flash"
            },
            "ui": {
                "click_through_mode": False,
                "output_window_opacity": 0.8,
                "api_call_mode": "manual"
            },
            "hotkeys": {
                "toggle_click_through": "Ctrl+Alt+T",
                "manual_translate": "Ctrl+Shift+T",
                "open_settings": "Ctrl+,"
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if not self.config_file.exists():
            return self.get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # API 키 복호화
            if "api" in config and "gemini_api_key" in config["api"]:
                if config["api"]["gemini_api_key"]:
                    try:
                        config["api"]["gemini_api_key"] = self._decrypt_data(config["api"]["gemini_api_key"])
                    except:
                        # 복호화 실패 시 빈 문자열로 설정
                        config["api"]["gemini_api_key"] = ""
            
            return config
        except Exception as e:
            return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """설정 파일 저장"""
        try:
            # API 키 암호화
            config_copy = config.copy()
            if "api" in config_copy and "gemini_api_key" in config_copy["api"]:
                if config_copy["api"]["gemini_api_key"]:
                    config_copy["api"]["gemini_api_key"] = self._encrypt_data(config_copy["api"]["gemini_api_key"])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_copy, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            return False
    
    def get_setting(self, key_path: str, default=None):
        """중첩된 키 경로로 설정 값 가져오기"""
        config = self.load_config()
        keys = key_path.split('.')
        
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_setting(self, key_path: str, value: Any) -> bool:
        """중첩된 키 경로로 설정 값 설정하기"""
        config = self.load_config()
        keys = key_path.split('.')
        
        # 중첩된 딕셔너리 구조 생성
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        
        return self.save_config(config)
    
    def is_first_run(self) -> bool:
        """첫 실행 여부 확인"""
        return not self.config_file.exists() or not self.get_setting("api.gemini_api_key")
    
    def reset_config(self) -> bool:
        """설정 초기화"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            if self.key_file.exists():
                self.key_file.unlink()
            return True
        except Exception as e:
            return False
