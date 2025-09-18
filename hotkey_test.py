#!/usr/bin/env python3
"""
단축키 테스트
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """단축키 테스트"""
    try:
        print("=== 단축키 테스트 ===")
        
        from utils.hotkey_manager import HotkeyManager
        import time
        
        def test_callback1():
            print("✓ Ctrl+Alt+T 작동!")
        
        def test_callback2():
            print("✓ Ctrl+Shift+T 작동!")
        
        def test_callback3():
            print("✓ Ctrl+, 작동!")
        
        hotkey_manager = HotkeyManager()
        
        # 단축키 등록
        hotkey_manager.register_hotkey("ctrl+alt+t", test_callback1, "테스트1")
        hotkey_manager.register_hotkey("ctrl+shift+t", test_callback2, "테스트2")
        hotkey_manager.register_hotkey("ctrl+,", test_callback3, "테스트3")
        
        # 리스너 시작
        hotkey_manager.start_listening()
        
        print("단축키 테스트 시작:")
        print("- Ctrl+Alt+T")
        print("- Ctrl+Shift+T") 
        print("- Ctrl+,")
        print("ESC 키를 누르면 종료됩니다.")
        
        # ESC 키로 종료
        from pynput import keyboard
        
        def on_press(key):
            if key == keyboard.Key.esc:
                print("종료 중...")
                hotkey_manager.stop_listening()
                return False
        
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
            
    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
