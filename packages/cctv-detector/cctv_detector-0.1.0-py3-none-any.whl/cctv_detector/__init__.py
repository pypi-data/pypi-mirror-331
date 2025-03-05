"""
CCTV Detector - 智能货舱监控检测库

一个基于YOLOv8的智能监控系统，用于检测货舱覆盖状态和各种异常情况。
"""

__version__ = "0.1.0"

from .core.detector import DetectionProcessor
from .core.result import DetectionResult

# 方便导入的别名
Detector = DetectionProcessor

# 版本信息
__all__ = ['DetectionProcessor', 'DetectionResult', 'Detector'] 