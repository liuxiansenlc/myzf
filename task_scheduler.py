import pymysql
import subprocess
import os
import time
from datetime import datetime, timedelta
from init_db import DB_CONFIG
import threading
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduler.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_db_connection():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def execute_user_task(user):
    logging.info(f"开始执行任务: 用户 {user['username']}")
    
    # 构造数据目录
    user_data_dir = os.path.join(os.getcwd(), 'data_users', user['username'])
    os.makedirs(user_data_dir, exist_ok=True)
    
    # 设置环境变量
    env = os.environ.copy()
    env['URL'] = user['url']
    env['USERNAME'] = user['username']
    env['PASSWORD'] = user['password']
    env['TOKEN'] = user['token']
    env['FORCE_PUSH_MESSAGE'] = str(user['force_push'] == 1)
    env['DATA_DIR'] = user_data_dir
    
    try:
        python_cmd = 'python3' if os.name != 'nt' else 'python'
        result = subprocess.run(
            [python_cmd, 'main.py'],
            env=env,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        status = 'success' if result.returncode == 0 else 'failed'
        logging.info(f"任务完成: 用户 {user['username']}, 状态: {status}")
        if result.returncode != 0:
            logging.error(f"任务失败输出: {result.stderr}")
        
        # 更新数据库运行状态
        update_run_status(user['id'], status)
        
    except Exception as e:
        logging.error(f"任务异常: 用户 {user['username']}, 错误: {e}")
        update_run_status(user['id'], 'error')

def update_run_status(user_id, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_run_time = NOW(), last_run_status = %s WHERE id = %s",
            (status, user_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"更新状态失败: {e}")

def check_and_run_tasks():
    # 注意：这是一个简化的调度器
    # 在生产环境中，通常使用 APScheduler 或 Celery 配合 Cron 表达式
    # 这里为了简化部署，我们使用简单的轮询机制
    # 实际部署时，建议将此脚本加入宝塔的计划任务，每分钟运行一次，或者使用常驻进程
    
    logging.info("检查任务队列...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有激活的用户
        cursor.execute("SELECT * FROM users WHERE is_active = TRUE")
        users = cursor.fetchall()
        conn.close()
        
        now = datetime.now()
        
        for user in users:
            cron = user['cron_expression']
            should_run = False
            
            # 解析时间间隔逻辑
            # 我们通过判断距离上次运行时间是否超过了设定的间隔来决定是否运行
            last_run = user['last_run_time']
            
            interval_minutes = 0
            if "*/1" in cron: # 每1分钟
                interval_minutes = 1
            elif "*/30" in cron: # 每30分钟
                interval_minutes = 30
            elif "0 *" in cron: # 每60分钟
                interval_minutes = 60
            
            if interval_minutes > 0:
                if not last_run:
                    should_run = True # 从未运行过，立即运行
                else:
                    # 计算时间差
                    diff = now - last_run
                    if diff.total_seconds() / 60 >= interval_minutes:
                        should_run = True
            
            if should_run:
                # 启动线程执行任务，避免阻塞
                t = threading.Thread(target=execute_user_task, args=(user,))
                t.start()
                
    except Exception as e:
        logging.error(f"调度器错误: {e}")

if __name__ == "__main__":
    # 模式选择：
    # 1. 如果通过宝塔计划任务（Shell脚本）每分钟调用一次，则只执行一次 check_and_run_tasks()
    # 2. 如果作为常驻进程（Supervisor/Systemd），则循环执行
    
    # 这里我们采用循环模式，配合 nohup 或 Supervisor 使用
    logging.info("任务调度器已启动 (循环模式)...")
    while True:
        check_and_run_tasks()
        # 每分钟检查一次
        time.sleep(60) 
