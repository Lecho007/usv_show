# backend/app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import pymysql

app = Flask(__name__)

# 配置 MySQL 数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usvuser:usvpass@mysql:3306/usvdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定义 ORM 模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 等待 MySQL 完全启动
def wait_for_mysql():
    while True:
        try:
            conn = pymysql.connect(
                host='mysql',
                user='usvuser',
                password='usvpass',
                database='usvdb',
                port=3306
            )
            conn.close()
            print(" MySQL is ready!")
            break
        except pymysql.err.OperationalError:
            print("Waiting for MySQL...")
            time.sleep(2)

# 初始化数据库表
with app.app_context():
    wait_for_mysql()
    db.create_all()
    print("Tables created (if not exist)")

# 测试路由
@app.route('/')
def hello():
    return 'Hello Flask + MySQL!'

if __name__ == '__main__':
    # 容器内监听 0.0.0.0
    app.run(host='0.0.0.0', port=5000, debug=True)
