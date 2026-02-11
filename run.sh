#!/bin/bash
# ---------------------------------------------------------
# 宝塔面板定时任务运行脚本
# 请将此文件上传到服务器项目目录中
# ---------------------------------------------------------

# 1. 进入项目目录
# 注意：请将下面的路径修改为你实际上传的目录路径
# 根据你的反馈，你的实际目录是 /www/wwwroot/myzf
cd /www/wwwroot/myzf

# 2. 确保依赖已安装（解决 ModuleNotFoundError）
# 自动安装依赖到当前用户环境，避免环境不一致问题
pip3 install -r requirements.txt --user > /dev/null 2>&1


# 2. 设置环境变量
export URL="http://syjw.zjhu.edu.cn/jwglxt/"
export USERNAME=""
export PASSWORD=""
export TOKEN=""
# 强制推送设置：True=每次都推送，False=仅成绩变化推送
export FORCE_PUSH_MESSAGE="False"

# 3. 运行Python脚本
# 如果你在宝塔使用了"Python项目管理器"创建了虚拟环境，请使用虚拟环境的python绝对路径
# 例如：/www/wwwroot/myzf-main/my_env/bin/python3 main.py
# 如果直接使用系统Python，直接用 python3 即可
python3 main.py
