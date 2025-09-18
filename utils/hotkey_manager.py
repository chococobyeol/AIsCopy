"""
단축키 관리 모듈
pynput을 사용한 전역 단축키 관리
"""

from pynput import keyboard
from typing import Dict, Callable, Optional
import threading
import time

class HotkeyManager:
    """전역 단축키 관리 클래스"""
    
    def __init__(self):
        self.hotkeys = {}
        self.listener = None
        self.is_running = False
        self._lock = threading.Lock()
        self.pressed_keys = set()  # 현재 눌린 키들 추적
    
    def register_hotkey(self, key_combination: str, callback: Callable, description: str = ""):
        """
        단축키 등록
        
        Args:
            key_combination: 키 조합 (예: "ctrl+t", "ctrl+shift+t")
            callback: 단축키가 눌렸을 때 실행할 함수
            description: 단축키 설명
        """
        try:
            # 키 조합 파싱
            keys = self._parse_key_combination(key_combination)
            
            with self._lock:
                self.hotkeys[key_combination] = {
                    'keys': keys,
                    'callback': callback,
                    'description': description
                }
            
            from utils.logger import logger
            logger.info(f"단축키 등록 완료: {key_combination} - {description}")
            
        except Exception as e:
            from utils.logger import logger
            logger.error(f"단축키 등록 실패: {key_combination} - {e}")
    
    def unregister_hotkey(self, key_combination: str):
        """단축키 등록 해제"""
        with self._lock:
            if key_combination in self.hotkeys:
                del self.hotkeys[key_combination]
    
    def _parse_key_combination(self, key_combination: str) -> list:
        """키 조합 문자열을 파싱"""
        keys = []
        parts = key_combination.lower().split('+')
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.append(keyboard.Key.ctrl_l)
            elif part == 'alt':
                keys.append(keyboard.Key.alt_l)
            elif part == 'shift':
                keys.append('shift')  # 문자열로 저장
            elif part == 'cmd' or part == 'win':
                keys.append(keyboard.Key.cmd)
            elif len(part) == 1:
                # 단일 문자 키 처리
                if part == 't':
                    keys.append('t')
                elif part == ',':
                    keys.append(',')
                else:
                    keys.append(part)
            else:
                # 특수 키 처리
                special_keys = {
                    'space': keyboard.Key.space,
                    'enter': keyboard.Key.enter,
                    'tab': keyboard.Key.tab,
                    'esc': keyboard.Key.esc,
                    'backspace': keyboard.Key.backspace,
                    'delete': keyboard.Key.delete,
                    'up': keyboard.Key.up,
                    'down': keyboard.Key.down,
                    'left': keyboard.Key.left,
                    'right': keyboard.Key.right,
                    'home': keyboard.Key.home,
                    'end': keyboard.Key.end,
                    'page_up': keyboard.Key.page_up,
                    'page_down': keyboard.Key.page_down,
                    'f1': keyboard.Key.f1,
                    'f2': keyboard.Key.f2,
                    'f3': keyboard.Key.f3,
                    'f4': keyboard.Key.f4,
                    'f5': keyboard.Key.f5,
                    'f6': keyboard.Key.f6,
                    'f7': keyboard.Key.f7,
                    'f8': keyboard.Key.f8,
                    'f9': keyboard.Key.f9,
                    'f10': keyboard.Key.f10,
                    'f11': keyboard.Key.f11,
                    'f12': keyboard.Key.f12,
                }
                
                if part in special_keys:
                    keys.append(special_keys[part])
                else:
                    raise ValueError(f"알 수 없는 키: {part}")
        
        return keys
    
    def _on_press(self, key):
        """키가 눌렸을 때 호출되는 함수"""
        try:
            # 눌린 키 추가
            self.pressed_keys.add(key)
            
            from utils.logger import logger
            logger.debug(f"키 눌림: {key} (현재 눌린 키: {len(self.pressed_keys)}개)")
            
            with self._lock:
                # 키 조합 길이 순으로 정렬 (긴 것부터)
                sorted_hotkeys = sorted(self.hotkeys.items(), 
                                      key=lambda x: len(x[1]['keys']), 
                                      reverse=True)
                
                for key_combination, hotkey_info in sorted_hotkeys:
                    if self._check_key_combination(hotkey_info['keys']):
                        logger.info(f"단축키 매칭: {key_combination} - {hotkey_info['description']}")
                        # Qt 메인 스레드에서 콜백 실행
                        self._execute_callback(hotkey_info['callback'])
                        break
        except Exception as e:
            from utils.logger import logger
            logger.error(f"키 눌림 처리 오류: {e}")
    
    def _on_release(self, key):
        """키가 떼어졌을 때 호출되는 함수"""
        try:
            # 떼어진 키 제거
            self.pressed_keys.discard(key)
        except Exception as e:
            pass
    
    def _check_key_combination(self, required_keys):
        """현재 눌린 키들이 필요한 키 조합과 일치하는지 확인"""
        try:
            # 필요한 키들이 모두 눌려있는지 확인
            for required_key in required_keys:
                found = False
                for pressed_key in self.pressed_keys:
                    if self._keys_match(pressed_key, required_key):
                        found = True
                        break
                if not found:
                    return False
            return True
        except Exception as e:
            return False
    
    def _keys_match(self, pressed_key, required_key):
        """두 키가 같은지 확인"""
        try:
            # 문자열로 비교
            if isinstance(required_key, str):
                # 특수 키 매핑 먼저 확인
                if required_key == 't':
                    pressed_str = str(pressed_key)
                    # '\x14' KeyCode 객체 직접 비교
                    if hasattr(pressed_key, 'char') and pressed_key.char == '\x14':
                        return True
                    elif pressed_str in ['<84>', '\x14', 't', 'T']:
                        return True
                    else:
                        return False
                elif required_key == ',':
                    pressed_str = str(pressed_key)
                    if hasattr(pressed_key, 'char') and pressed_key.char:
                        return pressed_key.char == ','
                    else:
                        return pressed_str in ['<188>', ',']
                elif required_key == 'shift':
                    pressed_str = str(pressed_key)
                    return ('shift' in pressed_str.lower() or 
                            pressed_key == keyboard.Key.shift or
                            'Key.shift' in pressed_str)
                else:
                    # 일반 문자 비교
                    if hasattr(pressed_key, 'char') and pressed_key.char:
                        return pressed_key.char.lower() == required_key.lower()
                    else:
                        pressed_str = str(pressed_key)
                        return pressed_str == required_key
            else:
                return pressed_key == required_key
        except Exception as e:
            return False
    
    def _execute_callback(self, callback):
        """콜백 함수 실행"""
        try:
            from utils.logger import logger
            logger.info("콜백 실행 시도")
            # 직접 실행 (pynput은 이미 별도 스레드에서 실행됨)
            callback()
            logger.info("콜백 실행 완료")
        except Exception as e:
            from utils.logger import logger
            logger.error(f"콜백 실행 오류: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
    def start_listening(self):
        """단축키 리스너 시작"""
        if self.is_running:
            from utils.logger import logger
            logger.warning("단축키 리스너가 이미 실행 중입니다")
            return
        
        try:
            from utils.logger import logger
            logger.info("단축키 리스너 시작")
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.is_running = True
            logger.info(f"등록된 단축키 수: {len(self.hotkeys)}")
            for key, info in self.hotkeys.items():
                logger.info(f"  - {key}: {info['description']}")
            
        except Exception as e:
            from utils.logger import logger
            logger.error(f"단축키 리스너 시작 실패: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
    def stop_listening(self):
        """단축키 리스너 중지"""
        if not self.is_running:
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            self.is_running = False
            pass
        except Exception as e:
            pass
    
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """등록된 단축키 목록 반환"""
        with self._lock:
            return {key: info['description'] for key, info in self.hotkeys.items()}
    
    def clear_all_hotkeys(self):
        """모든 단축키 제거"""
        with self._lock:
            self.hotkeys.clear()
    
    def is_hotkey_registered(self, key_combination: str) -> bool:
        """단축키가 등록되어 있는지 확인"""
        with self._lock:
            return key_combination in self.hotkeys
    
    def __del__(self):
        """소멸자 - 리소스 정리"""
        self.stop_listening()
