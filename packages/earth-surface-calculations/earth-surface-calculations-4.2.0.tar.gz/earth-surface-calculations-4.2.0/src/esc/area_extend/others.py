# 一些可能有用的函数
import math
from . import translate
import numpy as np
from . import geodesic_buffer

def point_to_line(points):
    # 大圆上的点获取路径
    lines = []
    for i in range(1, len(points),1):
        p1 = points[i-1]
        p2 = points[i]
        
        vec = np.cross(np.array(translate.vectopoint(p1)),np.array(translate.vectopoint(p2)))
        c_vec = translate.pointtovect(vec.tolist())

        line = (p1, p2, (0, c_vec))
        lines.append(line)


    p1 = points[len(points)-1]
    p2 = points[0]
    vec = np.cross(np.array(translate.vectopoint(p1)),np.array(translate.vectopoint(p2)))
    c_vec = translate.pointtovect(vec.tolist())
    line = (p1, p2, (0, c_vec))
    lines.append(line)
    return lines

def kilo_to_degree(l):
    # 千米转换为对地角度
    l = l * 1000
    R = 6371000
    while l >= R:
        l = l - R
    L = 2 * math.pi * R
    degree = (l / L) * 2 * math.pi
    return degree


def pd_point_online(point, line):
    p_a = translate.vectopoint(line[0])
    p_b = translate.vectopoint(line[1])
    vec_n = np.array(translate.vectopoint((line[2][1])))
    vec_ap = (point[0]-p_a[0], point[1]-p_a[1], point[2]-p_a[2])
    vec_ab = (point[0]-p_b[0], point[1]-p_b[1], point[2]-p_b[2])
    vec_ab = np.array(vec_ab)
    vec_ap = np.array(vec_ap)
    vec_nn = np.cross(vec_ap, vec_ab)
    cos_a = np.dot(vec_n, vec_nn)/(np.linalg.norm(vec_nn)*np.linalg.norm(vec_n))
    if cos_a>0:
        return False
    else:
        return True


def points_on_line(line):
    # 获取线段上的点（约10度一个点）
    points = []
    p_a = translate.vectopoint(line[0])
    p_b = translate.vectopoint(line[1])
    p_c = translate.vectopoint(line[2][1])
    p_d = line[2][0]
    p_o = [p_c[0]*p_d, p_c[1]*p_d, p_c[2]*p_d]
    o_a = [p_a[0] - p_o[0],p_a[1] - p_o[1],p_a[2] - p_o[2]]
    o_b = [p_b[0] - p_o[0],p_b[1] - p_o[1],p_b[2] - p_o[2]]
    vec1 = np.cross(-1*np.array(p_c), np.array(o_a))
    vec2 = np.cross(-1*np.array(p_c), np.array(o_b))
    cos_alpha = np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))
    if cos_alpha > 1:
        cos_alpha = 1.0
    alpha = math.acos(cos_alpha)
    alpha = math.degrees(alpha)
    num = int(alpha/10)
    vec_list = []
    for i in range(0,int(num/2),1):
        vec_n = ((i + 1) * vec2) / (int(num/2) + 1)
        v = np.add(vec1,vec_n)
        vec_list.append(v.tolist())
    if num%2 == 1:
        v = np.add(vec1,vec2)
        vec_list.append(v.tolist())
    for i in range(int(num/2)+1,1,-1):
        vec_n = ((i-1) * vec1) / (int(num/2) + 1)
        v = np.add(vec_n,vec2)
        vec_list.append(v.tolist())

    vec_list_copy = vec_list.copy()
    vec_list = []
    for i in vec_list_copy:
        if i not in vec_list:
            vec_list.append(i)

    cir1 = (p_c,p_d)
    for vec in vec_list:
        cir2 = (vec, 0)
        ret, res = geodesic_buffer.caculate_points_cir(cir1, cir2)
        if ret == 1:
            points.append(res)

        if ret == 2:
            p1 = res[0]
            p2 = res[1]
            if pd_point_online(p2, line):
                points.append(p2)
            elif pd_point_online(p1, line):
                points.append(p1)

    results = [line[0]]
    for p in points:
        r = translate.pointtovect(p)
        results.append(r)
    results.append(line[1])

    return results
