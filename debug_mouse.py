#!/usr/bin/env python3
"""
Air Mouse 調試工具 - 檢查滑鼠控制問題
"""
import sys
import os
import cv2
import pyautogui

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import AirMouse
from core.config import CAMERA_AREA_RATIO

def debug_mouse_control():
    """調試滑鼠控制功能"""
    print("🔍 Air Mouse 調試模式")
    print("=" * 50)
    
    # 檢查基本設定
    print(f"PyAutoGUI 安全模式: {pyautogui.FAILSAFE}")
    screen_size = pyautogui.size()
    print(f"螢幕尺寸: {screen_size}")
    current_pos = pyautogui.position()
    print(f"當前滑鼠位置: {current_pos}")
    
    # 測試滑鼠移動
    print("\n🖱️ 測試滑鼠移動...")
    try:
        test_x, test_y = screen_size[0] // 2, screen_size[1] // 2
        print(f"嘗試移動滑鼠到螢幕中央: ({test_x}, {test_y})")
        pyautogui.moveTo(test_x, test_y, duration=1)
        new_pos = pyautogui.position()
        print(f"移動後位置: {new_pos}")
        if abs(new_pos[0] - test_x) < 10 and abs(new_pos[1] - test_y) < 10:
            print("✅ 滑鼠移動測試成功")
        else:
            print("❌ 滑鼠移動測試失敗")
    except Exception as e:
        print(f"❌ 滑鼠移動錯誤: {e}")
    
    # 初始化 Air Mouse
    print("\n🚀 初始化 Air Mouse...")
    try:
        air_mouse = AirMouse()
        air_mouse.show_preview = True
        print("✅ Air Mouse 初始化成功")
    except Exception as e:
        print(f"❌ Air Mouse 初始化失敗: {e}")
        return
    
    print("\n📷 開始攝像頭調試...")
    print("請將手放在綠色框內，並伸出食指")
    print("按 'q' 退出，按 't' 測試滑鼠移動")
    
    frame_count = 0
    gesture_count = 0
    
    try:
        while air_mouse.cap.isOpened():
            success, frame = air_mouse.cap.read()
            if not success:
                print("❌ 無法讀取攝影機畫面")
                break
            
            frame_count += 1
            
            # 處理影格
            processed_frame, gesture = air_mouse.process_frame(frame)
            
            # 統計手勢檢測
            if gesture:
                gesture_count += 1
                print(f"檢測到手勢: {gesture} (第 {gesture_count} 次)")
                  # 檢查食指位置
                if hasattr(air_mouse.gesture_detector, 'prev_hand_landmarks') and air_mouse.gesture_detector.prev_hand_landmarks:
                    hand_landmarks = air_mouse.gesture_detector.prev_hand_landmarks
                    
                    # 導入所需模組
                    from core.gestures import mp_hands
                    index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    
                    # 計算座標
                    cam_width, cam_height = frame.shape[1], frame.shape[0]
                    margin_x = cam_width * (1 - CAMERA_AREA_RATIO) / 2
                    margin_y = cam_height * (1 - CAMERA_AREA_RATIO) / 2
                    
                    finger_x = index_finger.x * cam_width
                    finger_y = index_finger.y * cam_height
                    
                    print(f"  食指位置: ({finger_x:.1f}, {finger_y:.1f})")
                    print(f"  交互區域: x({margin_x:.1f}-{cam_width-margin_x:.1f}), y({margin_y:.1f}-{cam_height-margin_y:.1f})")
                    
                    # 檢查是否在交互區域內
                    in_area_x = margin_x < finger_x < (cam_width - margin_x)
                    in_area_y = margin_y < finger_y < (cam_height - margin_y)
                    print(f"  在交互區域內: x={in_area_x}, y={in_area_y}")
                    
                    if in_area_x and in_area_y:
                        # 計算螢幕座標
                        screen_x = screen_size[0] * (finger_x - margin_x) / (cam_width * CAMERA_AREA_RATIO)
                        screen_y = screen_size[1] * (finger_y - margin_y) / (cam_height * CAMERA_AREA_RATIO)
                        print(f"  映射螢幕座標: ({screen_x:.1f}, {screen_y:.1f})")
            
            # 顯示統計信息
            if frame_count % 30 == 0:  # 每30幀顯示一次
                print(f"📊 影格: {frame_count}, 手勢檢測: {gesture_count}")
            
            # 顯示影像
            cv2.imshow('Air Mouse Debug', processed_frame)
            
            # 按鍵處理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('t'):
                print("🧪 測試滑鼠移動到螢幕中央...")
                center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                print(f"移動到: ({center_x}, {center_y})")
    
    except KeyboardInterrupt:
        print("\n用戶中斷")
    except Exception as e:
        print(f"\n❌ 運行錯誤: {e}")
    finally:
        air_mouse.cleanup()
        cv2.destroyAllWindows()
        print("\n🧹 清理完成")

if __name__ == "__main__":
    debug_mouse_control()
