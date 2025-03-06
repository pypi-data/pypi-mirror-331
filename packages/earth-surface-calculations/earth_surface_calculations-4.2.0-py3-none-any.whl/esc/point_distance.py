from math import asin, cos, radians, sin, sqrt, atan2, tan

def _vincenty_distance(point1, point2):
    """
    计算两个经纬度坐标之间的球面vincenty距离（单位：米）
    参数：
    - point1: 第一个经纬度坐标，格式为 (经度, 纬度)
    - point2: 第二个经纬度坐标，格式为 (经度, 纬度)
    """
    lon1, lat1  = radians(point1[0]), radians(point1[1])
    lon2, lat2  = radians(point2[0]), radians(point2[1])

    a = 6378137.0  # 地球长轴（米）
    f = 1 / 298.257223563  # 扁率
    b = (1 - f) * a

    L = lon2 - lon1
    U1 = atan2((1 - f) * tan(lat1), 1)
    U2 = atan2((1 - f) * tan(lat2), 1)
    sinU1, cosU1 = sin(U1), cos(U1)
    sinU2, cosU2 = sin(U2), cos(U2)

    lambda_ = L
    while True:
        sinLambda, cosLambda = sin(lambda_), cos(lambda_)
        sinSigma = sqrt((cosU2 * sinLambda) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        if sinSigma == 0:  # 重叠点
            return 0.0
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cos2Alpha = 1 - sinAlpha ** 2
        cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cos2Alpha if cos2Alpha != 0 else 0  # 赤道线上的点
        C = f / 16 * cos2Alpha * (4 + f * (4 - 3 * cos2Alpha))
        lambda_prev = lambda_
        lambda_ = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM ** 2)))
        if abs(lambda_ - lambda_prev) < 1e-12:
            break

    u2 = cos2Alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    s = b * A * (sigma - deltaSigma)

    return s

def _haversine_distance(point1, point2):
    """
    计算两个经纬度坐标之间的球面haversine距离（单位：米）
    参数：
    - point1: 第一个经纬度坐标，格式为 (经度, 纬度)
    - point2: 第二个经纬度坐标，格式为 (经度, 纬度)
    """
    lon1, lat1  = radians(point1[0]), radians(point1[1])
    lon2, lat2  = radians(point2[0]), radians(point2[1])

    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6378137
    return c * r

def point_distance(point1, point2, method='haversine'):
    """
    计算两个经纬度坐标之间的球面距离（单位：米）
    参数：
    - point1: 第一个经纬度坐标，格式为 (经度, 纬度)
    - point2: 第二个经纬度坐标，格式为 (经度, 纬度)
    - method: 计算方法，可选 'haversine' 或 'vincenty'，默认为 'haversine'
    """
    match method:
        case 'haversine':
            return _haversine_distance(point1, point2)
        case 'vincenty':
            return _vincenty_distance(point1, point2)
        case _:
            raise ValueError(f"无效的计算方法: {method}，请使用'haversine'或'vincenty'")
