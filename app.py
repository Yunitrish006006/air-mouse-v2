#!/usr/bin/env python3
"""
Air Mouse - 使用手勢控制滑鼠
主啟動文件
"""
import argparse
import sys
import os

# 確保可以導入自定義模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import AirMouse
from ui import AirMouseUI


def print_welcome_message():
    """顯示歡迎信息"""
    print("啟動Air Mouse...")
    print("請將手放在攝像頭前的桌面上")
    print("- 只伸出食指：移動滑鼠")
    print("- 食指和中指伸直並靠近：左鍵點擊")
    print("- 食指和大拇指伸直並靠近：右鍵點擊")
    print("- 食指和中指伸直保持距離：拖曳")
    print("- 五指伸直上下移動：滾動")
    print("- 按ESC鍵退出")
    print("- 按P鍵切換畫面預覽（關閉預覽可提升效能）")
    print("- 按+/-鍵增加/減少處理頻率（影響效能和反應速度）")
    print("- 按R鍵旋轉畫面90度（調整手部方向）")
    print("- 按H鍵水平翻轉畫面")
    print("- 按V鍵垂直翻轉畫面")
    print("- 按0鍵重置畫面方向")


def run_cli_mode(args):
    """運行命令行模式"""
    air_mouse = AirMouse()
    
    # 設定處理頻率 (轉換為處理間隔毫秒)
    fps = max(10, min(100, args.fps))
    air_mouse.frame_process_interval = int(1000 / fps)
    print(f"處理頻率: 約 {fps} FPS")
    
    # 設定畫面方向
    air_mouse.frame_rotation = args.rotation
    air_mouse.flip_horizontal = args.flip_h
    air_mouse.flip_vertical = args.flip_v
    if args.rotation != 0 or args.flip_h or args.flip_v:
        print(f"畫面方向設定: 旋轉{args.rotation}度, "
              f"水平翻轉{'開啟' if args.flip_h else '關閉'}, "
              f"垂直翻轉{'開啟' if args.flip_v else '關閉'}")
    
    air_mouse.show_preview = False
    print("已啟動高效能模式（無預覽）")
    
    if args.no_gpu:
        air_mouse.use_gpu = False
        print("已禁用 GPU 加速，使用 CPU 模式運行")
    else:
        if air_mouse.opencv_gpu_available:
            print("已啟用 OpenCV GPU 加速")
        if air_mouse.tf_gpu_available:
            print("已啟用 MediaPipe/TensorFlow GPU 加速")
        if not (air_mouse.opencv_gpu_available or air_mouse.tf_gpu_available):
            print("未檢測到可用的 GPU 加速，使用 CPU 模式運行")
    
    air_mouse.run()


def run_gui_mode(args):
    """運行圖形化界面模式"""
    ui = AirMouseUI()
    
    # 從命令行參數設定初始值
    ui.set_initial_settings(
        rotation=args.rotation,
        flip_h=args.flip_h,
        flip_v=args.flip_v,
        fps=max(10, min(100, args.fps)),
        use_gpu=not args.no_gpu
    )
    
    ui.run()


def main():
    """主函數"""
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="Air Mouse - 使用手勢控制滑鼠")
    parser.add_argument('--no-preview', action='store_true', 
                        help='啟動時不顯示預覽畫面 (提升效能)')
    parser.add_argument('--fps', type=int, default=50, 
                        help='設定處理頻率 (10-100 之間，數值越小越流暢但CPU負擔越重)')
    parser.add_argument('--no-gpu', action='store_true', 
                        help='禁用 GPU 加速 (在 GPU 出現問題時使用)')
    parser.add_argument('--rotation', type=int, choices=[0, 90, 180, 270], default=0, 
                        help='設定攝像頭畫面初始旋轉角度 (0, 90, 180, 270)')
    parser.add_argument('--flip-h', action='store_true', 
                        help='啟動時水平翻轉畫面')
    parser.add_argument('--flip-v', action='store_true', 
                        help='啟動時垂直翻轉畫面')
    
    args = parser.parse_args()
    
    print_welcome_message()
    
    # 選擇運行模式
    if args.no_preview:
        run_cli_mode(args)
    else:
        run_gui_mode(args)


if __name__ == "__main__":
    main()
