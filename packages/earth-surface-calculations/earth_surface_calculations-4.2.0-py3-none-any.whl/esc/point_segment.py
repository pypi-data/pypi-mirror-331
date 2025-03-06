from math import radians, cos, sin, sqrt, asin

def to_cartesian(lon, lat):
    """将地理坐标转换为三维笛卡尔坐标"""
    if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
        raise ValueError(f"无效的坐标值: ({lon}, {lat})，经度需在-180到180度之间，纬度需在-90到90度之间")
    lon_r = radians(lon)
    lat_r = radians(lat)
    return (cos(lat_r) * cos(lon_r), cos(lat_r) * sin(lon_r), sin(lat_r))

def point_to_segment_distance(point, line):
    """
    计算点到线段的最短球面距离（单位：米）
    参数：
    - point: 点的经纬度坐标，格式为 (经度, 纬度)
    - line: 线段的两个端点坐标，格式为 [(经度1, 纬度1), (经度2, 纬度2)]
    """
    lon, lat = point
    seg_lon1, seg_lat1 = line[0]
    seg_lon2, seg_lat2 = line[1]
    # 校验所有输入参数
    for v in [lon, lat, seg_lon1, seg_lat1, seg_lon2, seg_lat2]:
        if not isinstance(v, (int, float)):
            raise TypeError("坐标参数必须为数值类型")

    # 转换为三维坐标
    p = to_cartesian(lon, lat)
    a = to_cartesian(seg_lon1, seg_lat1)
    b = to_cartesian(seg_lon2, seg_lat2)

    # 计算向量ab和ap
    ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    ap = (p[0]-a[0], p[1]-a[1], p[2]-a[2])

    # 计算投影参数
    t = sum(ab[i]*ap[i] for i in range(3)) / sum(x**2 for x in ab)

    # 处理端点情况
    if t <= 0:
        closest = a
    elif t >= 1:
        closest = b
    else:
        closest = (a[0]+t*ab[0], a[1]+t*ab[1], a[2]+t*ab[2])

    # 计算球面三角形面积
    cross = (p[1]*closest[2] - p[2]*closest[1],
             p[2]*closest[0] - p[0]*closest[2],
             p[0]*closest[1] - p[1]*closest[0])
    area = 0.5 * sqrt(sum(x**2 for x in cross))
    
    # 通过球面面积公式计算距离
    return 2 * 6378137 * asin(min(area, 1.0))