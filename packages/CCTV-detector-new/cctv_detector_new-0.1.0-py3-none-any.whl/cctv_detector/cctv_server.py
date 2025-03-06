#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CCTV 智能检测系统 - API服务器
提供RESTful API接口，用于接收图像检测请求并返回结果
"""

import os
import sys
import json
import time
import base64
import uuid
import uvicorn
import numpy as np
import cv2
import urllib.parse
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
import logging
from io import BytesIO
from .cctv_detector import CCTVDetector


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cctv_server")

# 创建FastAPI应用
app = FastAPI(
    title="CCTV 智能检测系统 API",
    description="提供图像检测和分析服务的RESTful API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保results目录存在
os.makedirs("results", exist_ok=True)

# 创建静态文件服务，用于访问results目录中的结果图像
app.mount("/results", StaticFiles(directory="results"), name="results")

# 模型配置和状态
MODEL_PATH = os.environ.get("MODEL_PATH", "models/segment_best228.pt")
DEFAULT_CONF = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.25"))
DEFAULT_IOU = float(os.environ.get("IOU_THRESHOLD", "0.45"))
DEVICE = os.environ.get("DEVICE", None)  # None将自动选择可用设备

# 检测器实例（全局单例）
detector = None

# 请求模型
class DetectionRequest(BaseModel):
    confidence: Optional[float] = Field(DEFAULT_CONF, description="置信度阈值")
    iou: Optional[float] = Field(DEFAULT_IOU, description="IoU阈值")

class PathRequest(BaseModel):
    path: str = Field(..., description="图像文件路径")
    confidence: Optional[float] = Field(DEFAULT_CONF, description="置信度阈值")
    iou: Optional[float] = Field(DEFAULT_IOU, description="IoU阈值")


@app.on_event("startup")
async def startup_event():
    """应用启动时加载模型"""
    global detector
    logger.info("正在初始化检测器...")
    try:
        detector = CCTVDetector(
            model_path=MODEL_PATH,
            conf=DEFAULT_CONF,
            iou=DEFAULT_IOU,
            device=DEVICE
        )
        logger.info(f"检测器初始化成功，使用设备: {detector.device}")
    except Exception as e:
        logger.error(f"检测器初始化失败: {str(e)}")
        sys.exit(1)


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "CCTV 智能检测系统 API",
        "status": "运行中",
        "version": "1.0.0"
    }


@app.get("/status")
async def get_status():
    """获取服务状态"""
    if detector is None:
        return {"status": "未初始化"}
    
    return {
        "status": "就绪",
        "device": detector.device,
        "model_path": MODEL_PATH,
        "default_conf": DEFAULT_CONF,
        "default_iou": DEFAULT_IOU
    }


@app.post("/detect")
async def detect_file(
    file: UploadFile = File(...),
    confidence: Optional[float] = Form(DEFAULT_CONF),
    iou: Optional[float] = Form(DEFAULT_IOU)
):
    """
    从上传的文件进行检测
    
    参数:
    - file: 上传的图像文件
    - confidence: 置信度阈值
    - iou: IoU阈值
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")
    
    try:
        # 更新检测器配置
        detector.conf = confidence
        detector.iou = iou
        
        # 保存上传的文件到临时目录
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        # 写入文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 执行检测
        result = detector.process_image(image_path=file_path)
        
        # 修改visualization_path为完整URL
        if result["success"] and "visualization_path" in result["data"]:
            # 获取请求的主机信息
            vis_path = result["data"]["visualization_path"]
            # 创建绝对URL路径 (使用服务器URL)
            # 获取文件名并进行URL编码
            file_name = os.path.basename(vis_path)
            encoded_file_name = urllib.parse.quote(file_name)
            # 由于FastAPI已经挂载了/results目录，我们直接使用该路径
            result["data"]["visualization_url"] = f"/results/{encoded_file_name}"
            # 保留原始路径
            result["data"]["visualization_path"] = vis_path
            
        # 清理临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        return result
        
    except Exception as e:
        logger.error(f"处理检测请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/detect/path")
async def detect_path(request: PathRequest):
    """
    从本地文件路径进行检测
    
    参数:
    - path: 服务器上的图像文件路径
    - confidence: 置信度阈值
    - iou: IoU阈值
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")
    
    if not os.path.exists(request.path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {request.path}")
    
    try:
        # 更新检测器配置
        detector.conf = request.confidence
        detector.iou = request.iou
        
        # 执行检测
        result = detector.process_image(image_path=request.path)
        
        # 修改visualization_path为完整URL
        if result["success"] and "visualization_path" in result["data"]:
            vis_path = result["data"]["visualization_path"]
            # 获取文件名并进行URL编码
            file_name = os.path.basename(vis_path)
            encoded_file_name = urllib.parse.quote(file_name)
            # 创建绝对URL路径
            result["data"]["visualization_url"] = f"/results/{encoded_file_name}"
            # 保留原始路径
            result["data"]["visualization_path"] = vis_path
        
        return result
        
    except Exception as e:
        logger.error(f"处理检测请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/results/{filename}")
async def get_result_file(filename: str):
    """
    获取检测结果图像
    """
    # 解码URL编码的文件名
    decoded_filename = urllib.parse.unquote(filename)
    file_path = os.path.join("results", decoded_filename)
    
    if not os.path.exists(file_path):
        # 如果解码后的文件不存在，尝试使用原始文件名
        file_path = os.path.join("results", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)


def main():
    """启动服务器"""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # 确保结果和临时目录存在
    os.makedirs("results", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    logger.info(f"启动CCTV检测服务器于 {host}:{port}")
    # 修改为使用当前模块路径
    uvicorn.run("cctv_detector.cctv_server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main() 