import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import argparse
import os
import threading
import queue
from collections import deque

# 設定 GPU 加速環境變數
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'  # 動態分配 GPU 內存

# GPU 狀態檢測 
has_opencv_gpu = False
has_tf_gpu = False

# 檢查 OpenCV GPU 支援
try:
    cv2_gpu_count = cv2.cuda.getCudaEnabledDeviceCount()
    if cv2_gpu_count > 0:
        has_opencv_gpu = True
        print(f"檢測到 {cv2_gpu_count} 個 OpenCV 支持的 GPU 設備")
    else:
        print("未檢測到 OpenCV 支持的 GPU")
except Exception as e:
    print(f"OpenCV GPU 檢測失敗: {e}")

# 檢查 TensorFlow GPU 支援 (用於 MediaPipe)
try:
    # 延遲導入 TensorFlow，僅用於檢測
    import tensorflow as tf
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        has_tf_gpu = True
        print(f"檢測到 {len(gpus)} 個 TensorFlow 支持的 GPU 設備")
        # 防止 TensorFlow 佔用所有 GPU 內存
        for gpu in gpus:
            try:
                tf.config.experimental.set_memory_growth(gpu, True)
            except:
                # 有些環境下可能不支持動態內存分配
                print(f"無法為 GPU {gpu} 設置動態內存分配")
    else:
        print("未檢測到 TensorFlow 支持的 GPU")
except Exception as e:
    print(f"TensorFlow GPU 檢測失敗: {e}")

# 設定 MediaPipe 手部追蹤
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 防止 pyautogui 移出螢幕邊界時引發異常
pyautogui.FAILSAFE = False

# 設定螢幕尺寸
screen_width, screen_height = pyautogui.size()
print(f"螢幕解析度: {screen_width} x {screen_height}")

# 相機影像處理區域的大小比例
CAMERA_AREA_RATIO = 0.6

# 手勢設定
class Gestures:
    # 閾值：判斷手指是否彎曲的距離比例
    FINGER_BENT_THRESHOLD = 0.3
    
    # 點擊動作判斷的時間閾值(秒)
    CLICK_TIME_THRESHOLD = 0.2
    
    # 手勢定義
    MOVE = "move"          # 食指伸直，其他手指彎曲
    LEFT_CLICK = "left click"  # 食指和中指伸直並快速合併
    RIGHT_CLICK = "right click"  # 食指和大拇指伸直並快速碰觸
    SCROLL_UP = "scroll up"     # 所有手指伸直向上移動
    SCROLL_DOWN = "scroll down"   # 所有手指伸直向下移動
    DRAG = "drag"          # 食指和中指伸直保持固定距離

class AirMouse:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        # 設定較低的相機解析度以降低延遲
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # 設定相機的緩衝大小為1，減少延遲
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.prev_hand_landmarks = None
        self.smoothing_factor = 0.5  # 基礎平滑因子
        self.adaptive_smoothing = True  # 是否使用自適應平滑
        self.min_smoothing = 0.2  # 最小平滑值（更靈敏）
        self.max_smoothing = 0.8  # 最大平滑值（更穩定）
        
        self.prev_gesture = None
        self.gesture_start_time = 0
        self.is_dragging = False
        
        # 控制畫面預覽的變數
        self.show_preview = True
        
        # 處理頻率控制 (ms)
        self.frame_process_interval = 20
        self.last_process_time = 0
        
        # 低功耗模式 - 降低精確度以提高效能
        self.low_power_mode = False
        
        # GPU 加速相關設定
        self.use_gpu = True  # 是否嘗試使用 GPU
        self.opencv_gpu_available = has_opencv_gpu  # 全局變數
        self.tf_gpu_available = has_tf_gpu  # 全局變數
        
        # 手勢狀態追蹤
        self.prev_fingers_up = [0, 0, 0, 0, 0]
        self.finger_gesture_history = []
        self.history_length = 5
        
        # 多執行緒處理相關
        self.frame_queue = queue.Queue(maxsize=1)  # 限制隊列大小為1，確保使用最新影格
        self.result_queue = queue.Queue(maxsize=1)  # 處理結果隊列
        self.processing_thread_active = False
        self.processing_thread = None
        
        # 滑鼠座標平滑處理
        self.position_history = deque(maxlen=3)  # 保存最近幾個滑鼠位置
        
        # 初始化手部檢測，啟用 GPU 加速
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3,
            model_complexity=0)
    
    def get_finger_up_status(self, hand_landmarks):
        """判斷五指是否伸直"""
        fingers_up = [0, 0, 0, 0, 0]  # 大拇指, 食指, 中指, 無名指, 小指
        
        # 大拇指判斷 (基於大拇指尖與大拇指關節的水平位置)
        if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
            fingers_up[0] = 1
        
        # 其他四指判斷 (基於指尖與第二關節的垂直位置)
        finger_tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                      mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
        finger_pips = [mp_hands.HandLandmark.INDEX_FINGER_PIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
                      mp_hands.HandLandmark.RING_FINGER_PIP, mp_hands.HandLandmark.PINKY_PIP]
        
        for i in range(4):
            if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[finger_pips[i]].y:
                fingers_up[i+1] = 1
        
        return fingers_up
    
    def detect_gesture(self, hand_landmarks, frame_shape):
        """檢測手勢類型"""
        fingers_up = self.get_finger_up_status(hand_landmarks)
        
        # 保存手勢歷史以平滑判斷
        self.finger_gesture_history.append(fingers_up)
        if len(self.finger_gesture_history) > self.history_length:
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
            
            if distance < Gestures.FINGER_BENT_THRESHOLD:  # 手指接近，表示點擊
                if self.prev_gesture != Gestures.LEFT_CLICK:
                    self.gesture_start_time = current_time
                
                if current_time - self.gesture_start_time > Gestures.CLICK_TIME_THRESHOLD:
                    gesture = Gestures.LEFT_CLICK
            else:
                gesture = Gestures.DRAG  # 手指分開，表示拖曳
        
        # 食指和大拇指都伸直: 可能是右鍵點擊
        elif stable_fingers_up == [1, 1, 0, 0, 0]:
            # 計算食指和大拌指的距離
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            distance = np.sqrt((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)
            
            if distance < Gestures.FINGER_BENT_THRESHOLD:  # 手指接近，表示右鍵點擊
                if self.prev_gesture != Gestures.RIGHT_CLICK:
                    self.gesture_start_time = current_time
                
                if current_time - self.gesture_start_time > Gestures.CLICK_TIME_THRESHOLD:
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
    
    def control_mouse(self, hand_landmarks, frame_shape, gesture):
        """根據手的位置和手勢控制滑鼠"""
        # 獲取食指尖端的位置
        index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # 將攝像頭畫面座標映射到螢幕座標
        # 使用攝像頭中心區域作為交互區域
        cam_width, cam_height = frame_shape[1], frame_shape[0]
        margin_x = cam_width * (1 - CAMERA_AREA_RATIO) / 2
        margin_y = cam_height * (1 - CAMERA_AREA_RATIO) / 2
        
        # 檢查是否在交互區域內
        in_area_x = margin_x < index_finger.x * cam_width < (cam_width - margin_x)
        in_area_y = margin_y < index_finger.y * cam_height < (cam_height - margin_y)
        
        if in_area_x and in_area_y:
            # 將攝像頭中心區域映射至全螢幕
            screen_x = screen_width * (index_finger.x * cam_width - margin_x) / (cam_width * CAMERA_AREA_RATIO)
            screen_y = screen_height * (index_finger.y * cam_height - margin_y) / (cam_height * CAMERA_AREA_RATIO)
            
            # 確保座標在螢幕範圍內
            screen_x = max(0, min(screen_width - 1, screen_x))
            screen_y = max(0, min(screen_height - 1, screen_y))
            
            # 平滑移動滑鼠
            current_x, current_y = pyautogui.position()
            target_x = int(current_x + (screen_x - current_x) * self.smoothing_factor)
            target_y = int(current_y + (screen_y - current_y) * self.smoothing_factor)
            
            # 處理各種手勢
            if gesture == Gestures.MOVE:
                if self.is_dragging:
                    self.is_dragging = False
                    pyautogui.mouseUp()
                pyautogui.moveTo(target_x, target_y)
            
            elif gesture == Gestures.LEFT_CLICK:
                pyautogui.click(target_x, target_y)
            
            elif gesture == Gestures.RIGHT_CLICK:
                pyautogui.rightClick(target_x, target_y)
            
            elif gesture == Gestures.DRAG:
                pyautogui.moveTo(target_x, target_y)
                if not self.is_dragging:
                    self.is_dragging = True
                    pyautogui.mouseDown()
            
            elif gesture == Gestures.SCROLL_UP:
                pyautogui.scroll(5)  # 向上滾動
            
            elif gesture == Gestures.SCROLL_DOWN:
                pyautogui.scroll(-5)  # 向下滾動
    
    def run(self):
        """運行Air Mouse主程式"""
        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    print("無法讀取攝影機畫面")
                    break
                
                current_time = time.time() * 1000  # 轉換為毫秒
                should_process = (current_time - self.last_process_time) >= self.frame_process_interval
                
                # 只在應該處理的影格上執行手部檢測，降低 CPU/GPU 使用率
                if should_process:
                    self.last_process_time = current_time
                      # 使用 GPU 處理（如果可用並啟用）
                    if self.use_gpu and self.opencv_gpu_available:
                        try:
                            # 使用 OpenCV CUDA 優化處理
                            # 將影像上傳到 GPU
                            gpu_frame = cv2.cuda_GpuMat()
                            gpu_frame.upload(frame)
                            
                            # 可選 GPU 優化：調整大小以加快處理速度
                            # 如果需要更高效能，可以取消下面的註釋，但精確度會略有降低
                            #gpu_resized = cv2.cuda.resize(gpu_frame, (320, 240))
                            #frame_processed = gpu_resized.download()
                            
                            # 從 GPU 下載處理後的影像
                            frame_processed = gpu_frame.download()
                            
                            # 將BGR轉換為RGB用於MediaPipe處理
                            rgb_frame = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
                            
                        except Exception as e:
                            print(f"GPU 處理錯誤：{e}，切換到 CPU 模式")
                            self.opencv_gpu_available = False  # 標記為不可用，避免重複嘗試
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    else:
                        # 常規 CPU 處理
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # MediaPipe 將自動使用 TensorFlow GPU 加速 (如果可用)
                    
                    # MediaPipe 手部檢測（自動使用 TensorFlow 的 GPU 加速）
                    results = self.hands.process(rgb_frame)
                    
                    # 只有當show_preview為True時才處理和顯示畫面
                    if self.show_preview:
                        # 繪製交互區域
                        frame_h, frame_w, _ = frame.shape
                        margin_x = int(frame_w * (1 - CAMERA_AREA_RATIO) / 2)
                        margin_y = int(frame_h * (1 - CAMERA_AREA_RATIO) / 2)
                        cv2.rectangle(frame, 
                                    (margin_x, margin_y), 
                                    (frame_w - margin_x, frame_h - margin_y), 
                                    (0, 255, 0), 2)
                    
                    if results.multi_hand_landmarks:
                        # 只處理第一隻手
                        hand_landmarks = results.multi_hand_landmarks[0]
                        
                        # 只有當show_preview為True時才在畫面上繪製手部標記點
                        if self.show_preview:
                            mp_drawing.draw_landmarks(
                                frame,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())
                        
                        # 檢測手勢
                        gesture = self.detect_gesture(hand_landmarks, frame.shape)
                        
                        # 根據手勢控制滑鼠
                        if gesture:
                            self.control_mouse(hand_landmarks, frame.shape, gesture)
                            
                            # 只有當show_preview為True時才在畫面上顯示當前手勢
                            if self.show_preview:
                                cv2.putText(frame, f"gesture: {gesture}", (10, 30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    # 只有當show_preview為True時才顯示畫面
                    if self.show_preview:
                        frame_h, frame_w, _ = frame.shape
                        fps = int(1000 / self.frame_process_interval)
                        cv2.putText(frame, f"FPS: ~{fps}", (frame_w - 120, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, "esc: exit \nP:switch preview", (10, frame_h - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.imshow('Air Mouse', frame)
                
                # 檢測按鍵，不需要與處理頻率同步
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC鍵
                    break
                elif key == ord('p') or key == ord('P'):  # P鍵切換預覽
                    self.show_preview = not self.show_preview
                    if not self.show_preview:
                        cv2.destroyWindow('Air Mouse')
                    print(f"畫面預覽: {'開啟' if self.show_preview else '關閉'}")
                elif key == ord('+'):  # 增加處理頻率
                    self.frame_process_interval = max(10, self.frame_process_interval - 5)
                    print(f"處理頻率: 約 {int(1000/self.frame_process_interval)} FPS")
                elif key == ord('-'):  # 減少處理頻率
                    self.frame_process_interval = min(100, self.frame_process_interval + 5)
                    print(f"處理頻率: 約 {int(1000/self.frame_process_interval)} FPS")
        
        finally:
            # 釋放資源
            self.cap.release()
            cv2.destroyAllWindows()
            self.hands.close()
            if self.is_dragging:
                pyautogui.mouseUp()  # 確保拖曳動作結束

if __name__ == "__main__":
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="Air Mouse - 使用手勢控制滑鼠")
    parser.add_argument('--no-preview', action='store_true', help='啟動時不顯示預覽畫面 (提升效能)')
    parser.add_argument('--fps', type=int, default=50, help='設定處理頻率 (10-100 之間，數值越小越流暢但CPU負擔越重)')
    parser.add_argument('--no-gpu', action='store_true', help='禁用 GPU 加速 (在 GPU 出現問題時使用)')
    args = parser.parse_args()
    
    print("啟動Air Mouse...")
    print("請將手放在攝像頭前的桌面上")
    print("- 只伸出食指：移動滑鼠")
    print("- 食指和中指伸直並靠近：左鍵點擊")
    print("- 食指和大拇指伸直並靠近：右鍵點擊")
    print("- 食指和中指伸直保持距離：拖曳")
    print("- 五指伸直上下移動：滾動")
    print("- 按ESC鍵退出")
    print("- 按P鍵切換畫面預覽（關閉預覽可提升效能）")
    print("- 按+/-鍵增加/減少處理頻率（影響效能和反應速度）")
    
    air_mouse = AirMouse()
    # 設定處理頻率 (轉換為處理間隔毫秒)
    fps = max(10, min(100, args.fps))  # 確保FPS在10-100範圍內
    air_mouse.frame_process_interval = int(1000 / fps)
    print(f"處理頻率: 約 {fps} FPS")
    
    if args.no_preview:
        air_mouse.show_preview = False
        print("已啟動高效能模式（無預覽）")
    if args.no_gpu:
        air_mouse.use_gpu = False
        print("已禁用 GPU 加速，使用 CPU 模式運行")
    else:
        if air_mouse.opencv_gpu_available:
            print("已啟用 OpenCV GPU 加速")
        if air_mouse.tf_gpu_available:
            print("已啟用 MediaPipe/TensorFlow GPU 加速")
        if not (air_mouse.opencv_gpu_available or air_mouse.tf_gpu_available):
            print("未檢測到可用的 GPU 加速，使用 CPU 模式運行")
    air_mouse.run()