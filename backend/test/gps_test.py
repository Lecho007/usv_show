# def parse_gga(sentence: str):
#     if not sentence.startswith("$GNGGA"):
#         return None
#
#     parts = sentence.strip().split(",")
#     if len(parts) < 15:
#         return None
#
#     # 经纬度转换
#     def nmea_to_decimal(value, direction):
#         if not value:
#             return None
#         degrees = int(float(value) / 100)
#         minutes = float(value) - degrees * 100
#         decimal = degrees + minutes / 60
#         if direction in ['S', 'W']:
#             decimal = -decimal
#         return decimal
#
#     utc_time = parts[1]
#     lat = nmea_to_decimal(parts[2], parts[3])
#     lon = nmea_to_decimal(parts[4], parts[5])
#     fix_quality = int(parts[6]) if parts[6] else 0
#     sats = int(parts[7]) if parts[7] else 0
#     altitude = float(parts[9]) if parts[9] else 0.0
#
#     return {
#         "utc_time": utc_time, # 定位时的 UTC 时间
#         "latitude": lat,    # 纬度
#         "longitude": lon,   # 经度
#         "fix_quality": fix_quality, # 定位状态
#         "satellites": sats, # 使用卫星数
#         "altitude": altitude    # 海拔高度
#     }
#
# # 示例
# data = "$GNGGA,023634.00,4004.73871635,N,11614.19729418,E,1,28,0.7,61.0988,M,-8.4923,M,,*58"
# parsed = parse_gga(data)
# print(parsed)