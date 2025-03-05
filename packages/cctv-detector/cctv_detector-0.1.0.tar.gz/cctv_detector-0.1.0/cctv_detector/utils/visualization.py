"""
可视化工具模块

提供检测结果的可视化功能
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Union, Optional


def visualize_detection(
    image: np.ndarray,
    detections: List[Dict],
    colors: Optional[Dict[str, Tuple[int, int, int]]] = None
) -> np.ndarray:
    """
    在图像上可视化检测结果
    
    参数:
        image: 原始图像（OpenCV格式，BGR）
        detections: 检测结果列表
        colors: 类别对应的颜色字典
        
    返回:
        可视化后的图像
    """
    # 默认颜色配置
    if colors is None:
        colors = {
            "covered": (0, 255, 0),      # 绿色 - 已覆盖
            "partially": (0, 165, 255),  # 橙色 - 部分覆盖
            "uncovered": (0, 0, 255),    # 红色 - 未覆盖
            "person": (255, 0, 0),       # 蓝色 - 人员
            "ship": (255, 255, 0),       # 青色 - 船只
            "machinery": (128, 0, 128),  # 紫色 - 机械
            "default": (255, 255, 255)   # 白色 - 默认
        }
    
    # 创建图像副本
    vis_image = image.copy()
    
    # 绘制每个检测结果
    for det in detections:
        # 获取边界框和类别
        bbox = det["bbox"]
        cls_name = det["class_name"]
        conf = det["confidence"]
        
        # 获取颜色
        color = colors.get(cls_name, colors.get("default", (255, 255, 255)))
        
        # 绘制边界框
        cv2.rectangle(
            vis_image,
            (bbox["x1"], bbox["y1"]),
            (bbox["x2"], bbox["y2"]),
            color,
            2
        )
        
        # 准备标签文本
        label = f"{cls_name} {conf:.2f}"
        
        # 获取文本大小
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        
        # 绘制标签背景
        cv2.rectangle(
            vis_image,
            (bbox["x1"], bbox["y1"] - text_height - 5),
            (bbox["x1"] + text_width, bbox["y1"]),
            color,
            -1
        )
        
        # 绘制标签文本
        cv2.putText(
            vis_image,
            label,
            (bbox["x1"], bbox["y1"] - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )
    
    return vis_image 