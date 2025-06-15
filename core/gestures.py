"""
手勢檢測和識別模組
"""
import time
import numpy as np
import mediapipe as mp
from .config import FINGER_BENT_THRESHOLD, CLICK_TIME_THRESHOLD, GESTURE_HISTORY_LENGTH

# 設定 MediaPipe 手部追蹤
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class Gestures:
    """手勢定義常數類"""
    MOVE = "move"        # 移動滑鼠
    LEFT_CLICK = "left click"  # 左鍵點擊

class GestureDetector:
    """手勢檢測器"""
    
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3,
            model_complexity=0
        )
        
        self.prev_hand_landmarks = None
        
    def get_finger_up_status(self, hand_landmarks):
        """判斷五指是否伸直"""
        fingers_up = [0, 0, 0, 0, 0]  # 大拇指, 食指, 中指, 無名指, 小指
        
        # 大拇指判斷 (基於大拇指尖與大拇指關節的水平位置)
        if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
            fingers_up[0] = 1
        
        # 其他四指判斷 (基於指尖與第二關節的垂直位置)
        finger_tips = [
            mp_hands.HandLandmark.INDEX_FINGER_TIP, 
            mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            mp_hands.HandLandmark.RING_FINGER_TIP, 
            mp_hands.HandLandmark.PINKY_TIP
        ]
        finger_pips = [
            mp_hands.HandLandmark.INDEX_FINGER_PIP, 
            mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            mp_hands.HandLandmark.RING_FINGER_PIP, 
            mp_hands.HandLandmark.PINKY_PIP
        ]
        
        for i in range(4):
            if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[finger_pips[i]].y:
                fingers_up[i+1] = 1
        
        return fingers_up
    
    def detect_gesture(self, hand_landmarks, frame_shape):
        """超簡化的手勢檢測：只檢測食指位置進行移動"""
        fingers_up = self.get_finger_up_status(hand_landmarks)
        
        # 除錯輸出
        print(f"[DEBUG] 手指狀態: {fingers_up} (拇指,食指,中指,無名指,小指)")
        
        gesture = None
        
        # 檢查是否有食指伸直（移動模式）
        if fingers_up == [1, 0, 1, 1, 1] or fingers_up == [0, 1, 0, 0, 0]:
            gesture = Gestures.MOVE
            print(f"[DEBUG] 移動模式: {fingers_up}")
        
        # 更新前一個手部地標
        self.prev_hand_landmarks = hand_landmarks
        
        return gesture
    
    def process_frame(self, rgb_frame):
        """處理影格並返回手部檢測結果"""
        return self.hands.process(rgb_frame)
    
    def close(self):
        """釋放資源"""
        if hasattr(self, 'hands'):
            self.hands.close()
