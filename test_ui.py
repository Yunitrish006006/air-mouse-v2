"""
Air Mouse GUI 測試腳本
這個腳本可以單獨運行來測試UI功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import time

def test_camera():
    """測試攝像頭是否可用"""
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return True, "攝像頭測試成功"
            else:
                return False, "攝像頭無法讀取畫面"
        else:
            return False, "無法打開攝像頭"
    except Exception as e:
        return False, f"攝像頭測試失敗: {e}"

def test_ui():
    """測試UI功能"""
    root = tk.Tk()
    root.title("Air Mouse UI 測試")
    root.geometry("400x300")
    
    # 測試結果顯示
    test_frame = ttk.LabelFrame(root, text="測試結果", padding=10)
    test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 攝像頭測試
    camera_success, camera_msg = test_camera()
    camera_status = "✓" if camera_success else "✗"
    camera_color = "green" if camera_success else "red"
    
    camera_label = tk.Label(test_frame, text=f"{camera_status} 攝像頭: {camera_msg}", 
                           fg=camera_color, font=("Arial", 10))
    camera_label.pack(pady=5)
    
    # GPU測試結果
    try:
        import tensorflow as tf
        gpus = tf.config.experimental.list_physical_devices('GPU')
        tf_gpu = len(gpus) > 0
    except:
        tf_gpu = False
    
    try:
        opencv_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
    except:
        opencv_gpu = False
    
    gpu_status = "✓" if (tf_gpu or opencv_gpu) else "✗"
    gpu_color = "green" if (tf_gpu or opencv_gpu) else "orange"
    gpu_msg = f"TensorFlow GPU: {'是' if tf_gpu else '否'}, OpenCV GPU: {'是' if opencv_gpu else '否'}"
    
    gpu_label = tk.Label(test_frame, text=f"{gpu_status} GPU加速: {gpu_msg}", 
                        fg=gpu_color, font=("Arial", 10))
    gpu_label.pack(pady=5)
    
    # 依賴項測試
    dependencies = ['cv2', 'mediapipe', 'numpy', 'pyautogui', 'PIL']
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    deps_status = "✓" if not missing_deps else "✗"
    deps_color = "green" if not missing_deps else "red"
    deps_msg = "所有依賴項已安裝" if not missing_deps else f"缺少: {', '.join(missing_deps)}"
    
    deps_label = tk.Label(test_frame, text=f"{deps_status} 依賴項: {deps_msg}", 
                         fg=deps_color, font=("Arial", 10))
    deps_label.pack(pady=5)
    
    # 啟動按鈕
    if camera_success and not missing_deps:
        def start_air_mouse():
            root.destroy()
            import app
            ui = app.AirMouseUI()
            ui.run()
        
        start_button = ttk.Button(test_frame, text="啟動 Air Mouse", command=start_air_mouse)
        start_button.pack(pady=20)
    else:
        error_msg = "請確保攝像頭連接正常且所有依賴項已安裝"
        error_label = tk.Label(test_frame, text=error_msg, fg="red", font=("Arial", 10))
        error_label.pack(pady=20)
    
    # 退出按鈕
    quit_button = ttk.Button(test_frame, text="退出", command=root.destroy)
    quit_button.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_ui()
