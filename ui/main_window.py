"""
Air Mouse GUI 主視窗
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import cv2
import numpy as np
from PIL import Image, ImageTk
import mediapipe as mp

from core.air_mouse import AirMouse
from core.config import (
    UI_WINDOW_SIZE, UI_BG_COLOR, VIDEO_DISPLAY_SIZE,
    CAMERA_AREA_RATIO
)

# MediaPipe 繪圖工具
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class AirMouseUI:
    """Air Mouse 圖形化使用者介面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Air Mouse Controller")
        self.root.geometry(UI_WINDOW_SIZE)
        self.root.configure(bg=UI_BG_COLOR)
        
        # 設定風格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background=UI_BG_COLOR, foreground='white')
        self.style.configure('TButton', padding=6)
        self.style.configure('TFrame', background=UI_BG_COLOR)
        
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
        """建立 UI 元件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左側控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self._create_control_buttons(control_frame)
        self._create_performance_settings(control_frame)
        self._create_orientation_settings(control_frame)
        self._create_status_display(control_frame)
        self._create_gesture_help(control_frame)
        
        # 右側視頻顯示
        self._create_video_display(main_frame)
        
        # 更新GPU狀態
        self.update_gpu_status()
    
    def _create_control_buttons(self, parent):
        """建立控制按鈕"""
        # 啟動/停止按鈕
        self.start_button = ttk.Button(parent, text="啟動", command=self.toggle_tracking)
        self.start_button.pack(fill=tk.X, pady=5)
    
    def _create_performance_settings(self, parent):
        """建立效能設定介面"""
        perf_frame = ttk.LabelFrame(parent, text="效能設定", padding=10)
        perf_frame.pack(fill=tk.X, pady=10)
        
        # FPS滑桿
        ttk.Label(perf_frame, text="處理頻率 (FPS):").pack()
        self.fps_var = tk.IntVar(value=50)
        self.fps_scale = ttk.Scale(perf_frame, from_=10, to=100, variable=self.fps_var, 
                                   orient=tk.HORIZONTAL, command=self.update_fps)
        self.fps_scale.pack(fill=tk.X, pady=5)
        self.fps_label = ttk.Label(perf_frame, text="50 FPS")
        self.fps_label.pack()
    
    def _create_orientation_settings(self, parent):
        """建立畫面方向設定介面"""
        orientation_frame = ttk.LabelFrame(parent, text="畫面方向", padding=10)
        orientation_frame.pack(fill=tk.X, pady=10)
        
        # 旋轉按鈕
        ttk.Button(orientation_frame, text="旋轉90°", command=self.rotate_frame).pack(fill=tk.X, pady=2)
        ttk.Button(orientation_frame, text="水平翻轉", command=self.flip_horizontal).pack(fill=tk.X, pady=2)
        ttk.Button(orientation_frame, text="垂直翻轉", command=self.flip_vertical).pack(fill=tk.X, pady=2)
        ttk.Button(orientation_frame, text="重置方向", command=self.reset_orientation).pack(fill=tk.X, pady=2)
    
    def _create_status_display(self, parent):
        """建立狀態顯示介面"""
        status_frame = ttk.LabelFrame(parent, text="狀態信息", padding=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="未啟動")
        self.status_label.pack()
        
        self.orientation_label = ttk.Label(status_frame, text="方向: 0°")
        self.orientation_label.pack()
        
        self.gpu_label = ttk.Label(status_frame, text="GPU: 檢測中...")
        self.gpu_label.pack()
    
    def _create_gesture_help(self, parent):
        """建立手勢說明介面"""
        gesture_frame = ttk.LabelFrame(parent, text="手勢說明", padding=10)
        gesture_frame.pack(fill=tk.X, pady=10)
        
        gestures_text = """
• 食指：移動滑鼠
• 食指+中指靠近：左鍵點擊
• 食指+大拇指靠近：右鍵點擊
• 食指+中指分開：拖曳
• 五指伸直：滾動
        """
        ttk.Label(gesture_frame, text=gestures_text, justify=tk.LEFT).pack()
    
    def _create_video_display(self, parent):
        """建立視頻顯示介面"""
        video_frame = ttk.LabelFrame(parent, text="攝像頭畫面", padding=10)
        video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.video_label = ttk.Label(video_frame, text="攝像頭未啟動", anchor=tk.CENTER)
        self.video_label.pack(fill=tk.BOTH, expand=True)
    
    def update_fps(self, value):
        """更新 FPS 設定"""
        fps = int(float(value))
        self.fps_label.config(text=f"{fps} FPS")
        if hasattr(self.air_mouse, 'frame_process_interval'):
            self.air_mouse.frame_process_interval = int(1000 / fps)
    
    def toggle_tracking(self):
        """切換追蹤狀態"""
        if not self.is_running:
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        """開始追蹤"""
        self.is_running = True
        self.start_button.config(text="停止")
        self.status_label.config(text="運行中...")
        
        # 啟動視頻處理執行緒
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
    
    def stop_tracking(self):
        """停止追蹤"""
        self.is_running = False
        self.start_button.config(text="啟動")
        self.status_label.config(text="已停止")
        self.video_label.config(image='', text="攝像頭未啟動")
    
    def video_loop(self):
        """視頻處理主循環"""
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
                    rgb_frame = self._process_frame(frame)
                    
                    # MediaPipe 手部檢測
                    results = self.air_mouse.gesture_detector.process_frame(rgb_frame)
                    
                    # 繪製交互區域
                    self._draw_interaction_area(frame)
                    
                    # 處理手部檢測結果
                    if results.multi_hand_landmarks:
                        self._process_hand_landmarks(results.multi_hand_landmarks[0], frame, original_shape, rotated_shape)
                    
                    # 顯示FPS和方向信息
                    self._draw_info_overlay(frame)
                
                # 更新UI中的影像
                self.update_video_display(frame)
                
        except Exception as e:
            print(f"視頻處理錯誤: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_button.config(text="啟動"))
            self.root.after(0, lambda: self.status_label.config(text="已停止"))
    
    def _process_frame(self, frame):
        """處理影像幀"""
        if self.air_mouse.use_gpu and self.air_mouse.gpu_detector.opencv_gpu_available:
            try:
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)
                frame_processed = gpu_frame.download()
                return cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print(f"GPU 處理錯誤：{e}，切換到 CPU 模式")
                self.air_mouse.gpu_detector.opencv_gpu_available = False
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def _draw_interaction_area(self, frame):
        """繪製交互區域"""
        frame_h, frame_w, _ = frame.shape
        margin_x = int(frame_w * (1 - CAMERA_AREA_RATIO) / 2)
        margin_y = int(frame_h * (1 - CAMERA_AREA_RATIO) / 2)
        cv2.rectangle(frame, (margin_x, margin_y), 
                     (frame_w - margin_x, frame_h - margin_y), (0, 255, 0), 2)
    
    def _process_hand_landmarks(self, hand_landmarks, frame, original_shape, rotated_shape):
        """處理手部特徵點"""
        # 根據畫面旋轉調整手部特徵點
        if (self.air_mouse.frame_rotation != 0 or 
            self.air_mouse.flip_horizontal or 
            self.air_mouse.flip_vertical):
            hand_landmarks = self.air_mouse.adjust_hand_landmarks_for_rotation(
                hand_landmarks, original_shape, rotated_shape)
        
        # 繪製手部標記點
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
          # 檢測手勢
        gesture = self.air_mouse.gesture_detector.detect_gesture(hand_landmarks, frame.shape)
        
        # 控制滑鼠
        if gesture:
            self.air_mouse.mouse_controller.control_mouse(hand_landmarks, frame.shape, gesture)
            cv2.putText(frame, f"Gesture: {gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    def _draw_info_overlay(self, frame):
        """繪製資訊覆蓋層"""
        frame_h, frame_w, _ = frame.shape
        
        # 顯示FPS
        fps = int(1000 / self.air_mouse.frame_process_interval)
        cv2.putText(frame, f"FPS: ~{fps}", (frame_w - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 顯示方向信息
        orientation_info = f"Rot:{self.air_mouse.frame_rotation}"
        if self.air_mouse.flip_horizontal:
            orientation_info += " H"
        if self.air_mouse.flip_vertical:
            orientation_info += " V"
        cv2.putText(frame, orientation_info, (frame_w - 120, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    def update_video_display(self, frame):
        """更新視頻顯示"""
        # 將OpenCV影像轉換為tkinter可顯示的格式
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # 調整影像大小以適應顯示區域
        frame_pil = frame_pil.resize(VIDEO_DISPLAY_SIZE, Image.Resampling.LANCZOS)
        
        # 轉換為PhotoImage
        photo = ImageTk.PhotoImage(frame_pil)
        
        # 更新顯示（使用after方法確保線程安全）
        self.root.after(0, lambda: self.video_label.config(image=photo, text=""))
        self.root.after(0, lambda: setattr(self.video_label, 'image', photo))  # 保持引用
    
    def rotate_frame(self):
        """旋轉畫面"""
        self.air_mouse.frame_rotation = (self.air_mouse.frame_rotation + 90) % 360
        self.update_orientation_display()
    
    def flip_horizontal(self):
        """水平翻轉"""
        self.air_mouse.flip_horizontal = not self.air_mouse.flip_horizontal
        self.update_orientation_display()
    
    def flip_vertical(self):
        """垂直翻轉"""
        self.air_mouse.flip_vertical = not self.air_mouse.flip_vertical
        self.update_orientation_display()
    
    def reset_orientation(self):
        """重置方向"""
        self.air_mouse.frame_rotation = 0
        self.air_mouse.flip_horizontal = False
        self.air_mouse.flip_vertical = False
        self.update_orientation_display()
    
    def update_orientation_display(self):
        """更新方向顯示"""
        orientation_text = f"方向: {self.air_mouse.frame_rotation}°"
        if self.air_mouse.flip_horizontal:
            orientation_text += " 水平翻轉"
        if self.air_mouse.flip_vertical:
            orientation_text += " 垂直翻轉"
        self.orientation_label.config(text=orientation_text)
    
    def update_gpu_status(self):
        """更新 GPU 狀態顯示"""
        gpu_status = self.air_mouse.gpu_detector.get_status_text()
        self.gpu_label.config(text=gpu_status)
    
    def set_initial_settings(self, rotation=0, flip_h=False, flip_v=False, fps=50, use_gpu=True):
        """設定初始參數"""
        self.air_mouse.frame_rotation = rotation
        self.air_mouse.flip_horizontal = flip_h
        self.air_mouse.flip_vertical = flip_v
        self.air_mouse.use_gpu = use_gpu
        
        # 設定FPS
        self.air_mouse.frame_process_interval = int(1000 / fps)
        self.fps_var.set(fps)
        
        # 更新顯示
        self.update_orientation_display()
        self.update_gpu_status()
    
    def on_closing(self):
        """關閉視窗事件處理"""
        if self.is_running:
            self.stop_tracking()
        
        # 釋放資源
        self.air_mouse.cleanup()
        self.root.destroy()
    
    def run(self):
        """啟動主循環"""
        self.root.mainloop()
