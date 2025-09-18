#!/usr/bin/env python3
"""
키보드 입력 테스트
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """키보드 입력 테스트"""
    try:
        print("=== 키보드 입력 테스트 ===")
        
        from pynput import keyboard
        import time
        
        def on_press(key):
            print(f"키 눌림: {key}")
        
        def on_release(key):
            print(f"키 릴리즈: {key}")
            if key == keyboard.Key.esc:
                print("ESC 키로 종료")
                return False
        
        print("키보드 입력을 테스트합니다...")
        print("ESC 키를 누르면 종료됩니다.")
        
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
            
    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
