# import struct
#
# def parse_oradar_frame(data: bytes):
#     """解析一帧 Oradar MS200p 激光雷达点云数据（支持动态 N）"""
#     if len(data) < 10 or data[0] != 0x54:
#         return None  # 无效帧
#
#     # 动态读取点数
#     N = data[1] & 0x1F  # 低5位 = 点数
#     expected_len = 10 + 3 * N  # 理论帧长度
#
#     if len(data) < expected_len:
#         print(f"[警告] 数据长度不完整：实际 {len(data)}，应为 {expected_len}")
#         return None
#
#     rpm, = struct.unpack_from("<H", data, 2)
#     start_angle, = struct.unpack_from("<H", data, 4)
#
#     # 解析点云
#     points = []
#     for i in range(N):
#         offset = 6 + 3 * i
#         distance, intensity = struct.unpack_from("<HB", data, offset)
#         points.append((distance, intensity))
#
#     end_angle, timestamp = struct.unpack_from("<HH", data, 6 + 3 * N)
#     crc = data[10 + 3 * N]
#
#     # 角度插值
#     start_angle_deg = start_angle / 100.0
#     end_angle_deg = end_angle / 100.0
#     if end_angle_deg < start_angle_deg:
#         end_angle_deg += 360.0
#     step = (end_angle_deg - start_angle_deg) / (N - 1) if N > 1 else 0
#
#     point_cloud = []
#     for i, (distance, intensity) in enumerate(points):
#         angle = (start_angle_deg + i * step) % 360
#         point_cloud.append({
#             "angle": round(angle, 2),
#             "distance_mm": distance,
#             "intensity": intensity
#         })
#
#     return {
#         "N": N,
#         "rpm": rpm,
#         "timestamp": timestamp,
#         "points": point_cloud,
#         "crc": crc
#     }


# # 假设接收一帧二进制数据
# frame = bytes([
#     0x54, 0x0C, 0xE8, 0x03, 0x10, 0x27,  # 头+点数+转速+起始角度
#     # 以下是假数据：12个点，每个3字节
#     *([0x00, 0x10, 100] * 12),
#     0x20, 0x27, 0x88, 0x13, 0x00
# ])
#
# parsed = parse_oradar_frame(frame)
# print(parsed)
