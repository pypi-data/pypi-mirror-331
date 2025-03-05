#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web应用示例

展示如何使用cctv_detector包启动Web应用
"""

import os
import sys
from cctv_detector.web.app import run_webapp

def main():
    """主函数"""
    # 创建结果目录
    output_dir = "webapp_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 启动Web应用
    print("启动Web应用...")
    print("访问 http://127.0.0.1:8501 查看界面")
    
    # 可以自定义端口和地址
    run_webapp(
        model_path=None,  # 使用默认模型
        output_dir=output_dir,
        port=8501,
        address="127.0.0.1"  # 使用0.0.0.0允许外部访问
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 