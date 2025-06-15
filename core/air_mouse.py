"""
Air Mouse 主要功能模組
"""
import cv2
import time
import pyautogui
from collections import deque
import sys
import os

# 添加 utils 模組到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .config import *
from .gpu_detector import GPUDetector
from .gestures import GestureDetector, Gestures, mp_hands, mp_drawing, mp_drawing_styles
from utils.image_processing import ImageProcessor

class MouseController:
    """滑鼠控制器"""
    
    def __init__(self, smoothing_factor=DEFAULT_SMOOTHING_FACTOR):
        self.smoothing_factor = smoothing_factor
        self.is_dragging = False
        self.position_history = deque(maxlen=3)
    
    def control_mouse(self, hand_landmarks, frame_shape, gesture):
        """根據手的位置和手勢控制滑鼠"""
        # 獲取食指尖端的位置
        index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # 將攝像頭畫面座標映射到螢幕座標
        cam_width, cam_height = frame_shape[1], frame_shape[0]
        margin_x = cam_width * (1 - CAMERA_AREA_RATIO) / 2
        margin_y = cam_height * (1 - CAMERA_AREA_RATIO) / 2
        
        # 檢查是否在交互區域內
        in_area_x = margin_x < index_finger.x * cam_width < (cam_width - margin_x)
        in_area_y = margin_y < index_finger.y * cam_height < (cam_height - margin_y)
        
        if in_area_x and in_area_y:
            # 將攝像頭中心區域映射至全螢幕
            screen_x = SCREEN_WIDTH * (index_finger.x * cam_width - margin_x) / (cam_width * CAMERA_AREA_RATIO)
            screen_y = SCREEN_HEIGHT * (index_finger.y * cam_height - margin_y) / (cam_height * CAMERA_AREA_RATIO)
            
            # 確保座標在螢幕範圍內
            screen_x = max(0, min(SCREEN_WIDTH - 1, screen_x))
            screen_y = max(0, min(SCREEN_HEIGHT - 1, screen_y))
            
            # 平滑移動滑鼠
            current_x, current_y = pyautogui.position()
            target_x = int(current_x + (screen_x - current_x) * self.smoothing_factor)
            target_y = int(current_y + (screen_y - current_y) * self.smoothing_factor)
            
            # 處理各種手勢
            self._handle_gesture(gesture, target_x, target_y)
    
    def _handle_gesture(self, gesture, x, y):
        """處理手勢動作"""
        if gesture == Gestures.MOVE:
            if self.is_dragging:
                self.is_dragging = False
                pyautogui.mouseUp()
            pyautogui.moveTo(x, y)
        
        elif gesture == Gestures.LEFT_CLICK:
            pyautogui.click(x, y)
        
        elif gesture == Gestures.RIGHT_CLICK:
            pyautogui.rightClick(x, y)
        
        elif gesture == Gestures.DRAG:
            pyautogui.moveTo(x, y)
            if not self.is_dragging:
                self.is_dragging = True
                pyautogui.mouseDown()
        
        elif gesture == Gestures.SCROLL_UP:
            pyautogui.scroll(5)
        
        elif gesture == Gestures.SCROLL_DOWN:
            pyautogui.scroll(-5)
    
    def cleanup(self):
        """清理資源"""
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

class AirMouse:
    """Air Mouse 主要功能類"""
    
    def __init__(self):
        # 初始化攝像頭
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
        
        # 初始化組件
        self.gpu_detector = GPUDetector()
        self.gesture_detector = GestureDetector()
        self.mouse_controller = MouseController()
        self.image_processor = ImageProcessor()
        
        # 控制參數
        self.show_preview = True
        self.use_gpu = True
        self.frame_process_interval = DEFAULT_FRAME_PROCESS_INTERVAL
        self.last_process_time = 0
        
        # 畫面方向控制
        self.frame_rotation = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # 平滑參數
        self.smoothing_factor = DEFAULT_SMOOTHING_FACTOR
        self.adaptive_smoothing = True
        self.min_smoothing = MIN_SMOOTHING
        self.max_smoothing = MAX_SMOOTHING
        
        # 低功耗模式
        self.low_power_mode = False
    
    @property
    def opencv_gpu_available(self):
        return self.gpu_detector.opencv_gpu_available
    
    @property
    def tf_gpu_available(self):
        return self.gpu_detector.tf_gpu_available
    
    def adjust_frame_orientation(self, frame):
        """調整畫面方向"""
        return self.image_processor.adjust_frame_orientation(
            frame, self.frame_rotation, self.flip_horizontal, self.flip_vertical
        )
    
    def adjust_hand_landmarks_for_rotation(self, hand_landmarks, original_shape, rotated_shape):
        """調整手部特徵點座標"""
        return self.image_processor.adjust_hand_landmarks_for_rotation(
            hand_landmarks, original_shape, rotated_shape,
            self.frame_rotation, self.flip_horizontal, self.flip_vertical
        )
    
    def process_frame(self, frame):
        """處理單個影格"""
        current_time = time.time() * 1000
        should_process = (current_time - self.last_process_time) >= self.frame_process_interval
        
        if not should_process:
            return frame, None
        
        self.last_process_time = current_time
        
        # 儲存原始畫面形狀
        original_shape = frame.shape
        
        # 調整畫面方向
        frame = self.adjust_frame_orientation(frame)
        rotated_shape = frame.shape
        
        # GPU 處理
        rgb_frame, gpu_success = self.image_processor.process_frame_with_gpu(
            frame, self.use_gpu and self.opencv_gpu_available
        )
        
        if not gpu_success and self.use_gpu:
            self.gpu_detector.opencv_gpu_available = False
        
        # 手部檢測
        results = self.gesture_detector.process_frame(rgb_frame)
        
        # 繪製交互區域
        if self.show_preview:
            self.image_processor.draw_interaction_area(frame, CAMERA_AREA_RATIO)
        
        # 處理手勢
        gesture = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # 調整手部特徵點座標
            if self.frame_rotation != 0 or self.flip_horizontal or self.flip_vertical:
                hand_landmarks = self.adjust_hand_landmarks_for_rotation(
                    hand_landmarks, original_shape, rotated_shape
                )
            
            # 繪製手部標記點
            if self.show_preview:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
            
            # 檢測手勢
            gesture = self.gesture_detector.detect_gesture(hand_landmarks, frame.shape)
            
            # 控制滑鼠
            if gesture:
                self.mouse_controller.control_mouse(hand_landmarks, frame.shape, gesture)
        
        # 繪製信息文字
        if self.show_preview:
            fps = int(1000 / self.frame_process_interval)
            self.image_processor.draw_info_text(
                frame, fps, self.frame_rotation, 
                self.flip_horizontal, self.flip_vertical, gesture
            )
        
        return frame, gesture
    
    def run(self):
        """運行 Air Mouse（命令行模式）"""
        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    print("無法讀取攝影機畫面")
                    break
                
                frame, gesture = self.process_frame(frame)
                
                if self.show_preview:
                    cv2.imshow('Air Mouse', frame)
                
                # 檢測按鍵
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC鍵
                    break
                elif key == ord('p') or key == ord('P'):
                    self.show_preview = not self.show_preview
                    if not self.show_preview:
                        cv2.destroyWindow('Air Mouse')
                    print(f"畫面預覽: {'開啟' if self.show_preview else '關閉'}")
                elif key == ord('+'):
                    self.frame_process_interval = max(10, self.frame_process_interval - 5)
                    print(f"處理頻率: 約 {int(1000/self.frame_process_interval)} FPS")
                elif key == ord('-'):
                    self.frame_process_interval = min(100, self.frame_process_interval + 5)
                    print(f"處理頻率: 約 {int(1000/self.frame_process_interval)} FPS")
                elif key == ord('r') or key == ord('R'):
                    self.frame_rotation = (self.frame_rotation + 90) % 360
                    print(f"畫面旋轉: {self.frame_rotation}度")
                elif key == ord('h') or key == ord('H'):
                    self.flip_horizontal = not self.flip_horizontal
                    print(f"水平翻轉: {'開啟' if self.flip_horizontal else '關閉'}")
                elif key == ord('v') or key == ord('V'):
                    self.flip_vertical = not self.flip_vertical
                    print(f"垂直翻轉: {'開啟' if self.flip_vertical else '關閉'}")
                elif key == ord('0'):
                    self.frame_rotation = 0
                    self.flip_horizontal = False
                    self.flip_vertical = False
                    print("已重置畫面方向")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理資源"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        if hasattr(self, 'gesture_detector'):
            self.gesture_detector.close()
        if hasattr(self, 'mouse_controller'):
            self.mouse_controller.cleanup()
