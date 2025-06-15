"""
Air Mouse 配置和常數
"""
import os
import pyautogui

# 設定 GPU 加速環境變數
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# 防止 pyautogui 移出螢幕邊界時引發異常
pyautogui.FAILSAFE = False
# 移除 PyAutoGUI 的內建延遲以提高響應速度
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0

# 螢幕尺寸
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# 相機設定
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_BUFFER_SIZE = 1
CAMERA_AREA_RATIO = 0.65  # 縮小偵測區域
CAMERA_VERTICAL_OFFSET = -0.1  # 框向上偏移 10%

# 手勢檢測參數
FINGER_BENT_THRESHOLD = 0.05  # 降低閾值，讓手指接近更容易被識別
CLICK_TIME_THRESHOLD = 0.1    # 縮短點擊時間，讓點擊更靈敏
GESTURE_HISTORY_LENGTH = 3    # 減少歷史長度，讓手勢反應更快

# 效能參數
DEFAULT_FPS = 60  # 提高到60FPS
MIN_FPS = 30
MAX_FPS = 120
DEFAULT_FRAME_PROCESS_INTERVAL = 16  # 約60FPS (1000/60≈16)

# 平滑參數（提高響應速度）
DEFAULT_SMOOTHING_FACTOR = 0.8  # 提高平滑係數，減少延遲
MIN_SMOOTHING = 0.5
MAX_SMOOTHING = 1.0

# UI 設定
UI_WINDOW_SIZE = "800x600"
UI_BG_COLOR = '#2b2b2b'
VIDEO_DISPLAY_SIZE = (480, 360)

print(f"螢幕解析度: {SCREEN_WIDTH} x {SCREEN_HEIGHT}")
