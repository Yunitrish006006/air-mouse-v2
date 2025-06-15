"""
圖像處理工具模組
"""
import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageProcessor:
    """圖像處理工具類"""
    
    @staticmethod
    def adjust_frame_orientation(frame, rotation=0, flip_horizontal=False, flip_vertical=False):
        """調整攝像頭畫面方向"""
        # 先進行水平或垂直翻轉
        if flip_horizontal:
            frame = cv2.flip(frame, 1)
        if flip_vertical:
            frame = cv2.flip(frame, 0)
        
        # 根據設定的角度旋轉畫面
        if rotation == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rotation == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        return frame
    
    @staticmethod
    def adjust_hand_landmarks_for_rotation(hand_landmarks, original_shape, rotated_shape, 
                                         rotation=0, flip_horizontal=False, flip_vertical=False):
        """根據畫面旋轉調整手部特徵點座標"""
        if not hand_landmarks:
            return hand_landmarks
        
        # 創建調整後的手部特徵點
        adjusted_landmarks = type(hand_landmarks)()
        adjusted_landmarks.CopyFrom(hand_landmarks)
        
        for i, landmark in enumerate(hand_landmarks.landmark):
            x, y = landmark.x, landmark.y
            
            # 根據翻轉調整座標
            if flip_horizontal:
                x = 1.0 - x
            if flip_vertical:
                y = 1.0 - y
            
            # 根據旋轉調整座標
            if rotation == 90:
                # 90度順時針旋轉: (x,y) -> (y, 1-x)
                new_x, new_y = y, 1.0 - x
            elif rotation == 180:
                # 180度旋轉: (x,y) -> (1-x, 1-y)
                new_x, new_y = 1.0 - x, 1.0 - y
            elif rotation == 270:
                # 270度順時針旋轉: (x,y) -> (1-y, x)
                new_x, new_y = 1.0 - y, x
            else:
                # 0度，無旋轉
                new_x, new_y = x, y
            
            # 更新特徵點座標
            adjusted_landmarks.landmark[i].x = new_x
            adjusted_landmarks.landmark[i].y = new_y
        
        return adjusted_landmarks
    
    @staticmethod
    def convert_frame_for_tkinter(frame, display_size=(480, 360)):
        """將OpenCV影像轉換為tkinter可顯示的格式"""
        # 將BGR轉換為RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        
        # 調整影像大小以適應顯示區域
        frame_pil = frame_pil.resize(display_size, Image.Resampling.LANCZOS)
        
        # 轉換為PhotoImage
        return ImageTk.PhotoImage(frame_pil)
    
    @staticmethod
    def process_frame_with_gpu(frame, gpu_available=False):
        """使用GPU處理影格（如果可用）"""
        if gpu_available:
            try:
                # 將影像上傳到 GPU
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)
                
                # 從 GPU 下載處理後的影像
                frame_processed = gpu_frame.download()
                
                # 將BGR轉換為RGB用於MediaPipe處理
                rgb_frame = cv2.cvtColor(frame_processed, cv2.COLOR_BGR2RGB)
                return rgb_frame, True
                
            except Exception as e:
                print(f"GPU 處理錯誤：{e}，切換到 CPU 模式")
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), False
        else:
            # 常規 CPU 處理
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), False
    
    @staticmethod
    def draw_interaction_area(frame, camera_area_ratio=0.6):
        """在影像上繪製交互區域"""
        frame_h, frame_w, _ = frame.shape
        margin_x = int(frame_w * (1 - camera_area_ratio) / 2)
        margin_y = int(frame_h * (1 - camera_area_ratio) / 2)
        cv2.rectangle(frame, 
                     (margin_x, margin_y), 
                     (frame_w - margin_x, frame_h - margin_y), 
                     (0, 255, 0), 2)
        return margin_x, margin_y
    
    @staticmethod
    def draw_info_text(frame, fps, rotation, flip_h, flip_v, gesture=None):
        """在影像上繪製信息文字"""
        frame_h, frame_w, _ = frame.shape
        
        # 顯示FPS
        cv2.putText(frame, f"FPS: ~{fps}", (frame_w - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 顯示方向信息
        orientation_info = f"Rot:{rotation}"
        if flip_h:
            orientation_info += " H"
        if flip_v:
            orientation_info += " V"
        cv2.putText(frame, orientation_info, (frame_w - 120, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # 顯示手勢
        if gesture:
            cv2.putText(frame, f"Gesture: {gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
