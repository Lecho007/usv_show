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
#
#
# # 假设接收一帧二进制数据
# frame = bytes([
#     0x54, 0x0C, 0xE8, 0x03, 0x10, 0x27,  # 头+点数+转速+起始角度
#     # 以下是假数据：12个点，每个3字节
#     *([0x00, 0x10, 100] * 12),
#     0x20, 0x27, 0x88, 0x13, 0x00
# ])
#
# # parsed = parse_oradar_frame(frame)
# # print(parsed)
# hex_str = ("54 50 00 00 00 00 00 00 00 00 AA 55 01 01 99 AF 99 AF AB 54 00 00 "
#            "AA 55 00 28 D9 AF 1F 05 34 91 00 00 00 00 00 00 00 00 00 00 00 00 00 "
#            "00 00 00 00 00 00 00 00 00 00 00 DC 2D 00 00 00 00 1C 7C 18 7D 04 7E "
#            "34 7D 30 7C F4 7A 2C 7A 88 79 F8 78 34 78 0C 77 10 76 18 75 48 74 00"
#            " 00 A8 4E 8C 4E 18 4F BC 4F 00 00 00 00 7C 39 E4 39 00 00 48 6C AA 55"
#            " 00 22 5F 05 4D 0D AC 13 DC 6B 44 68 00 6B 50 6A C8 69 50 69 84 68 84 "
#            "67 48 67 CC 66 68 66 DC 65 84 65 44 65 BC 64 54 64 C4 63 88 63 F0 62 "
#            "24 63 7C 63 28 63 A0 61 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
#            "00 00 00 00 00 00 00 AA 55 00 28 8D 0D DF 16 7C 3C 00 00 00 00 00 00 00 "
#            "00 98 5B E0 5B 40 5C 68 5C 10 5C E4 5B 80 5B 84 58 48 58 34 58 28 58 E4 "
#            "5A 80 5A 74 5A 34 5A 20 5A 1C 5A E0 59")  # 你的雷达数据
# # 转换为 bytes
# data_bytes = bytes.fromhex(hex_str)
#
# print(data_bytes)
# print(len(data_bytes))
#
# n = parse_oradar_frame(data_bytes)
# print(n)