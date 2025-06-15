"""
Air Mouse 配置和常數
"""
import os
import pyautogui

# 設定 GPU 加速環境變數
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# 防止 pyautogui 移出螢幕邊界時引發異常
pyautogui.FAILSAFE = False

# 螢幕尺寸
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# 相機設定
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_BUFFER_SIZE = 1
CAMERA_AREA_RATIO = 0.65  # 縮小偵測區域

# 手勢檢測參數
FINGER_BENT_THRESHOLD = 0.05  # 降低閾值，讓手指接近更容易被識別
CLICK_TIME_THRESHOLD = 0.1    # 縮短點擊時間，讓點擊更靈敏
GESTURE_HISTORY_LENGTH = 3    # 減少歷史長度，讓手勢反應更快

# 效能參數
DEFAULT_FPS = 50
MIN_FPS = 10
MAX_FPS = 100
DEFAULT_FRAME_PROCESS_INTERVAL = 20

# 平滑參數
DEFAULT_SMOOTHING_FACTOR = 0.5
MIN_SMOOTHING = 0.2
MAX_SMOOTHING = 0.8

# UI 設定
UI_WINDOW_SIZE = "800x600"
UI_BG_COLOR = '#2b2b2b'
VIDEO_DISPLAY_SIZE = (480, 360)

print(f"螢幕解析度: {SCREEN_WIDTH} x {SCREEN_HEIGHT}")
