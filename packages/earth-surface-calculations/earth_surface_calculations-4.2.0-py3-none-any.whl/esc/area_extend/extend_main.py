# 主函数
from .area_extend import extend
from .others import point_to_line, kilo_to_degree, points_on_line
from .translate import vectopoint, pointtovect


def atoa(arealist):
    area = []
    for a in arealist:
        a0 = vectopoint(a[0])
        a1 = vectopoint(a[1])
        a2 = vectopoint(a[2][1])
        d = (a[2][0])
        area.append((a0,a1,(a2,d)))

    return area

    
def abacktoa(arealist):
    area = []
    for a in arealist:
        a0 = pointtovect(a[0], end=True)
        a1 = pointtovect(a[1], end=True)
        a2 = pointtovect(a[2][0], end=True)
        # d = round((a[2][1]), 5)
        d = a[2][1]
        if int(d) == d:
            d = int(d)
        area.append((a0,a1,(d, a2)))
    return area

def ex(areaList, d):
    # 区域拓展函数
    results = []
    arealist = atoa(areaList)
    (ret, res) = extend(arealist, d)
    if ret == 'error':
        return res
    else:
        for r in res:
            res_to_a = abacktoa(r)
            results.append(res_to_a)
        return results

def lines2points(lines):
    point_new = []
    for a in lines:
        res = points_on_line(a)
        for r in res:
            n = vectopoint(r)
            point_new.append(n)
    all_points = []
    for i in point_new:
        if i not in all_points:
            all_points.append(i)
    return all_points

def points2points(points, d):
    """
    点拓展函数
    :param points: 点列表
    :param d: 距离
    :return: 点列表
    """
    d = kilo_to_degree(d)
    lines = point_to_line(points)
    lines_new = ex(lines, d)
    points_new = []
    for l in lines_new:
        points_list = []
        points_xyz = lines2points(l)
        for p in points_xyz:
            points_list.append(pointtovect(p, end=True))
        points_new.append(points_list)
    return points_new
