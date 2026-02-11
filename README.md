# 正方教务管理系统成绩推送 (Web 版)

<img src="https://github.com/liuxiansenlc/myzf/blob/main/img/7.jpg?raw=true" style="zoom:60%;" />

## 简介

**使用本项目前：**

早晨睡醒看一遍教务系统、上厕所看一遍教务系统、刷牙看一遍教务系统、洗脸看一遍教务系统、吃早餐看一遍教务系统、吃午饭看一遍教务系统、睡午觉前看一遍教务系统、午觉醒来看一遍教务系统、出门前看一遍教务系统、吃晚饭看一遍教务系统、洗澡看一遍教务系统、睡觉之前看一遍教务系统

**使用本项目后：**
取之于源，开之于源。
本系统基于NianBroken的项目基础，提供了一个 **Web 可视化界面**，支持**多用户**使用，且稳定性更强，成功推送率99%。造福全部同校同学，校园运营者强烈推荐。用户只需配置一次教务系统账号，系统便会在后台**自动定时检测**成绩更新，并通过微信及时推送通知。

## 核心功能

1.  **Web 可视化配置**：通过网页界面轻松录入账号、密码和推送 Token，无需修改代码。
2.  **多用户支持**：支持多人同时使用，数据相互隔离，互不干扰。
3.  **自定义推送频率**：用户可自主选择检测频率（如每 30 分钟、每 60 分钟等）。
4.  **智能推送策略**：
    *   支持“仅成绩变动时推送”或“强制每次检测都推送”。
    *   显示成绩提交时间、提交人姓名。
    *   成绩按时间降序排列。
    *   自动计算 GPA 和百分制 GPA。
5.  **后台自动运行**：基于 Python 调度器或宝塔计划任务，全自动后台运行。
6.  **数据持久化**：用户信息和运行状态存储于 MySQL 数据库，安全可靠。

## 测试环境

正方教务管理系统 版本 V8.0、V9.0

如果你的教务系统页面与下图所示的页面**完全一致**或**几乎一致**，则代表你可以使用本项目。

<img src="https://raw.githubusercontent.com/NianBroken/ZFCheckScores/main/img/9.png" style="zoom:60%;" />

## 宝塔面板部署教程 (推荐)

如果您使用的是宝塔面板，可以按照以下步骤快速部署：

### 1. 准备工作

*   进入宝塔面板 -> **软件商店**，安装 **Python项目管理器** (或直接使用服务器自带Python)。
*   安装 **MySQL** (推荐 5.7+)。
*   在宝塔 **数据库** 菜单中，添加一个新数据库（例如 `zhengfangjw`），记下用户名和密码。

### 2. 上传代码

*   进入 **文件** 菜单，将本项目代码上传到服务器目录（例如 `/www/wwwroot/myzf`）。
*   进入目录，找到 `init_db.py`，双击编辑修改数据库配置信息：

    ```python
    DB_CONFIG = {
        'host': 'localhost',
        'user': '您的数据库用户名',
        'password': '您的数据库密码',
        'database': 'zhengfangjw',
        'charset': 'utf8mb4'
    }
    ```

### 3. 安装依赖与初始化数据库

*   打开宝塔 **终端**，进入项目目录并执行命令：

    ```bash
    # 进入项目目录 (请根据实际路径修改)
    cd /www/wwwroot/myzf

    # 安装依赖
    pip install -r requirements.txt

    # 初始化数据库 (成功后会显示"数据库表初始化/更新成功")
    python init_db.py
    ```
    *(若提示 pip 命令不存在，请尝试使用 pip3 或安装 python-pip)*

### 4.在”python项目管理器“中创建一个项目，项目名称为 `myzf`，项目解释器为 `python3`。框架为 `Flask`。启动方式为 `gunicorn`。项目路径为 `/www/wwwroot/myzf`，启动文件为 `/www/wwwroot/myzf/app.py`。

### 5. 配置后台守护进程 (Supervisor)

为了让服务 24 小时稳定运行，我们需要使用 Supervisor 来管理进程。
进入 **软件商店** -> **进程守护管理器** -> **添加守护进程**：

**进程 1：Web 服务 (用于前端访问)**
*   **名称**：ZF_Web
*   **启动用户**：root
*   **运行目录**：`/www/wwwroot/myzf` (您的实际项目路径)
*   **启动命令**：`python app.py` 

**进程 2：任务调度器 (用于定时抓取成绩)**
*   **名称**：ZF_Scheduler
*   **启动用户**：root
*   **运行目录**：`/www/wwwroot/myzf` (您的实际项目路径)
*   **启动命令**：`python task_scheduler.py`

*(注意：如果您使用了虚拟环境，请在启动命令中填写完整的 python 路径，例如 `/www/wwwroot/myzf/venv/bin/python app.py`)*

### 6. 放行端口与访问

*   进入宝塔 **安全** 菜单，放行 **5000** 端口。
*   现在，您可以在浏览器中访问 `http://您的服务器IP:5000` 开始使用了！

---

## 普通 Linux 部署 (非宝塔)

### 1. 环境准备
*   Python 3.8+
*   MySQL 5.7+

### 2. 安装与配置
```bash
# 克隆项目
git clone https://github.com/YourRepo/myzf.git
cd myzf

# 安装依赖
pip install -r requirements.txt

# 修改 init_db.py 中的数据库配置
vi init_db.py

# 初始化数据库
python init_db.py
```

### 3. 启动服务
```bash
# 启动 Web
nohup python app.py > web.log 2>&1 &

# 启动调度器
nohup python task_scheduler.py > scheduler.log 2>&1 &
```

## 使用说明

1.  **访问 Web 界面**：在浏览器中输入 `http://您的服务器IP:5000`。
2.  **配置账号**：
    *   输入您的教务系统 **学号** 和 **密码**。
    *   **ShowDoc Token**：[点击此处获取 Token](https://push.showdoc.com.cn/#/push)（微信扫码关注后即可获得）。
3.  **设置频率**：选择您希望的自动检测频率（如每 30 分钟）。
4.  **保存并启动**：点击“保存配置并开启定时任务”。系统会立即进行一次测试运行，确保账号无误。
5.  **坐等推送**：配置完成后，系统将自动在后台运行，一旦有成绩更新，您的微信将立刻收到通知。

## 许可证

本项目采用 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0") 许可证。简而言之，你可以自由使用、修改和分享本项目的代码，但前提是在其衍生作品中必须保留原始许可证和版权信息，并且必须以相同的许可证发布所有修改过的代码。

## 特别感谢

*   原作者: [NianBroken](https://github.com/NianBroken)
*   API 支持: [openschoolcn/zfn_api](https://github.com/openschoolcn/zfn_api)
