"""
CCTV 智能检测系统 (CCTV Intelligent Detection System)
"""

__version__ = "0.1.0"

from .cctv_detector import CCTVDetector
from .cctv_server import app as server_app

# 提供方便的导入接口
__all__ = ['CCTVDetector', 'server_app'] 