"""
检测结果模块

定义检测结果的数据结构和处理方法
"""

from typing import Dict, List, Optional, Any
import json


class DetectionResult:
    """
    检测结果类
    
    封装检测结果数据并提供处理方法
    """
    
    def __init__(
        self,
        success: bool = True,
        image_path: Optional[str] = None,
        timestamp: Optional[str] = None,
        processing_time: Optional[float] = None,
        detections: Optional[List[Dict]] = None,
        alarms: Optional[Dict[str, List]] = None,
        visualization_path: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        初始化检测结果
        
        参数:
            success: 处理是否成功
            image_path: 图像路径
            timestamp: 处理时间戳
            processing_time: 处理耗时（秒）
            detections: 检测结果列表
            alarms: 告警信息字典
            visualization_path: 可视化结果图像路径
            error: 错误信息（如果处理失败）
        """
        self.success = success
        self.image_path = image_path
        self.timestamp = timestamp
        self.processing_time = processing_time
        self.detections = detections or []
        self.alarms = alarms or {}
        self.visualization_path = visualization_path
        self.error = error
    
    def to_dict(self) -> Dict:
        """
        将结果转换为字典格式
        
        返回:
            包含所有结果数据的字典
        """
        if not self.success:
            return {
                "success": False,
                "error": self.error
            }
        
        return {
            "success": True,
            "data": {
                "image_path": self.image_path,
                "timestamp": self.timestamp,
                "processing_time": self.processing_time,
                "detections": self.detections,
                "alarms": self.alarms,
                "visualization_path": self.visualization_path
            },
            "error": None
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        将结果转换为JSON字符串
        
        参数:
            indent: JSON缩进空格数
            
        返回:
            格式化的JSON字符串
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_json(self, output_path: str, indent: int = 2) -> bool:
        """
        将结果保存为JSON文件
        
        参数:
            output_path: 输出文件路径
            indent: JSON缩进空格数
            
        返回:
            保存是否成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存JSON失败: {str(e)}")
            return False
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DetectionResult':
        """
        从字典创建结果对象
        
        参数:
            data: 包含结果数据的字典
            
        返回:
            DetectionResult实例
        """
        if not data.get("success", False):
            return cls(success=False, error=data.get("error"))
        
        result_data = data.get("data", {})
        return cls(
            success=True,
            image_path=result_data.get("image_path"),
            timestamp=result_data.get("timestamp"),
            processing_time=result_data.get("processing_time"),
            detections=result_data.get("detections", []),
            alarms=result_data.get("alarms", {}),
            visualization_path=result_data.get("visualization_path")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DetectionResult':
        """
        从JSON字符串创建结果对象
        
        参数:
            json_str: JSON格式的结果字符串
            
        返回:
            DetectionResult实例
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except Exception as e:
            return cls(success=False, error=f"JSON解析错误: {str(e)}")
    
    @classmethod
    def load_json(cls, json_path: str) -> 'DetectionResult':
        """
        从JSON文件加载结果对象
        
        参数:
            json_path: JSON文件路径
            
        返回:
            DetectionResult实例
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            return cls(success=False, error=f"加载JSON文件失败: {str(e)}")
    
    def has_alarms(self) -> bool:
        """
        检查是否存在任何告警
        
        返回:
            是否存在告警
        """
        if not self.alarms:
            return False
        
        return any(len(alarms) > 0 for alarms in self.alarms.values())
    
    def get_alarm_count(self) -> int:
        """
        获取告警总数
        
        返回:
            告警总数
        """
        if not self.alarms:
            return 0
        
        return sum(len(alarms) for alarms in self.alarms.values())
    
    def get_detection_count(self) -> int:
        """
        获取检测对象总数
        
        返回:
            检测对象总数
        """
        return len(self.detections) 