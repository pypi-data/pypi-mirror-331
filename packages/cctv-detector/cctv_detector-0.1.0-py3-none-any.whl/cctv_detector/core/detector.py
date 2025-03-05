"""
检测处理器模块

提供图像和视频的对象检测和告警功能
"""

import os
import sys
import json
import uuid
import numpy as np
import torch
from ultralytics import YOLO
import cv2
import time
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

from ..models import get_default_model_path
from ..utils.visualization import visualize_detection
from ..utils.overlap import calculate_overlap
from .result import DetectionResult


class DetectionProcessor:
    """
    检测处理器类
    
    用于处理图像和视频中的对象检测，并提供告警分析
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None, 
        conf: float = 0.25, 
        iou: float = 0.45, 
        device: Optional[str] = None, 
        output_dir: str = "results"
    ):
        """
        初始化检测处理器
        
        参数:
            model_path: 模型路径，如果为None则使用默认模型
            conf: 置信度阈值
            iou: IOU阈值
            device: 推理设备 ('cuda' 或 'cpu')
            output_dir: 结果输出目录
        """
        self.conf = conf
        self.iou = iou
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 设备配置
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        if self.device == 'cuda':
            torch.backends.cudnn.benchmark = True
        
        # 加载模型
        if model_path is None:
            model_path = get_default_model_path()
            
        print(f"加载模型: {model_path}, 使用设备: {self.device}")
        self.model = YOLO(model_path)
        self.model.to(self.device)
        
        # 配置颜色和告警类型
        self.configure_settings()
    
    def configure_settings(self):
        """配置检测和告警设置"""
        # 告警类型配置
        self.alarm_types = {
            "person_intrusion": ["person", "人", "人员"],
            "vessel_approach": ["ship", "boat", "vessel", "船", "船只"],
            "machinery_intrusion": ["machinery", "machine", "机械"],
            "camera_alarm": ["camera_error", "error"]  # 摄像头异常检测
        }
        
        # 检测框颜色配置 (BGR格式)
        self.colors = {
            "covered": (0, 255, 0),      # 绿色 - 已覆盖
            "partially": (0, 165, 255),  # 橙色 - 部分覆盖
            "uncovered": (0, 0, 255),    # 红色 - 未覆盖
            "person": (255, 0, 0),       # 蓝色 - 人员
            "ship": (255, 255, 0),       # 青色 - 船只
            "machinery": (128, 0, 128),  # 紫色 - 机械
            "default": (255, 255, 255)   # 白色 - 默认
        }
    
    def process_image(self, image_path: str) -> Dict:
        """
        处理单张图像并返回检测结果
        
        参数:
            image_path: 图像文件路径
            
        返回:
            包含检测结果和告警信息的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return {"success": False, "error": f"文件不存在: {image_path}"}
            
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {"success": False, "error": f"无法读取图像: {image_path}"}
            
            # 记录开始时间
            start_time = time.time()
            
            # 执行检测
            results = self.model(image, conf=self.conf, iou=self.iou, verbose=False)
            
            # 处理检测结果
            detections = self._process_results(results)
            
            # 分析告警
            alarms = self._analyze_alarms(detections)
            
            # 可视化结果
            vis_image = visualize_detection(image.copy(), detections, self.colors)
            
            # 生成唯一文件名
            base_name = os.path.basename(image_path)
            result_id = uuid.uuid4().hex[:8]
            vis_path = os.path.join(self.output_dir, f"{os.path.splitext(base_name)[0]}_result_{result_id}{os.path.splitext(base_name)[1]}")
            
            # 保存可视化结果
            cv2.imwrite(vis_path, vis_image)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 构建结果
            result = DetectionResult(
                success=True,
                image_path=image_path,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                processing_time=process_time,
                detections=detections,
                alarms=alarms,
                visualization_path=vis_path
            )
            
            return result.to_dict()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _process_results(self, results) -> List[Dict]:
        """处理YOLOv8检测结果"""
        detections = []
        
        # 获取第一个结果（单张图像）
        result = results[0]
        
        # 处理检测框
        if hasattr(result, 'boxes') and len(result.boxes) > 0:
            boxes = result.boxes
            for i, box in enumerate(boxes):
                # 获取坐标和置信度
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = result.names[cls_id]
                
                # 添加到检测列表
                detections.append({
                    "id": i,
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": conf,
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2)
                    }
                })
        
        return detections
    
    def _analyze_alarms(self, detections: List[Dict]) -> Dict[str, List]:
        """分析检测结果中的告警情况"""
        alarms = {
            "person_intrusion": [],
            "vessel_approach": [],
            "machinery_intrusion": [],
            "camera_alarm": []
        }
        
        # 找到所有货舱区域
        cargo_areas = []
        for det in detections:
            if det["class_name"] in ["covered", "partially", "uncovered"]:
                cargo_areas.append(det["bbox"])
        
        # 检查每个检测结果是否与货舱区域重叠
        for det in detections:
            cls_name = det["class_name"]
            
            # 检查是否是摄像头异常（不需要与货舱重叠）
            if cls_name in self.alarm_types["camera_alarm"]:
                alarms["camera_alarm"].append({
                    "object_class": cls_name,
                    "confidence": det["confidence"],
                    "location": det["bbox"]
                })
                continue
            
            # 检查其他类型的告警（需要与货舱重叠）
            for alarm_type, class_list in self.alarm_types.items():
                if cls_name in class_list:
                    # 检查是否与任何货舱区域重叠
                    for cargo_area in cargo_areas:
                        overlap = calculate_overlap(det["bbox"], cargo_area)
                        if overlap > 0:
                            alarms[alarm_type].append({
                                "object_class": cls_name,
                                "confidence": det["confidence"],
                                "location": det["bbox"],
                                "overlap": overlap
                            })
                            break
        
        return alarms 