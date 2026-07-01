@echo off
title AI小说创作系统启动器

echo ===================================================
echo     AI 小说创作系统 - 正在进行环境健康检查...
echo ===================================================

echo [检查] 正在验证核心组件 (Gradio) 是否就绪...
python -c "import gradio" >nul 2>&1

if errorlevel 1 (
    echo [提示] 检测到本地环境缺少必要组件，正在为您全自动配置...
    echo [执行] 正在连接国内清华大学高速镜像源，请稍候...
    python -m pip install gradio google-generativeai -i http://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
)

echo ===================================================
echo     正在拉起 AI 小说创作系统后台服务，请稍候...
echo ===================================================

start /b python main.py

timeout /t 3 /nobreak >nul

if exist 启动控制台.html (
    start 启动控制台.html
) else (
    start http://127.0.0.1:7860
)

exit
