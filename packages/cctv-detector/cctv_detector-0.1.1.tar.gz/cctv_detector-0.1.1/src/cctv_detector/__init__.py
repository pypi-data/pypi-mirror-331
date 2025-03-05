"""
CCTV智能检测系统
基于YOLOv8的对象检测与警报系统
"""

from .detector import DetectionProcessor
from .visualizer import visualize_detections
from .webapp import run_webapp

__version__ = "0.1.0"
__all__ = ["DetectionProcessor", "visualize_detections", "run_webapp"] 