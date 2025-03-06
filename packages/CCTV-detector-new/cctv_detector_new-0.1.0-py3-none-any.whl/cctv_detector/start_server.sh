#!/bin/bash
# CCTV 智能检测系统 - 服务启动脚本

# 设置默认参数
PORT=8000
HOST="0.0.0.0"
DEVICE="auto"  # auto, cpu, 或 cuda
MODEL_PATH="models/segment_best228.pt"
CONFIDENCE=0.25
IOU=0.45

# 处理命令行参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -p|--port)
            PORT="$2"
            shift
            shift
            ;;
        -h|--host)
            HOST="$2"
            shift
            shift
            ;;
        -d|--device)
            DEVICE="$2"
            shift
            shift
            ;;
        -m|--model)
            MODEL_PATH="$2"
            shift
            shift
            ;;
        -c|--confidence)
            CONFIDENCE="$2"
            shift
            shift
            ;;
        -i|--iou)
            IOU="$2"
            shift
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 确保目录存在
mkdir -p models
mkdir -p results
mkdir -p temp

# 设置环境变量
export MODEL_PATH=$MODEL_PATH
export DEVICE=$DEVICE
export CONFIDENCE_THRESHOLD=$CONFIDENCE
export IOU_THRESHOLD=$IOU

echo "==============================================="
echo "  CCTV 智能检测系统 - 服务器 "
echo "==============================================="
echo "主机: $HOST"
echo "端口: $PORT"
echo "设备: $DEVICE"
echo "模型路径: $MODEL_PATH"
echo "置信度阈值: $CONFIDENCE"
echo "IoU阈值: $IOU"
echo "==============================================="
echo "启动中..."

# 启动服务器
python -m uvicorn cctv_server:app --host $HOST --port $PORT 