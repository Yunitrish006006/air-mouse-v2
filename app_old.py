#!/usr/bin/env python3
"""
Air Mouse - 使用手勢控制滑鼠
主啟動文件
"""
import argparse
import sys
import os

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import AirMouse
from ui import AirMouseUI


def print_welcome_message():
    """顯示歡迎信息"""
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
    print("- 按R鍵旋轉畫面90度（調整手部方向）")
    print("- 按H鍵水平翻轉畫面")
    print("- 按V鍵垂直翻轉畫面")
    print("- 按0鍵重置畫面方向")


def run_cli_mode(args):
    """運行命令行模式"""
    air_mouse = AirMouse()
    
    # 設定處理頻率 (轉換為處理間隔毫秒)
    fps = max(10, min(100, args.fps))
    air_mouse.frame_process_interval = int(1000 / fps)
    print(f"處理頻率: 約 {fps} FPS")
    
    # 設定畫面方向
    air_mouse.frame_rotation = args.rotation
    air_mouse.flip_horizontal = args.flip_h
    air_mouse.flip_vertical = args.flip_v
    if args.rotation != 0 or args.flip_h or args.flip_v:
        print(f"畫面方向設定: 旋轉{args.rotation}度, "
              f"水平翻轉{'開啟' if args.flip_h else '關閉'}, "
              f"垂直翻轉{'開啟' if args.flip_v else '關閉'}")
    
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


def run_gui_mode(args):
    """運行圖形化界面模式"""
    ui = AirMouseUI()
    
    # 從命令行參數設定初始值
    ui.set_initial_settings(
        rotation=args.rotation,
        flip_h=args.flip_h,
        flip_v=args.flip_v,
        fps=max(10, min(100, args.fps)),
        use_gpu=not args.no_gpu
    )
    
    ui.run()


def main():
    """主函數"""
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="Air Mouse - 使用手勢控制滑鼠")
    parser.add_argument('--no-preview', action='store_true', 
                        help='啟動時不顯示預覽畫面 (提升效能)')
    parser.add_argument('--fps', type=int, default=50, 
                        help='設定處理頻率 (10-100 之間，數值越小越流暢但CPU負擔越重)')
    parser.add_argument('--no-gpu', action='store_true', 
                        help='禁用 GPU 加速 (在 GPU 出現問題時使用)')
    parser.add_argument('--rotation', type=int, choices=[0, 90, 180, 270], default=0, 
                        help='設定攝像頭畫面初始旋轉角度 (0, 90, 180, 270)')
    parser.add_argument('--flip-h', action='store_true', 
                        help='啟動時水平翻轉畫面')
    parser.add_argument('--flip-v', action='store_true', 
                        help='啟動時垂直翻轉畫面')
    
    args = parser.parse_args()
    
    print_welcome_message()
    
    # 選擇運行模式
    if args.no_preview:
        run_cli_mode(args)
    else:
        run_gui_mode(args)


if __name__ == "__main__":
    main()
        
        # 根據設定的角度旋轉畫面
        if self.frame_rotation == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif self.frame_rotation == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif self.frame_rotation == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        return frame
    
    def adjust_hand_landmarks_for_rotation(self, hand_landmarks, original_shape, rotated_shape):
        """根據畫面旋轉調整手部特徵點座標"""
        if not hand_landmarks:
            return hand_landmarks
        
        # 創建調整後的手部特徵點
        adjusted_landmarks = type(hand_landmarks)()
        adjusted_landmarks.CopyFrom(hand_landmarks)
        
        orig_h, orig_w = original_shape[:2]
        rot_h, rot_w = rotated_shape[:2]
        
        for i, landmark in enumerate(hand_landmarks.landmark):
            x, y = landmark.x, landmark.y
            
            # 根據翻轉調整座標
            if self.flip_horizontal:
                x = 1.0 - x
            if self.flip_vertical:
                y = 1.0 - y
            
            # 根據旋轉調整座標
            if self.frame_rotation == 90:
                # 90度順時針旋轉: (x,y) -> (y, 1-x)
                new_x, new_y = y, 1.0 - x
            elif self.frame_rotation == 180:
                # 180度旋轉: (x,y) -> (1-x, 1-y)
                new_x, new_y = 1.0 - x, 1.0 - y
            elif self.frame_rotation == 270:
                # 270度順時針旋轉: (x,y) -> (1-y, x)
                new_x, new_y = 1.0 - y, x
            else:
                # 0度，無旋轉
                new_x, new_y = x, y
            
            # 更新特徵點座標
            adjusted_landmarks.landmark[i].x = new_x
            adjusted_landmarks.landmark[i].y = new_y
        
        return adjusted_landmarks

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
                
                # 儲存原始畫面形狀以便後續座標調整
                original_shape = frame.shape
                
                # 調整畫面方向
                frame = self.adjust_frame_orientation(frame)
                rotated_shape = frame.shape
                
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
                        
                        # 根據畫面旋轉調整手部特徵點
                        h, w, _ = frame.shape
                        if self.frame_rotation != 0 or self.flip_horizontal or self.flip_vertical:
                            hand_landmarks = self.adjust_hand_landmarks_for_rotation(hand_landmarks, (h, w, 3), (h, w, 3))
                        
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
                        
                        # 顯示畫面方向信息
                        orientation_info = f"Rot:{self.frame_rotation}"
                        if self.flip_horizontal:
                            orientation_info += " H"
                        if self.flip_vertical:
                            orientation_info += " V"
                        cv2.putText(frame, orientation_info, (frame_w - 120, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        
                        cv2.putText(frame, "ESC:exit P:preview R:rotate H:flip-h V:flip-v 0:reset", 
                                (10, frame_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                        cv2.putText(frame, "+/-:fps", (10, frame_h - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
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
                elif key == ord('r') or key == ord('R'):  # R鍵旋轉畫面 (順時針90度)
                    self.frame_rotation = (self.frame_rotation + 90) % 360
                    print(f"畫面旋轉: {self.frame_rotation}度")
                elif key == ord('h') or key == ord('H'):  # H鍵水平翻轉
                    self.flip_horizontal = not self.flip_horizontal
                    print(f"水平翻轉: {'開啟' if self.flip_horizontal else '關閉'}")
                elif key == ord('v') or key == ord('V'):  # V鍵垂直翻轉
                    self.flip_vertical = not self.flip_vertical
                    print(f"垂直翻轉: {'開啟' if self.flip_vertical else '關閉'}")
                elif key == ord('0'):  # 0鍵重置所有旋轉和翻轉
                    self.frame_rotation = 0
                    self.flip_horizontal = False
                    self.flip_vertical = False
                    print("已重置畫面方向")
        
        finally:
            # 釋放資源
            self.cap.release()
            cv2.destroyAllWindows()
            self.hands.close()
            if self.is_dragging:
                pyautogui.mouseUp()  # 確保拖曳動作結束


class AirMouseUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Air Mouse Controller")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # 設定風格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background='#2b2b2b', foreground='white')
        self.style.configure('TButton', padding=6)
        self.style.configure('TFrame', background='#2b2b2b')
        
        # 初始化Air Mouse實例
        self.air_mouse = AirMouse()
        self.air_mouse.show_preview = True  # 強制啟用預覽以在UI中顯示
        
        # 控制變數
        self.is_running = False
        self.video_thread = None
        
        # 建立UI
        self.create_widgets()
        
        # 綁定關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左側控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 啟動/停止按鈕
        self.start_button = ttk.Button(control_frame, text="啟動", command=self.toggle_tracking)
        self.start_button.pack(fill=tk.X, pady=5)
        
        # 效能設定
        perf_frame = ttk.LabelFrame(control_frame, text="效能設定", padding=10)
        perf_frame.pack(fill=tk.X, pady=10)
        
        # FPS滑桿
        ttk.Label(perf_frame, text="處理頻率 (FPS):").pack()
        self.fps_var = tk.IntVar(value=50)
        self.fps_scale = ttk.Scale(perf_frame, from_=10, to=100, variable=self.fps_var, 
                                   orient=tk.HORIZONTAL, command=self.update_fps)
        self.fps_scale.pack(fill=tk.X, pady=5)
        self.fps_label = ttk.Label(perf_frame, text="50 FPS")
        self.fps_label.pack()
        
        # 畫面方向設定
        orientation_frame = ttk.LabelFrame(control_frame, text="畫面方向", padding=10)
        orientation_frame.pack(fill=tk.X, pady=10)
        
        # 旋轉按鈕
        ttk.Button(orientation_frame, text="旋轉90°", command=self.rotate_frame).pack(fill=tk.X, pady=2)
        ttk.Button(orientation_frame, text="水平翻轉", command=self.flip_horizontal).pack(fill=tk.X, pady=2)
        ttk.Button(orientation_frame, text="垂直翻轉", command=self.flip_vertical).pack(fill=tk.X, pady=2)
        ttk.Button(orientation_frame, text="重置方向", command=self.reset_orientation).pack(fill=tk.X, pady=2)
        
        # 狀態顯示
        status_frame = ttk.LabelFrame(control_frame, text="狀態信息", padding=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="未啟動")
        self.status_label.pack()
        
        self.orientation_label = ttk.Label(status_frame, text="方向: 0°")
        self.orientation_label.pack()
        
        self.gpu_label = ttk.Label(status_frame, text="GPU: 檢測中...")
        self.gpu_label.pack()
        
        # 手勢說明
        gesture_frame = ttk.LabelFrame(control_frame, text="手勢說明", padding=10)
        gesture_frame.pack(fill=tk.X, pady=10)
        
        gestures_text = """
• 食指：移動滑鼠
• 食指+中指靠近：左鍵點擊
• 食指+大拇指靠近：右鍵點擊
• 食指+中指分開：拖曳
• 五指伸直：滾動
        """
        ttk.Label(gesture_frame, text=gestures_text, justify=tk.LEFT).pack()
        
        # 右側視頻顯示
        video_frame = ttk.LabelFrame(main_frame, text="攝像頭畫面", padding=10)
        video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.video_label = ttk.Label(video_frame, text="攝像頭未啟動", anchor=tk.CENTER)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # 更新GPU狀態
        self.update_gpu_status()
    
    def update_fps(self, value):
        fps = int(float(value))
        self.fps_label.config(text=f"{fps} FPS")
        if hasattr(self.air_mouse, 'frame_process_interval'):
            self.air_mouse.frame_process_interval = int(1000 / fps)
    
    def toggle_tracking(self):
        if not self.is_running:
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        self.is_running = True
        self.start_button.config(text="停止")
        self.status_label.config(text="運行中...")
        
        # 啟動視頻處理執行緒
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
    
    def stop_tracking(self):
        self.is_running = False
        self.start_button.config(text="啟動")
        self.status_label.config(text="已停止")
        self.video_label.config(image='', text="攝像頭未啟動")
    
    def video_loop(self):
        try:
            while self.is_running and self.air_mouse.cap.isOpened():
                success, frame = self.air_mouse.cap.read()
                if not success:
                    break
                
                # 儲存原始畫面形狀以便後續座標調整
                original_shape = frame.shape
                
                # 調整畫面方向
                frame = self.air_mouse.adjust_frame_orientation(frame)
                rotated_shape = frame.shape
                
                current_time = time.time() * 1000
                should_process = (current_time - self.air_mouse.last_process_time) >= self.air_mouse.frame_process_interval
                
                if should_process:
                    self.air_mouse.last_process_time = current_time
                    
                    # 處理影像
                    if self.air_mouse.use_gpu and self.air_mouse.opencv_gpu_available:
                        try:
                            gpu_frame = cv2.cuda_GpuMat()
                            gpu_frame.upload(frame)
                            frame_processed = gpu_frame.download()
                            rgb_frame = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
                        except Exception as e:
                            print(f"GPU 處理錯誤：{e}，切換到 CPU 模式")
                            self.air_mouse.opencv_gpu_available = False
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    else:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # MediaPipe 手部檢測
                    results = self.air_mouse.hands.process(rgb_frame)
                    
                    # 繪製交互區域
                    frame_h, frame_w, _ = frame.shape
                    margin_x = int(frame_w * (1 - CAMERA_AREA_RATIO) / 2)
                    margin_y = int(frame_h * (1 - CAMERA_AREA_RATIO) / 2)
                    cv2.rectangle(frame, (margin_x, margin_y), 
                                (frame_w - margin_x, frame_h - margin_y), (0, 255, 0), 2)
                    
                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]
                        
                        # 根據畫面旋轉調整手部特徵點
                        if self.air_mouse.frame_rotation != 0 or self.air_mouse.flip_horizontal or self.air_mouse.flip_vertical:
                            hand_landmarks = self.air_mouse.adjust_hand_landmarks_for_rotation(
                                hand_landmarks, original_shape, rotated_shape)
                        
                        # 繪製手部標記點
                        mp_drawing.draw_landmarks(
                            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
                        
                        # 檢測手勢
                        gesture = self.air_mouse.detect_gesture(hand_landmarks, frame.shape)
                        
                        # 控制滑鼠
                        if gesture:
                            self.air_mouse.control_mouse(hand_landmarks, frame.shape, gesture)
                            cv2.putText(frame, f"Gesture: {gesture}", (10, 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    # 顯示FPS和方向信息
                    fps = int(1000 / self.air_mouse.frame_process_interval)
                    cv2.putText(frame, f"FPS: ~{fps}", (frame_w - 120, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    orientation_info = f"Rot:{self.air_mouse.frame_rotation}"
                    if self.air_mouse.flip_horizontal:
                        orientation_info += " H"
                    if self.air_mouse.flip_vertical:
                        orientation_info += " V"
                    cv2.putText(frame, orientation_info, (frame_w - 120, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # 更新UI中的影像
                self.update_video_display(frame)
                
        except Exception as e:
            print(f"視頻處理錯誤: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_button.config(text="啟動"))
            self.root.after(0, lambda: self.status_label.config(text="已停止"))
    
    def update_video_display(self, frame):
        # 將OpenCV影像轉換為tkinter可顯示的格式
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # 調整影像大小以適應顯示區域
        display_size = (480, 360)
        frame_pil = frame_pil.resize(display_size, Image.Resampling.LANCZOS)
        
        # 轉換為PhotoImage
        photo = ImageTk.PhotoImage(frame_pil)
        
        # 更新顯示（使用after方法確保線程安全）
        self.root.after(0, lambda: self.video_label.config(image=photo, text=""))
        self.root.after(0, lambda: setattr(self.video_label, 'image', photo))  # 保持引用
    
    def rotate_frame(self):
        self.air_mouse.frame_rotation = (self.air_mouse.frame_rotation + 90) % 360
        self.update_orientation_display()
    
    def flip_horizontal(self):
        self.air_mouse.flip_horizontal = not self.air_mouse.flip_horizontal
        self.update_orientation_display()
    
    def flip_vertical(self):
        self.air_mouse.flip_vertical = not self.air_mouse.flip_vertical
        self.update_orientation_display()
    
    def reset_orientation(self):
        self.air_mouse.frame_rotation = 0
        self.air_mouse.flip_horizontal = False
        self.air_mouse.flip_vertical = False
        self.update_orientation_display()
    
    def update_orientation_display(self):
        orientation_text = f"方向: {self.air_mouse.frame_rotation}°"
        if self.air_mouse.flip_horizontal:
            orientation_text += " 水平翻轉"
        if self.air_mouse.flip_vertical:
            orientation_text += " 垂直翻轉"
        self.orientation_label.config(text=orientation_text)
    
    def update_gpu_status(self):
        gpu_status = "GPU: "
        if self.air_mouse.opencv_gpu_available:
            gpu_status += "OpenCV✓ "
        if self.air_mouse.tf_gpu_available:
            gpu_status += "TensorFlow✓"
        if not (self.air_mouse.opencv_gpu_available or self.air_mouse.tf_gpu_available):
            gpu_status += "未偵測到"
        self.gpu_label.config(text=gpu_status)
    
    def on_closing(self):
        if self.is_running:
            self.stop_tracking()
        
        # 釋放資源
        if hasattr(self.air_mouse, 'cap') and self.air_mouse.cap.isOpened():
            self.air_mouse.cap.release()
        if hasattr(self.air_mouse, 'hands'):
            self.air_mouse.hands.close()
        if self.air_mouse.is_dragging:
            pyautogui.mouseUp()
        
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="Air Mouse - 使用手勢控制滑鼠")
    parser.add_argument('--no-preview', action='store_true', help='啟動時不顯示預覽畫面 (提升效能)')
    parser.add_argument('--fps', type=int, default=50, help='設定處理頻率 (10-100 之間，數值越小越流暢但CPU負擔越重)')
    parser.add_argument('--no-gpu', action='store_true', help='禁用 GPU 加速 (在 GPU 出現問題時使用)')
    parser.add_argument('--rotation', type=int, choices=[0, 90, 180, 270], default=0, 
                        help='設定攝像頭畫面初始旋轉角度 (0, 90, 180, 270)')
    parser.add_argument('--flip-h', action='store_true', help='啟動時水平翻轉畫面')
    parser.add_argument('--flip-v', action='store_true', help='啟動時垂直翻轉畫面')
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
    print("- 按R鍵旋轉畫面90度（調整手部方向）")
    print("- 按H鍵水平翻轉畫面")
    print("- 按V鍵垂直翻轉畫面")
    print("- 按0鍵重置畫面方向")    
    # 啟動UI或傳統模式
    if args.no_preview:
        # 使用傳統的命令行模式
        air_mouse = AirMouse()
        
        # 設定處理頻率 (轉換為處理間隔毫秒)
        fps = max(10, min(100, args.fps))
        air_mouse.frame_process_interval = int(1000 / fps)
        print(f"處理頻率: 約 {fps} FPS")
        
        # 設定畫面方向
        air_mouse.frame_rotation = args.rotation
        air_mouse.flip_horizontal = args.flip_h
        air_mouse.flip_vertical = args.flip_v
        if args.rotation != 0 or args.flip_h or args.flip_v:
            print(f"畫面方向設定: 旋轉{args.rotation}度, "
                  f"水平翻轉{'開啟' if args.flip_h else '關閉'}, "
                  f"垂直翻轉{'開啟' if args.flip_v else '關閉'}")
        
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
    else:
        # 使用圖形化界面
        ui = AirMouseUI()
        
        # 從命令行參數設定初始值
        ui.air_mouse.frame_rotation = args.rotation
        ui.air_mouse.flip_horizontal = args.flip_h
        ui.air_mouse.flip_vertical = args.flip_v
        
        if args.no_gpu:
            ui.air_mouse.use_gpu = False
        
        # 設定FPS
        fps = max(10, min(100, args.fps))
        ui.air_mouse.frame_process_interval = int(1000 / fps)
        ui.fps_var.set(fps)
        
        ui.run()