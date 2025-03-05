#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用示例：检测单张图像
"""

import os
import json
from cctv_detector import DetectionProcessor

def main():
    # 配置参数
    model_path = "models/segment_best228.pt"  # 模型路径
    image_path = "test.jpg"  # 测试图像路径
    output_dir = "results"  # 输出目录
    
    # 创建检测器
    detector = DetectionProcessor(
        model_path=model_path,
        conf=0.25,
        iou=0.45,
        device="cuda" if torch.cuda.is_available() else "cpu",
        output_dir=output_dir
    )
    
    # 处理图像
    result = detector.process_image(image_path)
    
    # 打印结果
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 