from flask import Flask, render_template, request, jsonify
import pymysql
import os
import subprocess
import tempfile
import shutil
import uuid
from init_db import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_script():
    # 立即运行一次（用于测试）
    data = request.json
    result = run_task_internal(data)
    return jsonify(result)

@app.route('/save_task', methods=['POST'])
def save_task():
    data = request.json
    url = data.get('url', 'http://syjw.zjhu.edu.cn/jwglxt/')
    username = data.get('username')
    password = data.get('password')
    token = data.get('token')
    force_push = data.get('force_push', False)
    cron_expression = data.get('cron_expression', '0 8-22/2 * * *') # 默认定时策略
    
    if not username or not password or not token:
        return jsonify({'status': 'error', 'message': '必填项不能为空'})

    # 1. 先执行一次任务进行校验
    verification_result = run_task_internal(data)
    if verification_result['status'] != 'success':
        return jsonify({
            'status': 'error', 
            'message': '账号验证失败，请检查账号密码是否正确！',
            'details': verification_result.get('output') or verification_result.get('error')
        })

    # 2. 验证通过后，保存到数据库
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否存在，存在则更新，不存在则插入
        sql = """
        INSERT INTO users (username, password, url, token, force_push, cron_expression) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        password=%s, url=%s, token=%s, force_push=%s, cron_expression=%s, is_active=TRUE
        """
        cursor.execute(sql, (
            username, password, url, token, force_push, cron_expression,
            password, url, token, force_push, cron_expression
        ))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': '验证通过！任务已保存并激活'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/query')
def query_page():
    return render_template('query.html')

@app.route('/api/get_user_status', methods=['POST'])
def get_user_status():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': '请输入学号和密码'})
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证用户名和密码
        sql = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            return jsonify({
                'status': 'success',
                'data': {
                    'cron_expression': user['cron_expression'],
                    'force_push': bool(user['force_push']),
                    'is_active': bool(user['is_active']),
                    'last_run_time': str(user['last_run_time']) if user['last_run_time'] else None,
                    'last_run_status': user['last_run_status']
                }
            })
        else:
            return jsonify({'status': 'error', 'message': '账号或密码错误，或者该用户未注册任务'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/update_user_status', methods=['POST'])
def update_user_status():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_active = data.get('is_active')
    force_push = data.get('force_push')
    cron_expression = data.get('cron_expression')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': '验证信息缺失'})
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 再次验证身份并更新
        # 这里为了安全，应该先查是否存在匹配的记录，再更新
        # 或者直接 update ... where username=... and password=...
        
        sql = """
        UPDATE users 
        SET is_active=%s, force_push=%s, cron_expression=%s 
        WHERE username=%s AND password=%s
        """
        result = cursor.execute(sql, (is_active, force_push, cron_expression, username, password))
        conn.commit()
        conn.close()
        
        if result > 0:
            return jsonify({'status': 'success', 'message': '设置更新成功！'})
        else:
            # 可能是没有变化，也可能是密码错误
            # 我们可以先查一下用户是否存在来区分，但为了简单，这里假设如果前端流程正常，
            # 这里的0通常意味着没有行被修改（值一样）或者密码错。
            # 为了更好的体验，我们先查一下
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                 return jsonify({'status': 'success', 'message': '设置已更新（无变化）'})
            else:
                 return jsonify({'status': 'error', 'message': '更新失败：账号或密码错误'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def run_task_internal(data):
    # 执行具体的查询逻辑 (内部函数，返回字典)
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    token = data.get('token')
    force_push = str(data.get('force_push', False))
    
    # 使用用户的学号作为唯一目录名，以便持久化存储"旧成绩"
    # 这样可以实现"成绩变化才推送"的功能
    user_data_dir = os.path.join(os.getcwd(), 'data_users', username)
    os.makedirs(user_data_dir, exist_ok=True)
    
    try:
        env = os.environ.copy()
        env['URL'] = url
        env['USERNAME'] = username
        env['PASSWORD'] = password
        env['TOKEN'] = token
        env['FORCE_PUSH_MESSAGE'] = force_push
        env['DATA_DIR'] = user_data_dir
        
        python_cmd = 'python3' if os.name != 'nt' else 'python'
        
        result = subprocess.run(
            [python_cmd, 'main.py'],
            env=env,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        return {
            'status': 'success' if result.returncode == 0 else 'error',
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode
        }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
