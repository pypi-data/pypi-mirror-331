# CCTV_detector_new

基于YOLOv8的CCTV智能检测系统，用于货舱监控场景下的目标检测和智能告警。系统可识别不同覆盖状态（完全覆盖、部分覆盖、未覆盖）以及机械设备等异常情况。

## 安装

```bash
pip install CCTV_detector_new
```

## 简单使用

```python
from cctv_detector import CCTVDetector

# 初始化检测器
detector = CCTVDetector(model_path="models/segment_best228.pt")

# 执行检测
result = detector.process_image(image_path="example.jpg")

# 处理结果
if result["success"]:
    print(f"检测到 {len(result['data']['detections'])} 个目标")
    print(f"可视化结果保存于：{result['data']['visualization_path']}")
```

## 命令行工具

安装后，可以使用命令行工具进行检测：

```bash
cctv-detect image.jpg --conf 0.3 --iou 0.45
```

## 启动API服务器

```bash
cctv-server
```

详细文档请参见[完整说明文档](https://github.com/cctv-detector/CCTV_detector_new)。 