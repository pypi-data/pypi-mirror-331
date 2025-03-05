# CCTV Detector

CCTV Detector是一个基于YOLOv8的智能货舱监控检测库，用于检测货舱覆盖状态和各种异常情况，如人员入侵、船只接近、机械操作等。

## 功能特点

- 🎯 **多目标检测**：识别货舱覆盖状态（已覆盖/部分覆盖/未覆盖）
- 🚨 **智能告警**：检测人员入侵、船只接近、机械入侵等与货舱区域重叠的异常情况
- 📊 **结果可视化**：使用不同颜色标注不同类型的检测结果
- 💾 **JSON输出**：提供结构化的检测结果和告警信息
- 🌐 **Web界面**：提供友好的网页操作界面
- 📦 **可导入包**：可作为Python包导入到其他项目中

## 安装方法

### 从PyPI安装

```bash
pip install cctv-detector
```

### 从源码安装

```bash
git clone https://github.com/example/cctv-detector.git
cd cctv-detector
pip install -e .
```

## 使用方法

### 作为Python包导入

```python
from cctv_detector import Detector, DetectionResult

# 初始化检测器
detector = Detector(
    model_path="path/to/model.pt",  # 可选，默认使用内置模型
    conf=0.25,                      # 置信度阈值
    iou=0.45,                       # IoU阈值
    device="cuda",                  # 设备类型 (cuda 或 cpu)
    output_dir="results"            # 结果输出目录
)

# 处理图像
result = detector.process_image("path/to/image.jpg")

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
else:
    print(f"处理失败: {result['error']}")
```

### 使用命令行工具

处理单张图像：

```bash
cctv-detector image --image path/to/image.jpg --output result.json
```

启动Web应用：

```bash
cctv-detector web --port 8501 --address 0.0.0.0
```

### 命令行选项

#### 图像处理模式

```
cctv-detector image [选项]

选项:
  --image, -i      输入图像路径（必需）
  --model, -m      模型路径（默认使用内置模型）
  --conf, -c       置信度阈值（默认: 0.25）
  --iou            IoU阈值（默认: 0.45）
  --device, -d     运行设备（cuda 或 cpu）
  --output, -o     输出JSON文件路径
  --result-dir, -r 结果保存目录（默认: results）
```

#### Web应用模式

```
cctv-detector web [选项]

选项:
  --model, -m      模型路径（默认使用内置模型）
  --result-dir, -r 结果保存目录（默认: results）
  --port, -p       服务端口（默认: 8501）
  --address, -a    服务地址（默认: 127.0.0.1）
```

## API文档

### Detector 类

```python
class Detector:
    def __init__(
        self, 
        model_path=None, 
        conf=0.25, 
        iou=0.45, 
        device=None, 
        output_dir="results"
    ):
        """
        初始化检测器
        
        参数:
            model_path: 模型路径，如果为None则使用默认模型
            conf: 置信度阈值
            iou: IOU阈值
            device: 推理设备 ('cuda' 或 'cpu')
            output_dir: 结果输出目录
        """
        
    def process_image(self, image_path):
        """
        处理单张图像并返回检测结果
        
        参数:
            image_path: 图像文件路径
            
        返回:
            包含检测结果和告警信息的字典
        """
```

### DetectionResult 类

```python
class DetectionResult:
    def __init__(
        self,
        success=True,
        image_path=None,
        timestamp=None,
        processing_time=None,
        detections=None,
        alarms=None,
        visualization_path=None,
        error=None
    ):
        """
        初始化检测结果
        """
        
    def to_dict(self):
        """将结果转换为字典格式"""
        
    def to_json(self, indent=2):
        """将结果转换为JSON字符串"""
        
    def save_json(self, output_path, indent=2):
        """将结果保存为JSON文件"""
        
    def has_alarms(self):
        """检查是否存在任何告警"""
        
    def get_alarm_count(self):
        """获取告警总数"""
        
    def get_detection_count(self):
        """获取检测对象总数"""
```

## 系统要求

- Python 3.8 或更高版本
- 建议使用CUDA支持的GPU（用于加速推理）
- 依赖包参见 `requirements.txt`

## 许可证

MIT License 