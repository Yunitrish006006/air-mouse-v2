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
    MOVE = "move"
    LEFT_CLICK = "left click"
    RIGHT_CLICK = "right click"
    SCROLL_UP = "scroll up"
    SCROLL_DOWN = "scroll down"
    DRAG = "drag"

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
        self.prev_gesture = None
        self.gesture_start_time = 0
        self.finger_gesture_history = []
        
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
        """檢測手勢類型"""
        fingers_up = self.get_finger_up_status(hand_landmarks)
        
        # 保存手勢歷史以平滑判斷
        self.finger_gesture_history.append(fingers_up)
        if len(self.finger_gesture_history) > GESTURE_HISTORY_LENGTH:
            self.finger_gesture_history.pop(0)
        
        # 基於最近幾幀計算穩定的手勢狀態
        stable_fingers_up = [0, 0, 0, 0, 0]
        for i in range(5):
            count_up = sum(history[i] for history in self.finger_gesture_history)
            if count_up > len(self.finger_gesture_history) / 2:
                stable_fingers_up[i] = 1
        
        # 判斷基本手勢
        current_time = time.time()
        gesture = None
        
        # 只有食指伸直: 移動模式
        if stable_fingers_up == [0, 1, 0, 0, 0]:
            gesture = Gestures.MOVE
            
        # 食指和中指都伸直: 可能是左鍵點擊或拖曳
        elif stable_fingers_up == [0, 1, 1, 0, 0]:
            # 計算食指和中指的距離
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            distance = np.sqrt((index_tip.x - middle_tip.x)**2 + (index_tip.y - middle_tip.y)**2)
            
            if distance < FINGER_BENT_THRESHOLD:  # 手指接近，表示點擊
                if self.prev_gesture != Gestures.LEFT_CLICK:
                    self.gesture_start_time = current_time
                
                if current_time - self.gesture_start_time > CLICK_TIME_THRESHOLD:
                    gesture = Gestures.LEFT_CLICK
            else:
                gesture = Gestures.DRAG  # 手指分開，表示拖曳
        
        # 食指和大拇指都伸直: 可能是右鍵點擊
        elif stable_fingers_up == [1, 1, 0, 0, 0]:
            # 計算食指和大拇指的距離
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            distance = np.sqrt((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)
            
            if distance < FINGER_BENT_THRESHOLD:  # 手指接近，表示右鍵點擊
                if self.prev_gesture != Gestures.RIGHT_CLICK:
                    self.gesture_start_time = current_time
                
                if current_time - self.gesture_start_time > CLICK_TIME_THRESHOLD:
                    gesture = Gestures.RIGHT_CLICK
            else:
                gesture = Gestures.MOVE  # 預設為移動模式
        
        # 所有手指伸直: 可能是滾動
        elif stable_fingers_up == [1, 1, 1, 1, 1]:
            if self.prev_hand_landmarks:
                # 計算手部垂直移動方向
                curr_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                prev_y = self.prev_hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                
                if curr_y < prev_y - 0.01:
                    gesture = Gestures.SCROLL_UP
                elif curr_y > prev_y + 0.01:
                    gesture = Gestures.SCROLL_DOWN
        
        # 更新前一個手勢和手部地標
        self.prev_gesture = gesture
        self.prev_hand_landmarks = hand_landmarks
        
        return gesture
    
    def process_frame(self, rgb_frame):
        """處理影格並返回手部檢測結果"""
        return self.hands.process(rgb_frame)
    
    def close(self):
        """釋放資源"""
        if hasattr(self, 'hands'):
            self.hands.close()
