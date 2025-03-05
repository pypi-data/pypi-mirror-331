"""
命令行工具模块

提供命令行接口，用于处理图像和启动Web应用
"""

import os
import sys
import argparse
import json
from typing import Optional, Dict, List, Any

from .core.detector import DetectionProcessor
from .models import get_default_model_path, is_cuda_available
from .web.app import run_webapp


def process_image(args):
    """处理单张图像"""
    # 检查文件是否存在
    if not os.path.exists(args.image):
        print(f"错误: 文件不存在: {args.image}")
        return 1
    
    # 确保输出目录存在
    if args.result_dir and not os.path.exists(args.result_dir):
        os.makedirs(args.result_dir)
    
    # 初始化处理器
    processor = DetectionProcessor(
        model_path=args.model,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
        output_dir=args.result_dir
    )
    
    # 处理图像
    result = processor.process_image(args.image)
    
    # 输出结果
    if args.output:
        # 保存到文件
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        # 打印到控制台
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return 0


def start_webapp(args):
    """启动Web应用"""
    run_webapp(
        model_path=args.model,
        output_dir=args.result_dir,
        port=args.port,
        address=args.address
    )
    return 0


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="CCTV 智能检测系统")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 图像处理子命令
    image_parser = subparsers.add_parser("image", help="处理单张图像")
    image_parser.add_argument("--image", "-i", required=True, help="输入图像路径")
    image_parser.add_argument("--model", "-m", default=get_default_model_path(), help="模型路径")
    image_parser.add_argument("--conf", "-c", type=float, default=0.25, help="置信度阈值")
    image_parser.add_argument("--iou", type=float, default=0.45, help="IoU阈值")
    image_parser.add_argument("--device", "-d", default="cuda" if is_cuda_available() else "cpu", help="运行设备 (cuda 或 cpu)")
    image_parser.add_argument("--output", "-o", help="输出JSON文件路径")
    image_parser.add_argument("--result-dir", "-r", default="results", help="结果保存目录")
    image_parser.set_defaults(func=process_image)
    
    # Web应用子命令
    web_parser = subparsers.add_parser("web", help="启动Web应用")
    web_parser.add_argument("--model", "-m", default=None, help="模型路径")
    web_parser.add_argument("--result-dir", "-r", default="results", help="结果保存目录")
    web_parser.add_argument("--port", "-p", type=int, default=8501, help="服务端口")
    web_parser.add_argument("--address", "-a", default="127.0.0.1", help="服务地址")
    web_parser.set_defaults(func=start_webapp)
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定子命令，显示帮助信息
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行对应的函数
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main()) 