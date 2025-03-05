#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用示例：运行Web应用
"""

from cctv_detector import run_webapp

def main():
    # 运行Web应用
    run_webapp(model_path="models/segment_best228.pt")

if __name__ == "__main__":
    main() 