#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本 - 确保UTF-8编码
"""
import os
import sys
import subprocess

# 设置UTF-8环境
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "zh_CN.UTF-8"

# 添加项目路径
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

# 启动Streamlit
cmd = [
    sys.executable, "-m", "streamlit", "run", "app.py",
    "--server.headless=true",
    "--server.fileWatcherType=none"
]

print("启动法律助手...")
print(f"工作目录: {project_dir}")
print(f"Python: {sys.executable}")

subprocess.run(cmd)