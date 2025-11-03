# backend/app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import pymysql
import threading, paho.mqtt.client as mqtt, json

app = Flask(__name__)
latest_data = None  # 用于存储最新的 MQTT 消息内容（坐标信息）。

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


"""
  通过 MQTT 接收 RTK 模块上传的定位数据，并提供一个 Flask HTTP API /api/position 来访问这些数据。  
  RTK → 上传数据 → mqtt.wit-motion.cn
  Flask + MQTT 客户端 → 订阅消息 → 保存最新定位
  其他前端或系统 → 调用 /api/position → 拿到实时坐标
"""
# 当 MQTT 客户端接收到新的消息时，这个函数会被自动调用。
def on_message(client, userdata, msg):
    global latest_data
    latest_data = msg.payload.decode()  #消息（msg.payload）是二进制的，所以需要 .decode() 转成字符串。

# 启动 MQTT 客户端线程
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set("CYL", "FDA4235JHKBFSJF541KDO3NFK4")
    client.on_message = on_message
    client.connect("mqtt.wit-motion.cn", 31883, 60)
    client.subscribe("device/868327071852022/upload")
    client.loop_forever()

# 其他前端或系统 → 调用 /api/position → 拿到实时坐标
@app.route("/api/position")
def get_position():
    if latest_data:
        return jsonify(json.loads(latest_data))
    else:
        return jsonify({"status": "waiting for data"}), 404


# 测试路由
@app.route('/')
def hello():
    return 'Hello Flask + MySQL!'


if __name__ == '__main__':
    # 容器内监听 0.0.0.0
    app.run(host='0.0.0.0', port=5000, debug=True)
