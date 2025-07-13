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
from core.gesture_recorder import GestureRecorder, GestureData, GestureAnalyzer
from core.config import (
    UI_WINDOW_SIZE, UI_BG_COLOR, VIDEO_DISPLAY_SIZE,
    CAMERA_AREA_RATIO, CAMERA_VERTICAL_OFFSET
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
        
        # 初始化手勢錄入器
        self.gesture_recorder = GestureRecorder()
        
        # 控制變數
        self.is_running = False
        self.video_thread = None
        
        # 建立UI
        self.create_widgets()
        
        # 更新鍵盤狀態顯示
        self.update_keyboard_status()
        
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
        self._create_gesture_recording(control_frame)
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
        
        # 手動點擊按鈕
        self.click_button = ttk.Button(parent, text="手動點擊", command=self.test_click)
        self.click_button.pack(fill=tk.X, pady=5)
        
        # 鍵盤狀態顯示
        self.keyboard_status_label = ttk.Label(parent, text="檢查鍵盤狀態中...")
        self.keyboard_status_label.pack(fill=tk.X, pady=2)
        
        # 顯示模式切換按鈕
        self.show_hands_only = tk.BooleanVar(value=False)
        self.display_mode_button = ttk.Checkbutton(
            parent, 
            text="只顯示手部位置", 
            variable=self.show_hands_only,
            command=self.toggle_display_mode
        )
        self.display_mode_button.pack(fill=tk.X, pady=5)
    
    def _create_gesture_recording(self, parent):
        """建立手勢錄入介面"""
        recording_frame = ttk.LabelFrame(parent, text="手勢錄入", padding=10)
        recording_frame.pack(fill=tk.X, pady=10)
        
        # 手勢名稱輸入
        ttk.Label(recording_frame, text="手勢名稱:").pack()
        self.gesture_name_var = tk.StringVar(value="")
        self.gesture_name_entry = ttk.Entry(recording_frame, textvariable=self.gesture_name_var)
        self.gesture_name_entry.pack(fill=tk.X, pady=2)
        
        # 錄入控制按鈕
        button_frame = ttk.Frame(recording_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.record_button = ttk.Button(button_frame, text="開始錄入", command=self.start_gesture_recording)
        self.record_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_record_button = ttk.Button(button_frame, text="停止錄入", command=self.stop_gesture_recording, state=tk.DISABLED)
        self.stop_record_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_record_button = ttk.Button(button_frame, text="取消", command=self.cancel_gesture_recording, state=tk.DISABLED)
        self.cancel_record_button.pack(side=tk.LEFT)
        
        # 錄入狀態顯示
        self.recording_status_label = ttk.Label(recording_frame, text="未錄入")
        self.recording_status_label.pack(pady=2)
        
        # 已儲存手勢列表
        ttk.Label(recording_frame, text="已儲存手勢:").pack(pady=(10, 0))
        
        # 手勢列表框架
        list_frame = ttk.Frame(recording_frame)
        list_frame.pack(fill=tk.X, pady=2)
        
        # 手勢選擇下拉選單
        self.gesture_list_var = tk.StringVar()
        self.gesture_list_combo = ttk.Combobox(list_frame, textvariable=self.gesture_list_var, state="readonly")
        self.gesture_list_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 手勢管理按鈕
        manage_frame = ttk.Frame(recording_frame)
        manage_frame.pack(fill=tk.X, pady=2)
        
        self.refresh_list_button = ttk.Button(manage_frame, text="重新整理", command=self.refresh_gesture_list)
        self.refresh_list_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_gesture_button = ttk.Button(manage_frame, text="刪除", command=self.delete_selected_gesture)
        self.delete_gesture_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.analyze_gesture_button = ttk.Button(manage_frame, text="分析", command=self.analyze_selected_gesture)
        self.analyze_gesture_button.pack(side=tk.LEFT)
        
        # 初始化手勢列表
        self.refresh_gesture_list()
    
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
        
        # 抖動過濾設定
        self.jitter_filter_enabled = tk.BooleanVar(value=True)
        self.jitter_filter_button = ttk.Checkbutton(
            perf_frame, 
            text="啟用抖動過濾", 
            variable=self.jitter_filter_enabled,
            command=self.toggle_jitter_filter
        )
        self.jitter_filter_button.pack(fill=tk.X, pady=5)
        
        # 抖動過濾靈敏度
        ttk.Label(perf_frame, text="抖動過濾靈敏度:").pack()
        self.jitter_threshold_var = tk.IntVar(value=15)
        self.jitter_threshold_scale = ttk.Scale(
            perf_frame, from_=5, to=50, variable=self.jitter_threshold_var, 
            orient=tk.HORIZONTAL, command=self.update_jitter_threshold
        )
        self.jitter_threshold_scale.pack(fill=tk.X, pady=5)
        self.jitter_threshold_label = ttk.Label(perf_frame, text="15 像素")
        self.jitter_threshold_label.pack()
    
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
        
        self.gesture_label = ttk.Label(status_frame, text="手勢: 無")
        self.gesture_label.pack()
    
    def _create_gesture_help(self, parent):
        """建立手勢說明介面"""
        gesture_frame = ttk.LabelFrame(parent, text="操作說明", padding=10)
        gesture_frame.pack(fill=tk.X, pady=10)
        
        gestures_text = """
• 食指移動：控制滑鼠移動
• 空白鍵：左鍵點擊

注意：
- 保持食指在綠色框內
- 按下鍵盤空白鍵進行點擊
- 其他手指狀態不影響控制
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
    
    def test_click(self):
        """測試點擊功能"""
        try:
            from core.config import get_pyautogui
            pyautogui = get_pyautogui()
            current_pos = pyautogui.position()
            pyautogui.click(current_pos.x, current_pos.y, _pause=False)
            print(f"[UI TEST] 測試點擊: ({current_pos.x}, {current_pos.y})")
        except Exception as e:
            print(f"[UI TEST] 測試點擊失敗: {e}")
    
    def toggle_display_mode(self):
        """切換顯示模式：完整畫面 或 只顯示手部位置"""
        if self.show_hands_only.get():
            print("[UI] 切換到只顯示手部位置模式")
        else:
            print("[UI] 切換到完整畫面模式")
    
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
        self.gesture_label.config(text="手勢: 無")
    
    def video_loop(self):
        """視頻處理主循環"""
        try:
            while self.is_running and self.air_mouse.cap.isOpened():
                success, frame = self.air_mouse.cap.read()
                if not success:
                    break
                
                # 處理一幀影像
                processed_frame, gesture = self.air_mouse.process_frame(frame)
                
                # 手勢錄入處理
                if self.gesture_recorder.recording:
                    # 轉換為RGB格式供MediaPipe使用
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    hand_detected, landmarks = self.gesture_recorder.process_frame(rgb_frame)
                    
                    # 更新錄入狀態
                    status = self.gesture_recorder.get_recording_status()
                    status_text = f"錄製中: {status['gesture_name']} ({status['frame_count']} 幀, {status['remaining_time']:.1f}s)"
                    self.root.after(0, lambda text=status_text: self.recording_status_label.config(text=text))
                    
                    # 檢查是否錄製超時
                    if status['remaining_time'] <= 0:
                        self.root.after(0, self.stop_gesture_recording)
                
                # 根據顯示模式處理影像
                if self.show_hands_only.get():
                    # 只顯示手部位置模式：創建黑色背景並只繪製手部
                    display_frame = self.create_hands_only_frame(frame)
                else:
                    # 完整畫面模式
                    display_frame = processed_frame
                
                # 在錄製時在畫面上顯示錄製狀態
                if self.gesture_recorder.recording:
                    cv2.putText(display_frame, "RECORDING", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.circle(display_frame, (30, 60), 10, (0, 0, 255), -1)  # 紅色錄製指示燈
                
                # 更新手勢顯示
                gesture_text = f"手勢: {gesture if gesture else '無'}"
                self.root.after(0, lambda text=gesture_text: self.gesture_label.config(text=text))
                
                # 更新UI中的影像
                self.update_video_display(display_frame)
                
        except Exception as e:
            print(f"視頻處理錯誤: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_button.config(text="啟動"))
            self.root.after(0, lambda: self.status_label.config(text="已停止"))
    
    def update_video_display(self, frame):
        """更新視頻顯示"""
        try:
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
        except Exception as e:
            print(f"視頻顯示錯誤: {e}")
    
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
    
    def set_initial_settings(self, rotation=0, flip_h=True, flip_v=True, fps=50, use_gpu=True):
        """設定初始參數"""
        self.air_mouse.frame_rotation = rotation
        self.air_mouse.flip_horizontal = flip_h
        self.air_mouse.flip_vertical = flip_v
        self.air_mouse.use_gpu = use_gpu
        
        # 設定FPS
        self.air_mouse.frame_process_interval = int(1000 / fps)
        self.fps_var.set(fps)
        
        # 初始化抖動過濾設定
        self.jitter_filter_enabled.set(True)
        self.jitter_threshold_var.set(15)
        self.toggle_jitter_filter()
        self.update_jitter_threshold(15)
        
        # 更新顯示
        self.update_orientation_display()
        self.update_gpu_status()
    
    def on_closing(self):
        """關閉視窗事件處理"""
        if self.is_running:
            self.stop_tracking()
        
        # 釋放資源
        self.air_mouse.cleanup()
        self.gesture_recorder.close()
        self.root.destroy()
    
    def run(self):
        """啟動主循環"""
        # 設定預設值（與 air_mouse.py 中一致）
        self.set_initial_settings()
        self.root.mainloop()
    
    def create_hands_only_frame(self, original_frame):
        """創建只顯示手部位置的黑色背景圖像"""
        # 調整畫面方向
        frame = self.air_mouse.adjust_frame_orientation(original_frame)
        frame_h, frame_w = frame.shape[:2]
        
        # 創建黑色背景
        black_frame = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
        
        # 處理影像並檢測手部
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.air_mouse.gesture_detector.process_frame(rgb_frame)
        
        if results.multi_hand_landmarks:
            # 繪製交互區域（綠色框）
            from core.config import CAMERA_VERTICAL_OFFSET
            margin_x = int(frame_w * (1 - CAMERA_AREA_RATIO) / 2)
            margin_y = int(frame_h * (1 - CAMERA_AREA_RATIO) / 2)
            
            # 添加垂直偏移
            offset_pixels = int(frame_h * CAMERA_VERTICAL_OFFSET)
            top_y = margin_y + offset_pixels
            bottom_y = frame_h - margin_y + offset_pixels
            
            # 確保邊界
            top_y = max(0, top_y)
            bottom_y = min(frame_h, bottom_y)
            
            cv2.rectangle(black_frame, (margin_x, top_y), 
                         (frame_w - margin_x, bottom_y), (0, 255, 0), 2)
            
            # 繪製手部標記點（亮色）
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    black_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # 高亮食指尖端
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                tip_x = int(index_tip.x * frame_w)
                tip_y = int(index_tip.y * frame_h)
                cv2.circle(black_frame, (tip_x, tip_y), 8, (255, 255, 0), -1)  # 黃色圓點
        else:
            # 沒有檢測到手部時，顯示提示文字
            cv2.putText(black_frame, "No Hand Detected", 
                       (frame_w//2 - 100, frame_h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return black_frame
    
    def toggle_jitter_filter(self):
        """切換抖動過濾功能"""
        if hasattr(self.air_mouse, 'mouse_controller'):
            self.air_mouse.mouse_controller.jitter_filter_enabled = self.jitter_filter_enabled.get()
            status = "啟用" if self.jitter_filter_enabled.get() else "停用"
            print(f"[UI] 抖動過濾: {status}")
    
    def update_jitter_threshold(self, value):
        """更新抖動過濾靈敏度"""
        threshold = int(float(value))
        self.jitter_threshold_label.config(text=f"{threshold} 像素")
        if hasattr(self.air_mouse, 'mouse_controller'):
            self.air_mouse.mouse_controller.min_move_distance = threshold
            print(f"[UI] 抖動過濾靈敏度: {threshold} 像素")
    
    # ===== 手勢錄入相關方法 =====
    
    def start_gesture_recording(self):
        """開始錄製手勢"""
        gesture_name = self.gesture_name_var.get().strip()
        if not gesture_name:
            print("[UI] 請輸入手勢名稱")
            return
        
        if self.gesture_recorder.start_recording(gesture_name):
            self.record_button.config(state=tk.DISABLED)
            self.stop_record_button.config(state=tk.NORMAL)
            self.cancel_record_button.config(state=tk.NORMAL)
            self.recording_status_label.config(text=f"錄製中: {gesture_name}")
            print(f"[UI] 開始錄製手勢: {gesture_name}")
        else:
            print("[UI] 錄製失敗，可能正在錄製中")
    
    def stop_gesture_recording(self):
        """停止錄製手勢"""
        gesture_data = self.gesture_recorder.stop_recording()
        
        self.record_button.config(state=tk.NORMAL)
        self.stop_record_button.config(state=tk.DISABLED)
        self.cancel_record_button.config(state=tk.DISABLED)
        
        if gesture_data:
            # 儲存手勢
            if self.gesture_recorder.save_gesture(gesture_data):
                self.recording_status_label.config(text=f"已儲存: {gesture_data.name}")
                self.refresh_gesture_list()
                self.gesture_name_var.set("")  # 清空輸入欄
                print(f"[UI] 手勢錄製並儲存成功: {gesture_data.name}")
            else:
                self.recording_status_label.config(text="儲存失敗")
                print("[UI] 手勢儲存失敗")
        else:
            self.recording_status_label.config(text="錄製失敗")
            print("[UI] 手勢錄製失敗")
    
    def cancel_gesture_recording(self):
        """取消錄製手勢"""
        self.gesture_recorder.cancel_recording()
        
        self.record_button.config(state=tk.NORMAL)
        self.stop_record_button.config(state=tk.DISABLED)
        self.cancel_record_button.config(state=tk.DISABLED)
        self.recording_status_label.config(text="已取消")
        print("[UI] 手勢錄製已取消")
    
    def refresh_gesture_list(self):
        """重新整理已儲存的手勢列表"""
        saved_gestures = self.gesture_recorder.list_saved_gestures()
        self.gesture_list_combo['values'] = saved_gestures
        if saved_gestures:
            self.gesture_list_combo.set(saved_gestures[0])
        else:
            self.gesture_list_combo.set("")
        print(f"[UI] 手勢列表已更新: {len(saved_gestures)} 個手勢")
    
    def delete_selected_gesture(self):
        """刪除選中的手勢"""
        selected_gesture = self.gesture_list_var.get()
        if not selected_gesture:
            print("[UI] 請選擇要刪除的手勢")
            return
        
        # 確認對話框
        from tkinter import messagebox
        result = messagebox.askyesno("確認刪除", f"確定要刪除手勢 '{selected_gesture}' 嗎？")
        
        if result:
            if self.gesture_recorder.delete_gesture(selected_gesture):
                self.refresh_gesture_list()
                print(f"[UI] 已刪除手勢: {selected_gesture}")
            else:
                print(f"[UI] 刪除手勢失敗: {selected_gesture}")
    
    def analyze_selected_gesture(self):
        """分析選中的手勢"""
        selected_gesture = self.gesture_list_var.get()
        if not selected_gesture:
            print("[UI] 請選擇要分析的手勢")
            return
        
        # 載入手勢資料
        import os
        filepath = os.path.join(self.gesture_recorder.save_dir, selected_gesture)
        gesture_data = self.gesture_recorder.load_gesture(filepath)
        
        if gesture_data:
            # 分析手勢
            analysis = GestureAnalyzer.analyze_gesture(gesture_data)
            
            # 顯示分析結果
            from tkinter import messagebox
            analysis_text = f"""手勢分析結果: {gesture_data.name}
            
錄製時間: {gesture_data.timestamp}
幀數: {analysis.get('frame_count', 0)}
持續時間: {analysis.get('duration', 0):.2f} 秒
移動範圍:
  X軸: {analysis.get('movement_range', {}).get('x_range', 0):.3f}
  Y軸: {analysis.get('movement_range', {}).get('y_range', 0):.3f}
  Z軸: {analysis.get('movement_range', {}).get('z_range', 0):.3f}
            """
            
            messagebox.showinfo("手勢分析", analysis_text)
            print(f"[UI] 手勢分析完成: {selected_gesture}")
        else:
            print(f"[UI] 無法載入手勢: {selected_gesture}")
    
def main():
    """主程式入口點"""
    app = AirMouseUI()
    app.run()


if __name__ == "__main__":
    main()
