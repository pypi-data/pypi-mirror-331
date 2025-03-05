# CCTV 智能检测系统

基于 YOLOv8 的对象检测与警报系统，专为货舱监控设计。

## 功能特点

- 对象检测：支持人员、船只、机械等目标检测
- 货舱覆盖状态检测：已覆盖/部分覆盖/未覆盖
- 智能警报：自动检测并报警可疑情况
- 摄像头异常检测
- Web界面：友好的可视化界面
- JSON输出：标准化的检测结果输出

## 安装方法

```bash
pip install -e .
```

## 使用方法

### 1. 作为Python包使用

```python
from cctv_detector import DetectionProcessor

# 创建检测器
detector = DetectionProcessor(
    model_path="models/segment_best228.pt",
    conf=0.25,
    iou=0.45,
    device="cuda"
)

# 处理图像
result = detector.process_image("test.jpg")
print(result)
```

### 2. 运行Web应用

```python
from cctv_detector import run_webapp

# 运行Web应用
run_webapp(model_path="models/segment_best228.pt")
```

## 目录结构

```
cctv_detector/
├── src/
│   └── cctv_detector/
│       ├── __init__.py
│       ├── detector.py      # 检测器核心模块
│       ├── visualizer.py    # 可视化模块
│       └── webapp.py        # Web应用模块
├── examples/
│   ├── run_detection.py     # 检测示例
│   └── run_webapp.py        # Web应用示例
├── models/
│   └── segment_best228.pt   # 预训练模型
└── setup.py                 # 包配置文件
```

## 依赖要求

- Python >= 3.7
- PyTorch >= 1.9.0
- Ultralytics >= 8.0.0
- OpenCV >= 4.5.0
- Streamlit == 1.24.0
- 其他依赖见 setup.py

## 注意事项

1. 首次运行前请确保已安装所有依赖
2. 使用GPU加速需要安装CUDA支持的PyTorch版本
3. 模型文件需要放在正确的位置

## 许可证

MIT License 