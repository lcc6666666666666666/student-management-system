@echo off
chcp 65001 >nul
echo 正在启动教学管理系统后端服务...
:: 如果你使用了 Python 虚拟环境，可以取消下面这行的注释，并调整为你实际的虚拟环境路径
:: call venv\Scripts\activate
python run.py
pause