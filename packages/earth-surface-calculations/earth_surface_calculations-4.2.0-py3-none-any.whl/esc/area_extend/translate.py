# 经纬度和坐标相互转换
import math
import numpy as np

def vectopoint(vec, end=False):
    # 将经纬度对应xyz坐标系中(法向量)
    (latitude, longitude) = vec
    lat_rad = math.radians(latitude)
    long_rad = math.radians(longitude)
    x = math.cos(lat_rad) * math.cos(long_rad)
    y = math.cos(lat_rad) * math.sin(long_rad)
    z = math.sin(lat_rad)
    if abs(x) < 1e-5:
        x = 0
    if abs(y) < 1e-5:
        y = 0
    if abs(z) < 1e-5:
        z = 0
    if end:
        x = round(math.cos(lat_rad) * math.cos(long_rad), 7)
        y = round(math.cos(lat_rad) * math.sin(long_rad), 7)
        z = round(math.sin(lat_rad), 7)
    return [x,y,z]


def pointtovect(point, end=False):
    # xyz坐标系转换为经纬度
    point = (np.array(point) / np.linalg.norm(np.array(point))).tolist()
    (x, y, z) = point
    longitude_rad = math.atan2(y, x)
    latitude_rad = math.asin(z)
    longitude = math.degrees(longitude_rad)
    latitude = math.degrees(latitude_rad)
    if abs(longitude) < 1e-5:
        longitude = 0.0
    if abs(latitude) < 1e-5:
        latitude = 0.0
    if end:
        longitude = round(math.degrees(longitude_rad), 7)
        latitude = round(math.degrees(latitude_rad), 7)
    return (latitude, longitude)


def distance_point_to_spare(v_1, v_2, point):
    a = np.array(v_1)
    b = np.array(v_2)
    A = np.array(point)
    N = np.cross(a, b)
    P = A - (np.dot(A, N) / np.dot(N, N)) * N
    D = np.linalg.norm(A - P)
    return round(D, 5)


