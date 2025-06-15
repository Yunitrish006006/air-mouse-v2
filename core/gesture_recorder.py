"""
手勢錄入和管理模組
"""
import json
import time
import os
from datetime import datetime
import numpy as np
import mediapipe as mp
from typing import List, Dict, Optional, Tuple

mp_hands = mp.solutions.hands

class GestureData:
    """手勢資料類別"""
    
    def __init__(self, name: str, landmarks: List[List[float]], timestamp: str = None):
        self.name = name
        self.landmarks = landmarks  # 手部地標點座標
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.frame_count = len(landmarks)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'name': self.name,
            'landmarks': self.landmarks,
            'timestamp': self.timestamp,
            'frame_count': self.frame_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """從字典格式建立"""
        return cls(
            name=data['name'],
            landmarks=data['landmarks'],
            timestamp=data.get('timestamp', '')
        )

class GestureRecorder:
    """手勢錄入器"""
    
    def __init__(self, save_dir: str = "gestures"):
        self.save_dir = save_dir
        self.recording = False
        self.current_gesture_name = ""
        self.recorded_landmarks = []
        self.recording_start_time = None
        self.max_recording_time = 10.0  # 最大錄製時間（秒）
        self.min_frames = 5  # 最少錄製幀數
        
        # 建立儲存目錄
        os.makedirs(self.save_dir, exist_ok=True)
        
        # MediaPipe 手部追蹤
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
    
    def start_recording(self, gesture_name: str) -> bool:
        """開始錄製手勢"""
        if self.recording:
            return False
        
        self.recording = True
        self.current_gesture_name = gesture_name
        self.recorded_landmarks = []
        self.recording_start_time = time.time()
        
        print(f"[錄入] 開始錄製手勢: {gesture_name}")
        return True
    
    def stop_recording(self) -> Optional[GestureData]:
        """停止錄製手勢"""
        if not self.recording:
            return None
        
        self.recording = False
        
        # 檢查錄製的資料是否足夠
        if len(self.recorded_landmarks) < self.min_frames:
            print(f"[錄入] 錄製失敗: 幀數不足 ({len(self.recorded_landmarks)} < {self.min_frames})")
            return None
        
        # 建立手勢資料
        gesture_data = GestureData(
            name=self.current_gesture_name,
            landmarks=self.recorded_landmarks
        )
        
        print(f"[錄入] 錄製完成: {self.current_gesture_name} ({len(self.recorded_landmarks)} 幀)")
        return gesture_data
    
    def cancel_recording(self):
        """取消錄製"""
        if self.recording:
            self.recording = False
            self.recorded_landmarks = []
            print(f"[錄入] 取消錄製: {self.current_gesture_name}")
    
    def process_frame(self, rgb_frame) -> Tuple[bool, Optional[List[float]]]:
        """處理影格並錄製手部地標"""
        if not self.recording:
            return False, None
        
        # 檢查錄製時間是否超時
        if time.time() - self.recording_start_time > self.max_recording_time:
            print(f"[錄入] 錄製超時，自動停止")
            return False, None
        
        # 檢測手部
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            # 取得第一隻手的地標點
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # 將地標點轉換為列表格式
            landmarks_list = []
            for landmark in hand_landmarks.landmark:
                landmarks_list.extend([landmark.x, landmark.y, landmark.z])
            
            self.recorded_landmarks.append(landmarks_list)
            return True, landmarks_list
        
        return False, None
    
    def save_gesture(self, gesture_data: GestureData) -> bool:
        """儲存手勢資料到檔案"""
        try:
            filename = f"{gesture_data.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.save_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(gesture_data.to_dict(), f, ensure_ascii=False, indent=2)
            
            print(f"[錄入] 手勢已儲存: {filepath}")
            return True
        
        except Exception as e:
            print(f"[錄入] 儲存失敗: {e}")
            return False
    
    def load_gesture(self, filepath: str) -> Optional[GestureData]:
        """載入手勢資料"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return GestureData.from_dict(data)
        
        except Exception as e:
            print(f"[錄入] 載入失敗: {e}")
            return None
    
    def list_saved_gestures(self) -> List[str]:
        """列出所有已儲存的手勢檔案"""
        try:
            files = [f for f in os.listdir(self.save_dir) if f.endswith('.json')]
            return sorted(files)
        except:
            return []
    
    def delete_gesture(self, filename: str) -> bool:
        """刪除手勢檔案"""
        try:
            filepath = os.path.join(self.save_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[錄入] 已刪除手勢: {filename}")
                return True
            return False
        except Exception as e:
            print(f"[錄入] 刪除失敗: {e}")
            return False
    
    def get_recording_status(self) -> Dict:
        """取得錄製狀態資訊"""
        if not self.recording:
            return {
                'recording': False,
                'gesture_name': '',
                'frame_count': 0,
                'elapsed_time': 0,
                'remaining_time': 0
            }
        
        elapsed_time = time.time() - self.recording_start_time
        remaining_time = max(0, self.max_recording_time - elapsed_time)
        
        return {
            'recording': True,
            'gesture_name': self.current_gesture_name,
            'frame_count': len(self.recorded_landmarks),
            'elapsed_time': elapsed_time,
            'remaining_time': remaining_time
        }
    
    def close(self):
        """釋放資源"""
        if hasattr(self, 'hands'):
            self.hands.close()

class GestureAnalyzer:
    """手勢分析器"""
    
    @staticmethod
    def analyze_gesture(gesture_data: GestureData) -> Dict:
        """分析手勢特徵"""
        if not gesture_data.landmarks:
            return {}
        
        landmarks_array = np.array(gesture_data.landmarks)
        
        # 基本統計資訊
        analysis = {
            'frame_count': gesture_data.frame_count,
            'duration': gesture_data.frame_count * 0.033,  # 假設30FPS
            'landmark_mean': landmarks_array.mean(axis=0).tolist(),
            'landmark_std': landmarks_array.std(axis=0).tolist(),
            'movement_range': {
                'x_range': landmarks_array[:, ::3].max() - landmarks_array[:, ::3].min(),
                'y_range': landmarks_array[:, 1::3].max() - landmarks_array[:, 1::3].min(),
                'z_range': landmarks_array[:, 2::3].max() - landmarks_array[:, 2::3].min(),
            }
        }
        
        return analysis
    
    @staticmethod
    def compare_gestures(gesture1: GestureData, gesture2: GestureData) -> float:
        """比較兩個手勢的相似度（0-1，1為完全相同）"""
        if not gesture1.landmarks or not gesture2.landmarks:
            return 0.0
        
        # 簡單的相似度計算（基於平均地標點距離）
        arr1 = np.array(gesture1.landmarks)
        arr2 = np.array(gesture2.landmarks)
        
        # 標準化長度
        min_length = min(len(arr1), len(arr2))
        arr1 = arr1[:min_length]
        arr2 = arr2[:min_length]
        
        # 計算平均差異
        diff = np.mean(np.abs(arr1 - arr2))
        
        # 轉換為相似度（0-1）
        similarity = max(0, 1 - diff * 10)  # 調整係數
        
        return similarity
