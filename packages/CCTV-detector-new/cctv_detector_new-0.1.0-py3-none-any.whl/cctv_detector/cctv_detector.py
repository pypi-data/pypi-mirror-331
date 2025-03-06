#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CCTV 智能检测系统核心模块
提供图像检测和结果处理功能，可作为服务或库使用
"""

import os
import json
import uuid
import time
import numpy as np
import torch
from ultralytics import YOLO
import cv2
from typing import Dict, List, Union, Tuple, Optional, Any


class CCTVDetector:
    """
    CCTV 智能检测系统核心类
    用于加载模型、处理图像并返回检测结果
    """
    _instance = None  # 单例模式实例
    _initialized = False  # 初始化标志
    
    def __new__(cls, *args, **kwargs):
        """
        单例模式实现，确保只有一个模型实例被加载到内存中
        """
        if cls._instance is None:
            cls._instance = super(CCTVDetector, cls).__new__(cls)
        return cls._instance
        
    def __init__(self, model_path: str = None, conf: float = 0.25, 
                 iou: float = 0.45, device: str = None, output_dir: str = "results"):
        """
        初始化检测器
        
        参数:
            model_path: 模型路径，如果为None则使用之前加载的模型
            conf: 置信度阈值
            iou: IoU阈值
            device: 推理设备 ('cuda' 或 'cpu')
            output_dir: 结果保存目录
        """
        # 如果已经初始化过，且没有新的模型路径，直接返回
        if self._initialized and model_path is None:
            return
            
        self.conf = conf
        self.iou = iou
        self.output_dir = output_dir
        
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # 设备配置 - 处理'auto'选项
        if device == 'auto' or device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"使用设备: {self.device}")
        
        if self.device == 'cuda':
            torch.backends.cudnn.benchmark = True
        
        # 加载模型
        if model_path or not hasattr(self, 'model'):
            print(f"加载模型: {model_path}, 使用设备: {self.device}")
            self.model = YOLO(model_path)
            self.model.to(self.device)
        
        # 配置颜色和告警类型
        self.configure_settings()
        
        # 标记为已初始化
        self.__class__._initialized = True
    
    def configure_settings(self):
        """配置检测和告警设置"""
        # 告警类型配置
        self.alarm_types = {
            "person_intrusion": ["person", "人", "人员"],
            "vessel_approach": ["ship", "boat", "vessel", "船", "船只"],
            "machinery_intrusion": ["machinery", "machine", "机械"],
            "camera_alarm": ["camera_error", "error"]  # 摄像头异常检测
        }
        
        # 检测框颜色配置 (BGR格式)
        self.colors = {
            # 货舱覆盖状态颜色
            "covered": (0, 255, 0),      # 绿色 - 完全覆盖
            "partially": (0, 255, 255),  # 黄色 - 部分覆盖
            "uncovered": (0, 0, 255),    # 红色 - 未覆盖
            
            # 其他所有检测类型统一使用蓝色
            "default": (255, 0, 0)       # 蓝色
        }
    
    def process_image(self, image_path: str = None, image: np.ndarray = None) -> Dict[str, Any]:
        """
        处理图像并返回JSON格式结果
        
        参数:
            image_path: 图像文件路径，与image参数二选一
            image: 图像数据，与image_path参数二选一
            
        返回:
            包含检测结果的字典
        """
        start_time = time.time()
        
        try:
            # 检查输入参数
            if image_path is None and image is None:
                return self._error_response("必须提供image_path或image参数")
            
            # 如果提供了图像路径，检查文件是否存在
            if image_path is not None:
                if not os.path.exists(image_path):
                    return self._error_response(f"图像文件不存在: {image_path}")
                
                # 从路径读取图像
                image_for_vis = cv2.imread(image_path)
                if image_for_vis is None:
                    return self._error_response(f"无法读取图像: {image_path}")
                
                # 执行检测 (使用路径方式)
                results = self.model(image_path, conf=self.conf, iou=self.iou, verbose=False)
            else:
                # 使用传入的图像数据
                image_for_vis = image.copy()
                # 执行检测 (使用图像数据方式)
                results = self.model(image, conf=self.conf, iou=self.iou, verbose=False)
            
            result = results[0]
            
            # 处理检测结果
            detections, alarms = self._process_detections(result)
            
            # 可视化结果并获取保存路径
            vis_path = self._visualize_results(image_for_vis, result, 
                                            image_path if image_path else None, 
                                            alarms)
            
            # 准备输出
            output = {
                "success": True,
                "data": {
                    "image_path": image_path if image_path else "direct_input",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "processing_time": round(time.time() - start_time, 3),
                    "detections": detections,
                    "alarms": alarms,
                    "visualization_path": vis_path
                },
                "error": None
            }
            
            return output
            
        except Exception as e:
            return self._error_response(str(e))
    
    def _process_detections(self, result) -> Tuple[List[Dict], Dict]:
        """处理检测结果，生成检测列表和告警信息"""
        detections = []
        alarms = {}
        cargo_areas = []  # 存储货舱区域
        
        # 如果没有检测结果，直接返回
        if result.boxes is None or len(result.boxes) == 0:
            return detections, alarms
        
        # 初始化告警类别
        for alarm_type in self.alarm_types.keys():
            alarms[alarm_type] = []
        
        # 第一次遍历，收集货舱区域
        for box in result.boxes:
            cls_id = int(box.cls.item())
            cls_name = result.names[cls_id].lower()
            if cls_name in ["covered", "partially", "partially_covered", "uncovered"]:
                xyxy = box.xyxy.cpu().numpy()[0].astype(int)
                cargo_areas.append(xyxy)
        
        # 处理每个检测框
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls.item())
            cls_name = result.names[cls_id]
            # 统一将error改为camera_error
            if cls_name.lower() == "error":
                cls_name = "camera_error"
            confidence = float(box.conf.item())
            xyxy = box.xyxy.cpu().numpy()[0].astype(int)
            
            # 创建检测结果
            detection = {
                "id": i,
                "class_name": cls_name,
                "confidence": round(confidence, 3),
                "bbox": {
                    "x1": int(xyxy[0]),
                    "y1": int(xyxy[1]),
                    "x2": int(xyxy[2]),
                    "y2": int(xyxy[3])
                }
            }
            detections.append(detection)
            
            # 检查是否需要生成告警
            for alarm_type, keywords in self.alarm_types.items():
                if any(keyword == cls_name.lower() for keyword in keywords):
                    # 对于入侵类告警（人员、船只、机械），检查是否与货舱区域重叠
                    if alarm_type in ["person_intrusion", "vessel_approach", "machinery_intrusion"]:
                        if not cargo_areas or not self._check_overlap_with_cargo(xyxy, cargo_areas):
                            continue
                    
                    alarm = {
                        "object_class": cls_name,
                        "confidence": round(confidence, 3),
                        "location": detection["bbox"]
                    }
                    alarms[alarm_type].append(alarm)
        
        # 移除空的告警类别
        alarms = {k: v for k, v in alarms.items() if v}
        
        return detections, alarms
    
    def _check_overlap_with_cargo(self, obj_box, cargo_areas) -> bool:
        """检查目标是否与任何货舱区域重叠"""
        def calculate_overlap(box1, box2):
            # 计算两个框的重叠区域
            x1 = max(box1[0], box2[0])
            y1 = max(box1[1], box2[1])
            x2 = min(box1[2], box2[2])
            y2 = min(box1[3], box2[3])
            
            if x1 < x2 and y1 < y2:
                return True
            return False
        
        # 检查与任意货舱区域的重叠
        for cargo_box in cargo_areas:
            if calculate_overlap(obj_box, cargo_box):
                return True
        return False
    
    def _visualize_results(self, image, result, image_path, alarms) -> str:
        """
        可视化检测结果并保存到文件
        
        返回:
            output_path: 保存的可视化图像路径
        """
        try:
            vis_image = image.copy()
            h, w = image.shape[:2]
            
            # 处理掩码和检测框
            if result.masks is not None and result.boxes is not None:
                masks = result.masks.data.cpu().numpy()
                for i, (mask, box) in enumerate(zip(masks, result.boxes)):
                    # 获取基本信息
                    cls_id = int(box.cls.item())
                    cls_name = result.names[cls_id].lower()
                    confidence = float(box.conf.item())
                    xyxy = box.xyxy.cpu().numpy()[0].astype(int)
                    x1, y1, x2, y2 = xyxy
                    
                    # 根据覆盖状态确定颜色 - 使用精确匹配
                    if cls_name == "covered":
                        color = self.colors["covered"]
                    elif cls_name == "partially_covered" or cls_name == "partially":
                        color = self.colors["partially"]
                    elif cls_name == "uncovered":
                        color = self.colors["uncovered"]
                    else:
                        color = self.colors["default"]
                    
                    # 处理掩码
                    if mask.shape[:2] != (h, w):
                        # 调整掩码尺寸以匹配原图
                        mask = cv2.resize(mask, (w, h))
                    
                    # 创建彩色掩码
                    colored_mask = np.zeros((h, w, 3), dtype=np.uint8)
                    colored_mask[mask > 0.5] = color
                    
                    # 将掩码叠加到图像上（半透明效果）
                    alpha = 0.15  
                    vis_image = cv2.addWeighted(vis_image, 1, colored_mask, alpha, 0)
                    
                    # 确定是否是告警对象
                    is_alarm = False
                    if alarms:
                        for alerts in alarms.values():
                            for alert in alerts:
                                if (cls_name == alert["object_class"].lower() and
                                    x1 == alert["location"]["x1"] and
                                    y1 == alert["location"]["y1"]):
                                    is_alarm = True
                                    break
                    
                    # 绘制检测框
                    thickness = 3 if is_alarm else 2
                    cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, thickness)
                    
                    # 绘制标签
                    label = f"{cls_name} {confidence:.2f}"
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    
                    # 确定标签位置（优先上方，如果上方放不下就放在下方）
                    img_h = vis_image.shape[0]
                    if y1 - text_size[1] - 5 < 0:  # 上方放不下
                        label_y = min(y2 + text_size[1] + 5, img_h - 5)  # 放在下方，但不超出图像
                    else:  # 放在上方
                        label_y = y1 - 5
                    
                    # 绘制标签背景和文本
                    cv2.rectangle(vis_image,
                                (x1, label_y - text_size[1] - 5),
                                (x1 + text_size[0], label_y),
                                (0, 0, 0), -1)
                    cv2.putText(vis_image, label, (x1, label_y - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # 保存结果
            if self.output_dir:
                # 确保输出目录存在
                os.makedirs(self.output_dir, exist_ok=True)
                
                # 生成输出文件名
                if image_path:
                    base_name = os.path.basename(image_path)
                    name, ext = os.path.splitext(base_name)
                else:
                    name = "image"
                    ext = ".jpg"
                
                unique_id = uuid.uuid4().hex[:8]
                output_path = os.path.join(self.output_dir, f"{name}_result_{unique_id}{ext}")
                cv2.imwrite(output_path, vis_image)
                
                # 返回相对路径，方便前端使用
                rel_path = os.path.relpath(output_path)
                return rel_path
            
            # 如果没有输出目录，直接返回None
            return None
            
        except Exception as e:
            print(f"可视化过程出错: {str(e)}")
            return None
    
    def _error_response(self, error_message: str) -> Dict:
        """生成错误响应"""
        return {
            "success": False,
            "data": None,
            "error": error_message
        } 