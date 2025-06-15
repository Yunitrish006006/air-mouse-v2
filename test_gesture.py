#!/usr/bin/env python3
"""
手勢檢測測試
"""
import sys
import os
import cv2
import pyautogui

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import AirMouse

def test_gesture_detection():
    """測試手勢檢測"""
    print("🤚 手勢檢測測試")
    print("=" * 30)
    
    try:
        air_mouse = AirMouse()
        air_mouse.show_preview = True
        print("✅ Air Mouse 初始化成功")
        
        print("\n📷 請將手放在綠色框內")
        print("手勢說明:")
        print("- 只伸食指 = 移動滑鼠")
        print("- 食指+中指 = 點擊/拖曳")
        print("- 按 'q' 退出")
        
        frame_count = 0
        gesture_count = 0
        last_gesture = None
        
        while air_mouse.cap.isOpened():
            success, frame = air_mouse.cap.read()
            if not success:
                break
                
            frame_count += 1
            
            # 處理影格
            processed_frame, gesture = air_mouse.process_frame(frame)
            
            # 檢查手勢變化
            if gesture and gesture != last_gesture:
                gesture_count += 1
                print(f"🎯 檢測到手勢: {gesture} (第 {gesture_count} 次)")
                last_gesture = gesture
                
                # 檢查滑鼠是否實際移動
                if gesture == "move":
                    current_pos = pyautogui.position()
                    print(f"   當前滑鼠位置: {current_pos}")
            
            # 顯示統計
            if frame_count % 60 == 0:  # 每60幀顯示一次
                print(f"📊 處理了 {frame_count} 幀，檢測到 {gesture_count} 次手勢")
            
            # 顯示影像
            cv2.imshow('Gesture Test', processed_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        air_mouse.cleanup()
        cv2.destroyAllWindows()
        
    print(f"\n📊 總結:")
    print(f"- 處理影格: {frame_count}")
    print(f"- 檢測手勢: {gesture_count}")
    
    if gesture_count > 0:
        print("✅ 手勢檢測正常工作")
    else:
        print("❌ 未檢測到任何手勢")

if __name__ == "__main__":
    test_gesture_detection()
