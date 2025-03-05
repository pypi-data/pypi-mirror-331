#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基本使用示例

展示如何使用cctv_detector包进行图像检测
"""

import os
import sys
import json
from cctv_detector import Detector

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python basic_usage.py <图像路径>")
        return 1
    
    image_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在: {image_path}")
        return 1
    
    # 创建结果目录
    output_dir = "example_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 初始化检测器
    print("初始化检测器...")
    detector = Detector(
        model_path=None,  # 使用默认模型
        conf=0.25,
        iou=0.45,
        device="cuda" if Detector.is_cuda_available() else "cpu",
        output_dir=output_dir
    )
    
    # 处理图像
    print(f"处理图像: {image_path}")
    result = detector.process_image(image_path)
    
    # 检查结果
    if result["success"]:
        # 获取检测结果
        detections = result["data"]["detections"]
        print(f"检测到 {len(detections)} 个目标")
        
        # 获取告警信息
        alarms = result["data"]["alarms"]
        total_alarms = sum(len(alarms_list) for alarms_list in alarms.values())
        print(f"检测到 {total_alarms} 个告警")
        
        # 获取可视化结果路径
        vis_path = result["data"]["visualization_path"]
        print(f"可视化结果保存在: {vis_path}")
        
        # 保存JSON结果
        output_json = os.path.join(output_dir, "detection_result.json")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"JSON结果保存在: {output_json}")
        
        return 0
    else:
        print(f"处理失败: {result['error']}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 