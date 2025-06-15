#!/usr/bin/env python3
"""
簡化的滑鼠控制測試
"""
import sys
import os
import cv2
import pyautogui
import time

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import AirMouse

def simple_mouse_test():
    """簡單的滑鼠控制測試"""
    print("🖱️ 簡單滑鼠測試")
    print("=" * 30)
    
    # 測試基本滑鼠功能
    print("1. 測試 PyAutoGUI...")
    try:
        current_pos = pyautogui.position()
        print(f"當前位置: {current_pos}")
        
        # 移動到螢幕中央
        screen_size = pyautogui.size()
        center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
        print(f"移動到中央: ({center_x}, {center_y})")
        pyautogui.moveTo(center_x, center_y, duration=1)
        
        new_pos = pyautogui.position()
        print(f"移動後位置: {new_pos}")
        print("✅ PyAutoGUI 正常工作")
    except Exception as e:
        print(f"❌ PyAutoGUI 錯誤: {e}")
        return
    
    # 測試 Air Mouse
    print("\n2. 測試 Air Mouse...")
    try:
        air_mouse = AirMouse()
        print("✅ Air Mouse 初始化成功")
    except Exception as e:
        print(f"❌ Air Mouse 初始化失敗: {e}")
        return
    
    print("\n3. 開始手勢測試...")
    print("請將手伸入綠色框內，並伸出食指")
    print("按 'q' 退出")
    
    gesture_detected = False
    mouse_moved = False
    
    try:
        while air_mouse.cap.isOpened():
            success, frame = air_mouse.cap.read()
            if not success:
                break
            
            # 處理影格
            processed_frame, gesture = air_mouse.process_frame(frame)
            
            # 檢查手勢
            if gesture and not gesture_detected:
                print(f"✅ 檢測到手勢: {gesture}")
                gesture_detected = True
            
            # 檢查滑鼠是否移動
            if gesture == "move":
                current_mouse_pos = pyautogui.position()
                if not mouse_moved:
                    print(f"🖱️ 滑鼠位置: {current_mouse_pos}")
                    mouse_moved = True
            
            # 顯示影像
            cv2.imshow('Simple Mouse Test', processed_frame)
            
            # 按鍵處理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    except Exception as e:
        print(f"❌ 運行錯誤: {e}")
    finally:
        air_mouse.cleanup()
        cv2.destroyAllWindows()
        
    if gesture_detected:
        print("✅ 手勢檢測正常")
    else:
        print("❌ 未檢測到手勢")
        
    if mouse_moved:
        print("✅ 滑鼠控制正常")
    else:
        print("❌ 滑鼠沒有移動")

if __name__ == "__main__":
    simple_mouse_test()
