@echo off
REM CCTV 智能检测系统 - 服务启动脚本 (Windows版)

REM 设置默认参数
set PORT=8000
set HOST=0.0.0.0
set DEVICE=auto
set MODEL_PATH=models\segment_best228.pt
set CONFIDENCE=0.25
set IOU=0.45

REM 处理命令行参数
:GETOPTS
if "%~1"=="" goto :ENDGETOPTS
if "%~1"=="-p" set "PORT=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="--port" set "PORT=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="-h" set "HOST=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="--host" set "HOST=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="-d" set "DEVICE=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="--device" set "DEVICE=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="-m" set "MODEL_PATH=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="--model" set "MODEL_PATH=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="-c" set "CONFIDENCE=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="--confidence" set "CONFIDENCE=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="-i" set "IOU=%~2" & shift & shift & goto :GETOPTS
if "%~1"=="--iou" set "IOU=%~2" & shift & shift & goto :GETOPTS
shift
goto :GETOPTS
:ENDGETOPTS

REM 确保目录存在
if not exist models mkdir models
if not exist results mkdir results
if not exist temp mkdir temp

REM 设置环境变量
set "MODEL_PATH=%MODEL_PATH%"
set "DEVICE=%DEVICE%"
set "CONFIDENCE_THRESHOLD=%CONFIDENCE%"
set "IOU_THRESHOLD=%IOU%"

echo ===============================================
echo   CCTV 智能检测系统 - 服务器 
echo ===============================================
echo 主机: %HOST%
echo 端口: %PORT%
echo 设备: %DEVICE%
echo 模型路径: %MODEL_PATH%
echo 置信度阈值: %CONFIDENCE%
echo IoU阈值: %IOU%
echo ===============================================
echo 启动中...

REM 启动服务器
python -m uvicorn cctv_server:app --host %HOST% --port %PORT%

pause 