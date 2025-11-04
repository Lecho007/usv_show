# backend/app.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import time
import pymysql
# import threading, paho.mqtt.client as mqtt, json
import json
from gps_data import parse_gga
from datetime import timedelta
from ms200p_data import parse_oradar_frame
import datetime
app = Flask(__name__)

# === 全局gps定位数据（模拟或来自MQTT）===
gps_data = "$GNGGA,023634.00,4004.73871635,N,11614.19729418,E,1,28,0.7,61.0988,M,-8.4923,M,,*58"
gps_data = parse_gga(gps_data)

# === 全局激光雷达定位数据（模拟或来自MQTT）===
radar_data = bytes([
    0x54, 0x0C, 0xE8, 0x03, 0x10, 0x27,  # 头+点数+转速+起始角度
    # 以下是假数据：12个点，每个3字节
    *([0x00, 0x10, 100] * 12),
    0x20, 0x27, 0x88, 0x13, 0x00
])

radar_data = parse_oradar_frame(radar_data)

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

""" 激光雷达表 """
# 帧表：一帧扫描元信息
class RadarFrame(db.Model):
    __tablename__ = 'radar_frame'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.BigInteger, nullable=False)  # 时间戳
    rpm = db.Column(db.Integer) # 转速
    point_count = db.Column(db.Integer) # 点数
    crc = db.Column(db.Integer) # 校验位
    start_angle = db.Column(db.Float)   # 起始角度
    end_angle = db.Column(db.Float)     # 结束角度
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # 建立一对多关系
    points = db.relationship('RadarPoint', backref='frame', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<RadarFrame id={self.id} rpm={self.rpm} points={self.point_count}>"

# 点表：每个点的角度、距离、强度
class RadarPoint(db.Model):
    __tablename__ = 'radar_point'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    frame_id = db.Column(db.BigInteger, db.ForeignKey('radar_frame.id', ondelete='CASCADE'), nullable=False)
    angle = db.Column(db.Float) # 每个点的角度
    distance_mm = db.Column(db.Integer) # 每个点的距离
    intensity = db.Column(db.Integer)   # 每个点的反射强度

    def __repr__(self):
        return f"<RadarPoint id={self.id} angle={self.angle} distance={self.distance_mm}>"


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


""" 插入 gps 数据到数据库 """
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


""" 插入激光雷达数据 ra_data: dict"""
def insert_radar_frame():
    """
    插入一帧激光雷达数据到数据库
    参数：
        data: dict，包含以下字段：
        {
            "N": 12,
            "rpm": 1000,
            "timestamp": 5000,
            "points": [
                {"angle": 100.0, "distance_mm": 4096, "intensity": 100},
                ...
            ],
            "crc": 0
        }
    返回：
        frame (RadarFrame 对象)
    """
    global radar_data
    ra_data = radar_data
    # 参数检查
    if not ra_data or "points" not in ra_data or not ra_data["points"]:
        raise ValueError("输入数据无效或缺少 points。")

    # 自动计算角度范围与点数
    points_data = ra_data["points"]
    angles = [p["angle"] for p in points_data]
    start_angle = min(angles)
    end_angle = max(angles)
    point_count = len(points_data)

    # 构建 Frame 实例
    frame = RadarFrame(
        timestamp=ra_data.get("timestamp", 0),
        rpm=ra_data.get("rpm", 0),
        point_count=point_count,
        crc=ra_data.get("crc", 0),
        start_angle=start_angle,
        end_angle=end_angle,
        created_at=datetime.datetime.utcnow()
    )

    # 构建 Points 列表
    frame.points = [
        RadarPoint(
            angle=p.get("angle", 0),
            distance_mm=p.get("distance_mm", 0),
            intensity=p.get("intensity", 0)
        )
        for p in points_data
    ]

    # 提交数据库
    try:
        db.session.add(frame)
        db.session.commit()
        print(f"插入成功：帧 ID={frame.id}, 含 {point_count} 点")
        return frame
    except Exception as e:
        db.session.rollback()
        print(f"数据插入失败: {e}")
        raise


""" 按帧 ID 获取激光雷达数据 """
def get_radar_frame(frame_id: int):
    """
    根据帧ID获取激光雷达帧及其所有点数据
    """
    frame = RadarFrame.query.filter_by(id=frame_id).first()
    if not frame:
        return None

    return {
        "id": frame.id,
        "timestamp": frame.timestamp,
        "rpm": frame.rpm,
        "point_count": frame.point_count,
        "crc": frame.crc,
        "start_angle": frame.start_angle,
        "end_angle": frame.end_angle,
        "created_at": frame.created_at.isoformat(),
        "points": [
            {
                "angle": p.angle,
                "distance_mm": p.distance_mm,
                "intensity": p.intensity
            }
            for p in frame.points
        ]
    }


"""
  通过 MQTT 接收 RTK 模块上传的定位数据，并提供一个 Flask HTTP API /api/position 来访问这些数据。  
  RTK → 上传数据 → mqtt.wit-motion.cn
  Flask + MQTT 客户端 → 订阅消息 → 保存最新定位
  其他前端或系统 → 调用 /api/position → 拿到实时坐标
"""
# 当 MQTT 客户端接收到新的消息时，这个函数会被自动调用。
# def on_message(client, userdata, msg):
#     global gps_data
#     """消息类型: $GNGGA,023634.00,4004.73871635,N,11614.19729418,E,1,28,0.7,61.0988,M,-8.4923,M,,*58"""
#     gps_data = parse_gga(msg.payload)
#     gps_insert(gps_data)


# 启动 MQTT 客户端线程
# def mqtt_thread():
    # client = mqtt.Client()
    # client.username_pw_set("CYL", "FDA4235JHKBFSJF541KDO3NFK4")
    # client.on_message = on_message
    # client.connect("mqtt.wit-motion.cn", 31883, 60)
    # client.subscribe("device/868327071852022/upload")
    # client.loop_forever()


# 其他前端或系统 调用 /api/position → 拿到实时坐标
@app.route("/api/position")
def get_position():
    if gps_data:
        return jsonify(gps_data)
    else:
        return jsonify({"status": "waiting for data"}), 404

# 获取最近一条 GPS 数据
@app.route("/api/gps/last", methods=["GET"])
def get_last_gps():
    gps_record = GpsTable.query.order_by(GpsTable.id.desc()).first()
    if not gps_record:
        return jsonify({"error": "No GPS data found"}), 404
    return jsonify(gps_record.to_dict())


# 调用/api/radar/latest 拿到最新的雷达点云数据
@app.route('/api/radar/latest', methods=['GET'])
def get_latest_frame_api():
    frame = RadarFrame.query.order_by(RadarFrame.created_at.desc()).first()
    if not frame:
        return jsonify({"message": "No radar data found"}), 404

    return jsonify({
        "id": frame.id,
        "timestamp": frame.timestamp,
        "rpm": frame.rpm,
        "start_angle": frame.start_angle,
        "end_angle": frame.end_angle,
        "point_count": frame.point_count,
        "points": [
            {"angle": p.angle, "distance_mm": p.distance_mm, "intensity": p.intensity}
            for p in frame.points
        ]
    })


""" 插入点云数据api """
@app.route("/api/insert_radar")
def insert_radar_frame_0():
    """
    插入一帧激光雷达数据到数据库
    返回：
        JSON 格式，包含插入成功与帧ID
    """
    global radar_data
    ra_data = radar_data

    # 参数检查
    if not ra_data or "points" not in ra_data or not ra_data["points"]:
        return jsonify({"error": "输入数据无效或缺少 points"}), 400

    # 自动计算角度范围与点数
    points_data = ra_data["points"]
    angles = [p["angle"] for p in points_data]
    start_angle = min(angles)
    end_angle = max(angles)
    point_count = len(points_data)

    # 构建 Frame 实例
    frame = RadarFrame(
        timestamp=ra_data.get("timestamp", 0),
        rpm=ra_data.get("rpm", 0),
        point_count=point_count,
        crc=ra_data.get("crc", 0),
        start_angle=start_angle,
        end_angle=end_angle,
        created_at=datetime.datetime.utcnow()
    )

    # 构建 Points 列表
    frame.points = [
        RadarPoint(
            angle=p.get("angle", 0),
            distance_mm=p.get("distance_mm", 0),
            intensity=p.get("intensity", 0)
        )
        for p in points_data
    ]

    # 提交数据库
    try:
        db.session.add(frame)
        db.session.commit()
        print(f"插入成功：帧 ID={frame.id}, 含 {point_count} 点")
        return jsonify({
            "message": "插入成功",
            "frame_id": frame.id,
            "point_count": point_count
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"数据插入失败: {e}")
        return jsonify({"error": str(e)}), 500

# 测试路由
@app.route('/')
def hello():
    return 'Hello Flask + MySQL!'


if __name__ == '__main__':
    # 容器内监听 0.0.0.0
    app.run(host='0.0.0.0', port=5000, debug=True)
