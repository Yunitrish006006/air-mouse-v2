#!/usr/bin/env python3
"""
測試新增的只顯示手部位置功能
"""
import sys
import os

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hands_only_display():
    """測試只顯示手部位置功能"""
    try:
        from ui.main_window import AirMouseUI
        print("✓ 正在測試只顯示手部位置功能...")
        
        # 創建 UI 實例（不啟動主循環）
        ui = AirMouseUI()
        
        # 檢查新增的屬性
        if hasattr(ui, 'show_hands_only'):
            print("✓ show_hands_only 屬性存在")
        else:
            print("✗ show_hands_only 屬性不存在")
            return False
            
        if hasattr(ui, 'display_mode_button'):
            print("✓ display_mode_button 按鈕存在")
        else:
            print("✗ display_mode_button 按鈕不存在")
            return False
            
        if hasattr(ui, 'toggle_display_mode'):
            print("✓ toggle_display_mode 方法存在")
        else:
            print("✗ toggle_display_mode 方法不存在")
            return False
            
        if hasattr(ui, 'create_hands_only_frame'):
            print("✓ create_hands_only_frame 方法存在")
        else:
            print("✗ create_hands_only_frame 方法不存在")
            return False
        
        # 測試切換功能
        print("✓ 測試切換到只顯示手部位置模式...")
        ui.show_hands_only.set(True)
        ui.toggle_display_mode()
        
        print("✓ 測試切換回完整畫面模式...")
        ui.show_hands_only.set(False)
        ui.toggle_display_mode()
        
        # 清理
        ui.air_mouse.cleanup()
        ui.root.destroy()
        
        print("✓ 只顯示手部位置功能測試通過")
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        return False

def main():
    print("=== 只顯示手部位置功能測試 ===\n")
    
    if test_hands_only_display():
        print("\n🎉 所有測試通過！新功能準備就緒。")
        print("\n使用說明：")
        print("1. 啟動 Air Mouse: python app.py")
        print("2. 在控制面板中勾選「只顯示手部位置」")
        print("3. 點擊「啟動」開始手勢追蹤")
        print("4. 現在只會顯示手部骨架和食指位置，背景為黑色")
    else:
        print("\n❌ 測試失敗，請檢查程式碼。")

if __name__ == "__main__":
    main()
