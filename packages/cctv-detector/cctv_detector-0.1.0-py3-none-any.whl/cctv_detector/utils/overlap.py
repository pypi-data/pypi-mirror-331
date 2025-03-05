"""
重叠计算工具模块

提供边界框重叠计算功能
"""

from typing import Dict, Union, Tuple


def calculate_overlap(
    box1: Union[Dict, Tuple[int, int, int, int]],
    box2: Union[Dict, Tuple[int, int, int, int]]
) -> float:
    """
    计算两个边界框的重叠率 (IoU)
    
    参数:
        box1: 第一个边界框，可以是字典 {"x1": x1, "y1": y1, "x2": x2, "y2": y2} 或元组 (x1, y1, x2, y2)
        box2: 第二个边界框，格式同box1
        
    返回:
        重叠率，范围 [0, 1]
    """
    # 处理不同的输入格式
    if isinstance(box1, dict):
        x1_1, y1_1, x2_1, y2_1 = box1["x1"], box1["y1"], box1["x2"], box1["y2"]
    else:
        x1_1, y1_1, x2_1, y2_1 = box1
    
    if isinstance(box2, dict):
        x1_2, y1_2, x2_2, y2_2 = box2["x1"], box2["y1"], box2["x2"], box2["y2"]
    else:
        x1_2, y1_2, x2_2, y2_2 = box2
    
    # 计算交集区域
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    # 检查是否有交集
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    # 计算交集面积
    intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
    
    # 计算两个框的面积
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    # 计算并集面积
    union_area = box1_area + box2_area - intersection_area
    
    # 计算IoU
    iou = intersection_area / union_area if union_area > 0 else 0.0
    
    return iou 