#!/usr/bin/env python3
"""
Air Mouse v2 - 模組化測試腳本
測試所有模組是否正常導入和工作
"""
import sys
import os

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_core_modules():
    """測試核心模組"""
    print("🔧 測試核心模組...")
    
    try:
        from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_AREA_RATIO
        print(f"  ✅ config.py - 螢幕尺寸: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        
        from core.gpu_detector import GPUDetector
        gpu_detector = GPUDetector()
        print(f"  ✅ gpu_detector.py - {gpu_detector.get_status_text()}")
        
        from core.gestures import GestureDetector, Gestures
        gesture_detector = GestureDetector()
        print(f"  ✅ gestures.py - 手勢類別: {len([attr for attr in dir(Gestures) if not attr.startswith('_')])} 種")
        
        from core.air_mouse import AirMouse, MouseController
        print("  ✅ air_mouse.py - AirMouse 和 MouseController 類")
        
    except Exception as e:
        print(f"  ❌ 核心模組錯誤: {e}")
        return False
    
    return True

def test_utils_modules():
    """測試工具模組"""
    print("\n🛠️ 測試工具模組...")
    
    try:
        from utils.image_processing import ImageProcessor
        print("  ✅ image_processing.py - ImageProcessor 類")
        
    except Exception as e:
        print(f"  ❌ 工具模組錯誤: {e}")
        return False
    
    return True

def test_ui_modules():
    """測試UI模組"""
    print("\n🖥️ 測試UI模組...")
    
    try:
        from ui.main_window import AirMouseUI
        print("  ✅ main_window.py - AirMouseUI 類")
        
    except Exception as e:
        print(f"  ❌ UI模組錯誤: {e}")
        return False
    
    return True

def test_integration():
    """測試整合功能"""
    print("\n🔄 測試模組整合...")
    
    try:
        # 測試 AirMouse 初始化
        from core import AirMouse
        air_mouse = AirMouse()
        print("  ✅ AirMouse 初始化成功")
        
        # 測試 UI 初始化（不啟動主循環）
        from ui import AirMouseUI
        ui = AirMouseUI()
        print("  ✅ AirMouseUI 初始化成功")
        
        # 清理資源
        air_mouse.cleanup()
        ui.on_closing()
        
    except Exception as e:
        print(f"  ❌ 整合測試錯誤: {e}")
        return False
    
    return True

def main():
    """主測試函數"""
    print("=" * 50)
    print("🚀 Air Mouse v2 - 模組化測試")
    print("=" * 50)
    
    tests = [
        test_core_modules,
        test_utils_modules, 
        test_ui_modules,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有模組測試通過！Air Mouse v2 已準備就緒。")
        print("\n🚀 啟動方式:")
        print("  GUI模式: python app.py")
        print("  命令行模式: python app.py --no-preview")
    else:
        print("⚠️ 某些模組測試失敗，請檢查錯誤信息。")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
