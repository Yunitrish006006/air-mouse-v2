"""
Air Mouse 配置和常數
"""
import os

# 設定 GPU 加速環境變數
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# 嘗試修復 X11 認證問題
def setup_x11_auth():
    """設置 X11 認證"""
    try:
        # 確保 .Xauthority 文件存在
        xauth_file = os.path.expanduser('~/.Xauthority')
        if not os.path.exists(xauth_file):
            open(xauth_file, 'a').close()
            os.chmod(xauth_file, 0o600)
        
        # 設置環境變數
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0'
            
    except Exception as e:
        print(f"警告: 無法設置 X11 認證: {e}")

# 初始化 X11 認證
setup_x11_auth()

# 延遲導入 pyautogui 並添加錯誤處理
_pyautogui = None
_screen_width = 1920  # 默認寬度
_screen_height = 1080  # 默認高度

def get_pyautogui():
    """安全地獲取 pyautogui 模組"""
    global _pyautogui, _screen_width, _screen_height
    
    if _pyautogui is None:
        try:
            import pyautogui
            # 防止 pyautogui 移出螢幕邊界時引發異常
            pyautogui.FAILSAFE = False
            # 移除 PyAutoGUI 的內建延遲以提高響應速度
            pyautogui.PAUSE = 0
            pyautogui.MINIMUM_DURATION = 0
            pyautogui.MINIMUM_SLEEP = 0
            
            # 獲取螢幕尺寸
            _screen_width, _screen_height = pyautogui.size()
            _pyautogui = pyautogui
            
        except Exception as e:
            print(f"錯誤: 無法初始化 pyautogui: {e}")
            print("請確保您在支援 GUI 的環境中運行此程序")
            # 創建一個模擬對象以防止程序崩潰
            class MockPyAutoGUI:
                FAILSAFE = False
                PAUSE = 0
                MINIMUM_DURATION = 0
                MINIMUM_SLEEP = 0
                
                @staticmethod
                def size():
                    return (_screen_width, _screen_height)
                
                @staticmethod
                def moveTo(*args, **kwargs):
                    pass
                
                @staticmethod
                def click(*args, **kwargs):
                    pass
                    
            _pyautogui = MockPyAutoGUI()
    
    return _pyautogui

# 螢幕尺寸的 getter 函數
def get_screen_size():
    """獲取螢幕尺寸"""
    pyautogui = get_pyautogui()
    return pyautogui.size()

# 為了向後兼容，創建螢幕尺寸常數函數
def get_screen_width():
    return get_screen_size()[0]

def get_screen_height():
    return get_screen_size()[1]

# 創建初始常數
SCREEN_WIDTH = 1920  # 默認值，會在首次使用時更新
SCREEN_HEIGHT = 1080  # 默認值，會在首次使用時更新

def update_screen_constants():
    """更新螢幕常數"""
    global SCREEN_WIDTH, SCREEN_HEIGHT
    width, height = get_screen_size()
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height

# 初始化螢幕常數
update_screen_constants()

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

# 在模組載入時顯示螢幕解析度
def print_screen_info():
    """顯示螢幕解析度信息"""
    try:
        width, height = get_screen_size()
        print(f"螢幕解析度: {width} x {height}")
    except Exception as e:
        print(f"無法獲取螢幕解析度: {e}")

# 延遲執行螢幕信息顯示
if __name__ != "__main__":
    try:
        print_screen_info()
    except:
        pass  # 忽略錯誤，避免在導入時崩潰
