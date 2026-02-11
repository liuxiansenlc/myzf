import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    #数据库用户名
    'user': '',
    #数据库密码
    'password': '',
    #数据库名称
    'database': '',
    'charset': 'utf8mb4'
}

def init_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建用户表
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，主键自增',
            username VARCHAR(50) NOT NULL UNIQUE COMMENT '学号，唯一索引',
            password VARCHAR(100) NOT NULL COMMENT '教务系统密码',
            url VARCHAR(255) DEFAULT 'http://syjw.zjhu.edu.cn/jwglxt/' COMMENT '教务系统登录URL',
            token VARCHAR(255) NOT NULL COMMENT 'ShowDoc推送Token',
            force_push BOOLEAN DEFAULT FALSE COMMENT '是否强制推送(True=每次都推, False=仅变化推)',
            cron_expression VARCHAR(50) DEFAULT '0 * * * *' COMMENT '定时任务Cron表达式',
            is_active BOOLEAN DEFAULT TRUE COMMENT '账号是否激活',
            last_run_time DATETIME COMMENT '最后一次运行时间',
            last_run_status VARCHAR(50) COMMENT '最后一次运行状态(success/failed/error)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) COMMENT='教务系统用户配置表';
        """
        cursor.execute(sql)
        
        # 尝试更新现有表的字段注释（用于表已存在的情况）
        print("正在检查并更新数据库字段注释...")
        alter_statements = [
            "ALTER TABLE users MODIFY id INT AUTO_INCREMENT COMMENT '用户ID，主键自增'",
            "ALTER TABLE users MODIFY username VARCHAR(50) NOT NULL COMMENT '学号，唯一索引'",
            "ALTER TABLE users MODIFY password VARCHAR(100) NOT NULL COMMENT '教务系统密码'",
            "ALTER TABLE users MODIFY url VARCHAR(255) DEFAULT 'http://syjw.zjhu.edu.cn/jwglxt/' COMMENT '教务系统登录URL'",
            "ALTER TABLE users MODIFY token VARCHAR(255) NOT NULL COMMENT 'ShowDoc推送Token'",
            "ALTER TABLE users MODIFY force_push BOOLEAN DEFAULT FALSE COMMENT '是否强制推送(True=每次都推, False=仅变化推)'",
            "ALTER TABLE users MODIFY cron_expression VARCHAR(50) DEFAULT '0 * * * *' COMMENT '定时任务Cron表达式'",
            "ALTER TABLE users MODIFY is_active BOOLEAN DEFAULT TRUE COMMENT '账号是否激活'",
            "ALTER TABLE users MODIFY last_run_time DATETIME COMMENT '最后一次运行时间'",
            "ALTER TABLE users MODIFY last_run_status VARCHAR(50) COMMENT '最后一次运行状态(success/failed/error)'",
            "ALTER TABLE users MODIFY created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'",
            "ALTER TABLE users MODIFY updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
        ]
        
        for stmt in alter_statements:
            try:
                cursor.execute(stmt)
            except Exception as e:
                # 某些情况下修改可能会失败（如索引冲突），这里仅打印警告
                print(f"警告：更新字段注释失败 - {stmt[:50]}... -> {e}")

        conn.commit()
        print("数据库表初始化/更新成功！")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_db()
