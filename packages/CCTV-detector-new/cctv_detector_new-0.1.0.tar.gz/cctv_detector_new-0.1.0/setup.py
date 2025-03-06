import setuptools
import os

# 读取README文件
with open(os.path.join("cctv_detector", "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

# 读取requirements.txt文件
with open(os.path.join("cctv_detector", "requirements.txt"), "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="CCTV_detector_new",
    version="0.1.0",
    author="CCTV Development Team",
    author_email="info@cctv-detector.com",
    description="CCTV Intelligent Detection System based on YOLOv8",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cctv-detector/CCTV_detector_new",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "cctv-detect=cctv_detector.detect:main",
            "cctv-server=cctv_detector.cctv_server:main",
        ],
    },
) 