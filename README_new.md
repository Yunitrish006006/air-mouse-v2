# Air Mouse v2 - 手勢控制滑鼠

使用攝像頭和 MediaPipe 實現的手勢控制滑鼠系統，採用模組化設計，支援 GPU 加速、多種操作模式和完整的圖形化界面。

## 🚀 功能特色

### 核心功能

- **手勢識別**：使用 MediaPipe 進行精確的手部追蹤
- **滑鼠控制**：支援移動、點擊、拖曳、滾動等操作
- **GPU 加速**：自動檢測並使用 OpenCV CUDA 和 TensorFlow GPU 加速
- **效能優化**：可調整處理頻率、支援無預覽高效能模式

### 操作模式

- **圖形化界面**：完整的 tkinter GUI，即時預覽和設定調整
- **命令行模式**：高效能無預覽模式，適合資源受限環境

### 進階功能

- **畫面方向調整**：支援旋轉、水平/垂直翻轉
- **自適應設定**：動態調整處理頻率和平滑度
- **多執行緒處理**：視頻處理與 UI 分離，確保流暢性

## 🏗️ 系統架構

### 模組化設計

```
air-mouse-v2/
├── app.py                 # 主啟動文件
├── core/                  # 核心功能模組
│   ├── __init__.py       
│   ├── config.py         # 全域設定和常數
│   ├── gpu_detector.py   # GPU 檢測和管理
│   ├── gestures.py       # 手勢識別引擎
│   └── air_mouse.py      # Air Mouse 主控制器
├── ui/                   # 使用者介面
│   ├── __init__.py
│   └── main_window.py    # 圖形化主視窗
├── utils/                # 工具模組
│   ├── __init__.py
│   └── image_processing.py # 圖像處理工具
└── requirements.txt      # 依賴套件
```

### 核心模組說明

- **config.py**：集中管理所有設定參數和常數
- **gpu_detector.py**：自動檢測 OpenCV 和 TensorFlow GPU 支援
- **gestures.py**：手勢定義、檢測和識別邏輯
- **air_mouse.py**：主要的 Air Mouse 控制器和滑鼠操作
- **image_processing.py**：影像處理、方向調整、GPU 加速處理
- **main_window.py**：完整的 tkinter GUI 界面

## 📋 系統需求

- Python 3.7+
- 攝像頭（USB或內建）
- Windows 10/11（推薦）

### 依賴套件

- OpenCV (cv2)
- MediaPipe
- NumPy
- PyAutoGUI
- Pillow
- tkinter（Python 內建）

## 🛠 安裝步驟

1. **克隆或下載項目**

   ```bash
   git clone <repository-url>
   cd air-mouse-v2
   ```

2. **安裝依賴項**

   ```bash
   pip install -r requirements.txt
   ```

3. **運行應用程序**

   ```bash
   # GUI模式（推薦）
   python app.py
   
   # 或雙擊 start.bat
   ```

## 🎮 使用方法

### 手勢控制

- **移動滑鼠**：伸出食指
- **左鍵點擊**：食指和中指伸直並快速靠近
- **右鍵點擊**：食指和大拇指伸直並快速靠近
- **拖曳**：食指和中指伸直保持距離
- **滾動**：五指伸直，上下移動手部

### GUI控制面板

- **啟動/停止**：控制手勢追蹤的開始與停止
- **FPS調整**：使用滑桿調整處理頻率（10-100 FPS）
- **畫面旋轉**：點擊按鈕調整攝像頭方向
- **狀態監控**：查看當前運行狀態和系統信息

### 命令行選項

```bash
# 顯示幫助
python app.py --help

# 高效能模式（無GUI預覽）
python app.py --no-preview

# 設定初始FPS
python app.py --fps 60

# 設定初始畫面方向
python app.py --rotation 90 --flip-h

# 禁用GPU加速
python app.py --no-gpu
```

## 🔧 進階設定

### 畫面方向調整

如果您的攝像頭安裝方向與標準不同，可以使用以下方法調整：

1. **GUI模式**：使用「畫面方向」面板中的按鈕
2. **命令行**：使用 `--rotation`, `--flip-h`, `--flip-v` 參數
3. **運行時**：在GUI中隨時調整，或使用快捷鍵（僅限非預覽模式）

### 效能調優

- **FPS設定**：較高的 FPS 提供更好的反應速度，但增加 CPU/GPU 負擔
- **GPU 加速**：自動檢測可用的 GPU 加速，可手動禁用
- **無預覽模式**：使用 `--no-preview` 可大幅提升效能

## 🔍 故障排除

### 常見問題

1. **攝像頭無法開啟**
   - 檢查攝像頭是否被其他應用程式佔用
   - 確認攝像頭驅動程式正常

2. **手勢識別不準確**
   - 調整攝像頭角度和光線條件
   - 使用畫面方向調整功能
   - 確保手部在綠色交互區域內

3. **效能問題**
   - 降低FPS設定
   - 啟用 `--no-preview` 模式
   - 檢查 GPU 加速是否正常運作

### GPU 加速支援

系統會自動檢測以下 GPU 加速：

- **OpenCV CUDA**：用於影像處理加速
- **TensorFlow GPU**：用於 MediaPipe 手部檢測加速

如果遇到 GPU 相關問題，可以使用 `--no-gpu` 參數強制使用 CPU 模式。

## 🚀 開發和擴展

### 模組化架構優勢

1. **可維護性**：功能分離，便於除錯和修改
2. **可擴展性**：容易添加新功能或手勢
3. **可測試性**：各模組獨立，便於單元測試
4. **可重用性**：模組可在其他項目中重複使用

### 自定義手勢

要添加新的手勢，請修改 `core/gestures.py`：

```python
# 在 Gestures 類中添加新手勢
NEW_GESTURE = "new_gesture"

# 在 GestureDetector.detect_gesture() 方法中添加檢測邏輯
```

### 自定義UI

要修改界面，請編輯 `ui/main_window.py`，所有UI相關的代碼都集中在此文件中。

## 📄 授權

本項目採用 MIT 授權條款，詳見 LICENSE 文件。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進本項目！

---

*Air Mouse v2 - 讓手勢控制更簡單、更智能！*
