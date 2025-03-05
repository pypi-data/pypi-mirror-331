"""
模型管理模块
"""

import os
import torch
from pathlib import Path

# 默认模型路径
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "segment_best228.pt")

def get_default_model_path():
    """获取默认模型路径"""
    return DEFAULT_MODEL_PATH

def is_cuda_available():
    """检查CUDA是否可用"""
    return torch.cuda.is_available() 