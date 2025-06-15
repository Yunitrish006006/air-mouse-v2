"""
GPU 檢測和初始化模組
"""
import cv2

class GPUDetector:
    """GPU 檢測和管理類"""
    
    def __init__(self):
        self.opencv_gpu_available = False
        self.tf_gpu_available = False
        self._detect_gpu()
    
    def _detect_gpu(self):
        """檢測可用的 GPU 加速"""
        self._detect_opencv_gpu()
        self._detect_tensorflow_gpu()
    
    def _detect_opencv_gpu(self):
        """檢測 OpenCV GPU 支援"""
        try:
            gpu_count = cv2.cuda.getCudaEnabledDeviceCount()
            if gpu_count > 0:
                self.opencv_gpu_available = True
                print(f"檢測到 {gpu_count} 個 OpenCV 支持的 GPU 設備")
            else:
                print("未檢測到 OpenCV 支持的 GPU")
        except Exception as e:
            print(f"OpenCV GPU 檢測失敗: {e}")
    
    def _detect_tensorflow_gpu(self):
        """檢測 TensorFlow GPU 支援"""
        try:
            import tensorflow as tf
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                self.tf_gpu_available = True
                print(f"檢測到 {len(gpus)} 個 TensorFlow 支持的 GPU 設備")
                # 設置動態內存分配
                for gpu in gpus:
                    try:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    except:
                        print(f"無法為 GPU {gpu} 設置動態內存分配")
            else:
                print("未檢測到 TensorFlow 支持的 GPU")
        except Exception as e:
            print(f"TensorFlow GPU 檢測失敗: {e}")
    
    def get_status_text(self):
        """獲取 GPU 狀態文字"""
        status = "GPU: "
        if self.opencv_gpu_available:
            status += "OpenCV✓ "
        if self.tf_gpu_available:
            status += "TensorFlow✓"
        if not (self.opencv_gpu_available or self.tf_gpu_available):
            status += "未偵測到"
        return status
