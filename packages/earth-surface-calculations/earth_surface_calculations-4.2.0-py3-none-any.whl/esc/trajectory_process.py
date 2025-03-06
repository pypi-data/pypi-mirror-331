import math
import numpy as np
from scipy.interpolate import interp1d
from .point_segment import point_to_segment_distance

class Point(object):
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.distance = float("inf")

    def __str__(self):
        return '{} {} {} {}'.format(self.id, self.x, self.y, self.distance)

class DPCompress(object):
    def __init__(self, pointList):
        self.Compressed = list()
        self.pointList = pointList
        self.runDP(pointList)

    def calc_height(self, point1, point2, point):
        tops = abs(
            (point2.x - point1.x) * (point1.y - point.y) - (point1.x - point.x) * (point2.y - point1.y)
        )
        bottom = math.sqrt(
            math.pow(point2.y - point1.y, 2) + math.pow(point2.x - point1.x, 2)
        )
        height = tops / bottom
        return height

    def DouglasPeucker(self, pointList, firsPoint, lastPoint):
        maxDistance = 0.0
        indexFarthest = firsPoint
        for i in range(firsPoint + 1, lastPoint):
            distance = self.calc_height(pointList[firsPoint], pointList[lastPoint], pointList[i])
            if distance < pointList[i].distance:
                pointList[i].distance = distance
            if distance >= maxDistance:
                maxDistance = distance
                indexFarthest = i

        if maxDistance > 0:
            self.Compressed.append(pointList[indexFarthest])
            self.DouglasPeucker(pointList, firsPoint, indexFarthest)
            self.DouglasPeucker(pointList, indexFarthest, lastPoint)

    def runDP(self, pointList):
        if not pointList or len(pointList) < 3:
            return pointList

        firstPoint = 0
        lastPoint = len(pointList) - 1

        self.Compressed.append(pointList[firstPoint])
        self.Compressed.append(pointList[lastPoint])

        self.DouglasPeucker(pointList, firstPoint, lastPoint)

    def getCompressed(self, pointCount):
        self.Compressed.sort(key=lambda point: point.distance, reverse=True)
        result = sorted(self.Compressed[:pointCount], key=lambda point: point.id)
        return result

def trajectory_dilution(coords, count):
    """
    轨迹点稀释函数
    参数:
    coords: 原始轨迹点列表 [(lon1, lat1),...]
    count: 稀释后的点数量
    返回:
    稀释后的轨迹点列表
    """
    if count >= len(coords):
        return coords
    pointList = [Point(i, coord[0], coord[1]) for i, coord in enumerate(coords)]
    dp = DPCompress(pointList)
    simplify2 = [[p.x, p.y] for p in dp.getCompressed(count)]
    return simplify2


def trajectory_interpolation(track, length):
    """
    轨迹插值函数

    参数:
    track: 原始轨迹点列表 [(lon1, lat1),...]
    length: 插值后的轨迹长度
    插值后的轨迹点列表
    """
    track = np.array(track)
    longitudes = track[:, 0]
    latitudes = track[:, 1]
    
    longitudes_diff = np.diff(longitudes)
    jump_indices = np.where(np.abs(longitudes_diff) > 180)[0]

    for idx in jump_indices:
        if longitudes_diff[idx] > 0:
            longitudes[idx + 1:] -= 360
        else:
            longitudes[idx + 1:] += 360
    
    t = np.linspace(0, 1, len(track))
    interp_func_lat = interp1d(t, latitudes, kind='linear')
    interp_func_lon = interp1d(t, longitudes, kind='linear')
    
    t_new = np.linspace(0, 1, length)
    latitudes_new = interp_func_lat(t_new)
    longitudes_new = interp_func_lon(t_new)
    
    longitudes_new = (longitudes_new + 180) % 360 - 180
    
    track_new = np.column_stack((longitudes_new, latitudes_new))
    return track_new.tolist()

def trajectory_simplify(points, epsilon):
    """
    道格拉斯-普克轨迹稀释算法
    
    参数:
    points: 轨迹点列表 [(lon1, lat1), ...]
    epsilon: 稀释阈值（米）
    
    返回:
    简化后的点列表
    """
    dmax = 0
    index = 0
    for i in range(1, len(points)-1):
        d = point_to_segment_distance(points[i], (points[0], points[-1]))
        if d is not None and d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        rec1 = trajectory_simplify(points[:index+1], epsilon)
        rec2 = trajectory_simplify(points[index:], epsilon)
        return rec1[:-1] + rec2
    else:
        return [points[0], points[-1]]

