"""
Air Mouse 打包腳本
使用 PyInstaller 將 Air Mouse 打包成 .exe 檔案
"""

import os
import subprocess
import sys
from pathlib import Path

def create_spec_file():
    """創建 PyInstaller 規格檔案"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'mediapipe',
        'mediapipe.python._framework_bindings',
        'mediapipe.python.solutions',
        'cv2',
        'numpy',
        'tkinter',
        'PIL',
        'pyautogui',
        'keyboard',
        'tensorflow',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AirMouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 設為 False 以隱藏控制台視窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有圖示檔案可以在這裡指定
)
'''
    
    with open('air_mouse.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 已創建 air_mouse.spec 檔案")

def build_exe():
    """使用 PyInstaller 建構 .exe 檔案"""
    print("開始打包 Air Mouse...")
    print("這可能需要幾分鐘的時間，請耐心等待...")
    
    try:
        # 使用規格檔案建構
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',  # 清除之前的建構檔案
            'air_mouse.spec'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 打包成功！")
            print("✓ 可執行檔案位於: dist/AirMouse.exe")
            return True
        else:
            print("✗ 打包失敗")
            print("錯誤訊息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 打包過程發生錯誤: {e}")
        return False

def create_readme():
    """創建打包版本的說明檔案"""
    readme_content = """# Air Mouse v2.0 可執行版本

## 使用說明

1. 雙擊 AirMouse.exe 啟動程式
2. 確保攝像頭已連接並可正常運作
3. 在控制面板中調整設定
4. 點擊「啟動」按鈕開始手勢追蹤

## 功能特色

- 食指移動控制滑鼠
- 空白鍵進行左鍵點擊
- 圖形化使用者介面
- 可調整畫面方向與處理頻率
- 支援「只顯示手部位置」模式

## 系統需求

- Windows 10/11
- 攝像頭設備
- 充足的光線環境

## 疑難排解

如果程式無法啟動：
1. 確認攝像頭未被其他程式佔用
2. 檢查防毒軟體是否阻擋程式執行
3. 以系統管理員身分執行

## 版本資訊

- 版本: v2.0
- 建構日期: {build_date}
- 包含所有必要的相依套件
"""
    
    from datetime import datetime
    build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('dist/README_執行版.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content.format(build_date=build_date))
    
    print("✓ 已創建說明檔案")

def main():
    """主要打包流程"""
    print("=== Air Mouse .exe 打包工具 ===\n")
    
    # 檢查必要檔案
    if not os.path.exists('app.py'):
        print("✗ 找不到 app.py，請確認在正確的專案目錄中執行")
        return
    
    # 創建規格檔案
    create_spec_file()
    
    # 執行打包
    if build_exe():
        # 創建說明檔案
        if os.path.exists('dist'):
            create_readme()
        
        print("\n🎉 打包完成！")
        print("\n可執行檔案位置:")
        print("- 主程式: dist/AirMouse.exe")
        print("- 說明檔: dist/README_執行版.txt")
        print("\n你可以將整個 dist 資料夾複製到其他電腦使用。")
    else:
        print("\n❌ 打包失敗，請檢查錯誤訊息並重試。")

if __name__ == "__main__":
    main()
