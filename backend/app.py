# backend/app.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
import pymysql
# import threading, paho.mqtt.client as mqtt, json
import json
import datetime
from gps_data import parse_gga
app = Flask(__name__)

# === 全局gps定位数据（模拟或来自MQTT）===
data = "$GNGGA,023634.00,4004.73871635,N,11614.19729418,E,1,28,0.7,61.0988,M,-8.4923,M,,*58"
gps_data = parse_gga(data)

# === 全局激光雷达定位数据（模拟或来自MQTT）===


# 配置 MySQL 数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usvuser:usvpass@mysql:3306/usvdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定义 ORM 模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# GPS ORM 模型定义
class GpsTable(db.Model):
    __tablename__ = 'gps_tb'   # 表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    utc_time = db.Column(db.String(20), nullable=False)  # UTC 时间字符串
    latitude = db.Column(db.Float, nullable=False)       # 纬度
    longitude = db.Column(db.Float, nullable=False)      # 经度
    fix_quality = db.Column(db.Integer, nullable=False)  # 定位质量
    satellites = db.Column(db.Integer, nullable=False)   # 卫星数量
    altitude = db.Column(db.Float, nullable=False)       # 海拔高度
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # 数据记录时间

    def to_dict(self):
        return {
            "id": self.id,
            "utc_time": self.utc_time,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "fix_quality": self.fix_quality,
            "satellites": self.satellites,
            "altitude": self.altitude,
            "created_at": self.created_at.isoformat()
        }



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


""" 插入 latest_data 数据到数据库 """
def gps_insert(insert_gps_data):
    if not insert_gps_data:
        return jsonify({"status": "error", "message": "no data available"}), 404

    pos = GpsTable(
        utc_time=insert_gps_data.get("utc_time"),
        latitude=insert_gps_data.get("latitude"),
        longitude=insert_gps_data.get("longitude"),
        fix_quality=insert_gps_data.get("fix_quality"),
        satellites=insert_gps_data.get("satellites"),
        altitude=insert_gps_data.get("altitude")
    )
    db.session.add(pos)
    db.session.commit()

    return jsonify({"status": "ok", "inserted_id": pos.id, "data": insert_gps_data})



"""
  通过 MQTT 接收 RTK 模块上传的定位数据，并提供一个 Flask HTTP API /api/position 来访问这些数据。  
  RTK → 上传数据 → mqtt.wit-motion.cn
  Flask + MQTT 客户端 → 订阅消息 → 保存最新定位
  其他前端或系统 → 调用 /api/position → 拿到实时坐标
"""
# 当 MQTT 客户端接收到新的消息时，这个函数会被自动调用。
def on_message(client, userdata, msg):
    global gps_data
    """消息类型: $GNGGA,023634.00,4004.73871635,N,11614.19729418,E,1,28,0.7,61.0988,M,-8.4923,M,,*58"""
    gps_data = parse_gga(msg.payload)
    gps_insert(gps_data)


# 启动 MQTT 客户端线程
# def mqtt_thread():
    # client = mqtt.Client()
    # client.username_pw_set("CYL", "FDA4235JHKBFSJF541KDO3NFK4")
    # client.on_message = on_message
    # client.connect("mqtt.wit-motion.cn", 31883, 60)
    # client.subscribe("device/868327071852022/upload")
    # client.loop_forever()


# 其他前端或系统 → 调用 /api/position → 拿到实时坐标
@app.route("/api/position")
def get_position():
    if gps_data:
        return jsonify(gps_data)
    else:
        return jsonify({"status": "waiting for data"}), 404



# 测试路由
@app.route('/')
def hello():
    return 'Hello Flask + MySQL!'


if __name__ == '__main__':
    # 容器内监听 0.0.0.0
    app.run(host='172.26.47.124', port=5000, debug=True)
