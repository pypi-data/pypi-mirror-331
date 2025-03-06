#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CCTV 智能检测系统 - 简单命令行工具
提供直接从命令行调用检测功能的简单接口
"""

import os
import sys
import json
import argparse
import uuid
from .cctv_detector import CCTVDetector

# 确保结果目录存在
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def detect_image(image_path, confidence=0.25, iou=0.45, model_path="models/segment_best228.pt"):
    """
    直接检测并返回结果
    
    参数:
        image_path: 图像文件路径
        confidence: 置信度阈值
        iou: IoU阈值
        model_path: 模型文件路径
    """
    try:
        # 初始化检测器
        detector = CCTVDetector(model_path=model_path, conf=confidence, iou=iou)
        
        # 执行检测
        result = detector.process_image(image_path=image_path)
        
        # 将结果转为漂亮的JSON格式输出
        return result
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

def main():
    """
    命令行入口函数
    """
    # 创建命令行解析器
    parser = argparse.ArgumentParser(description="CCTV 智能检测系统命令行工具")
    parser.add_argument("image_path", help="要检测的图像文件路径")
    parser.add_argument("--conf", "-c", type=float, default=0.25, help="置信度阈值 (默认: 0.25)")
    parser.add_argument("--iou", "-i", type=float, default=0.45, help="IoU阈值 (默认: 0.45)")
    parser.add_argument("--model", "-m", default="models/segment_best228.pt", help="模型文件路径 (默认: models/segment_best228.pt)")
    parser.add_argument("--output", "-o", help="结果保存的JSON文件名 (可选，保存在results目录下)")
    parser.add_argument("--summary", "-s", action="store_true", help="只显示结果摘要而不是完整JSON")
    args = parser.parse_args()
    
    # 检查图像文件是否存在
    if not os.path.exists(args.image_path):
        print(f"错误: 图像文件不存在: {args.image_path}")
        sys.exit(1)
    
    # 执行检测
    result = detect_image(args.image_path, args.conf, args.iou, args.model)
    
    # 生成输出文件名
    if args.output:
        output_filename = args.output
        # 如果用户提供了完整路径，只取文件名部分
        if os.path.dirname(output_filename):
            output_filename = os.path.basename(output_filename)
    else:
        # 自动生成输出文件名
        base_name = os.path.basename(args.image_path)
        name, _ = os.path.splitext(base_name)
        unique_id = uuid.uuid4().hex[:8]
        output_filename = f"{name}_result_{unique_id}.json"
    
    # 完整输出路径
    output_path = os.path.join(RESULTS_DIR, output_filename)
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    if args.summary:
        # 打印简洁的结果摘要
        print(f"结果已保存至: {output_path}")
        if result["success"]:
            detections = result["data"]["detections"]
            vis_path = result["data"]["visualization_path"]
            print(f"检测成功: 找到 {len(detections)} 个目标")
            print(f"可视化结果: {vis_path}")
        else:
            print(f"检测失败: {result['error']}")
    else:
        # 打印完整的JSON结果，与API输出一致
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 