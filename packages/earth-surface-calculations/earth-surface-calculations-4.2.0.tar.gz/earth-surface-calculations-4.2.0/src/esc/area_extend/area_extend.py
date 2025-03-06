# 区域拓展函数
import numpy as np
import math
from . import geodesic_buffer


def clear_lines(line):
    p_a = np.array(line[0])
    p_o = np.array(line[2][0])
    d = abs(line[2][1])
    cosa = np.dot(p_a,p_o)/(np.linalg.norm(p_o)*np.linalg.norm(p_a))
    if cosa < 0:
        d = -d
    a = line[0]
    b = line[1]
    c = line[2][0]
    return (a, b ,(c, d))

    
def export_point(point1,point2,point_center):
    # 圆心+2个点求圆(用于点的拓展)
    (x1, y1, z1) = point1
    (x2, y2, z2) = point_center
    v_n = (-x2,-y2,-z2)
    d = abs((x1 * x2 + y1 * y2 + z1 * z2) / (x2 * x2 + y2 * y2 + z2 * z2))
    if d == 1:
        d = 1
        return (point1, point1, (v_n,d))
    res = (point1, point2, (v_n,d))
    res = clear_lines(res)
    return res


def get_out_circle(ab, circle, d):
    # 计算出移动后小圆的参数
    d = math.sin(d)
    if abs(d) < 1e-5:
        d = 0.0
    vec_old = circle[0]
    d_old = circle[1]
    degree = np.dot(np.array(ab), np.array(vec_old))/(np.linalg.norm(np.array(ab)) * np.linalg.norm(np.array(vec_old)))
    if degree > 0: # 小于90度,同向
        if d_old < 0:
            dd = d_old - d
        else:
            dd = d_old + d
    else: # 大于90度，反向
        if d_old < 0:
            dd = d_old + d
        else:
            dd = d_old - d
    trans = False
    if dd < 0:
        dd = abs(dd)
        if d_old > 0:
            trans = True
    while dd > 2:
        dd = dd - 2
        trans = not trans
    vec_new = vec_old
    clear = True
    if trans:
        vec_new = (-1 * np.array(vec_old)).tolist()
        clear = False
    if dd<=1:
        far = False
    else:
        dd =  2 - dd
        far = True
    if d_old != 0:
        if clear:
            dd = dd * (d_old/abs(d_old))
        else:
            dd = dd * (d_old/abs(d_old)) * (-1)
    if d_old * dd < 0:
        far = True
    else:
        far = False
    return (vec_new, dd), far

def trans_line(line, d):
    # 将线段向左侧平移d距离
    # 读取原先参数
    p_a = line[0] # a点坐标
    p_b = line[1] # b点坐标
    c_o = line[2][0] # 圆心向量
    # 计算移动后的小圆
    v_ab = np.cross(np.array(p_a), np.array(p_b))
    (c_n_o, c_n_d), is_far = get_out_circle(v_ab.tolist(), line[2], d)
    c_n = (c_n_o, c_n_d)
    # 计算过A点的大圆
    vec_a = np.cross(np.array(p_a),np.array(c_o))
    c_a_n = (vec_a.tolist(), 0)
    # 计算过B点的大圆
    vec_b = np.cross(np.array(p_b),np.array(c_o))
    c_b_n = (vec_b.tolist(), 0)
    # 小圆圆心在球上
    if c_n_d == 1.0:
        # 判断小圆是否在两个大圆上
        _ve = np.dot(np.array(c_n_o), vec_a) + np.dot(np.array(c_n_o), vec_b)
        if 0.0 == _ve:
            return (c_n_o, c_n_o, c_n)
    # 计算大圆A和小圆的交点
    res1 = geodesic_buffer.caculate_points_cir(c_a_n, c_n)
    if res1[0] == 0:
        return 'error'
    elif res1[0] == 1:
        P_1 = res1[1][0]
    else:
        p1 = res1[1][0]
        p2 = res1[1][1]
        # 判断舍弃的point
        th1 = np.dot(np.array(p_a), np.array(p1))/(np.linalg.norm(np.array(p_a)) *np.linalg.norm(np.array(p1)))
        th2 = np.dot(np.array(p_a), np.array(p2))/(np.linalg.norm(np.array(p_a)) *np.linalg.norm(np.array(p2)))
        if not is_far:
            if th1 > th2:
                P_1 = p1
            else:
                P_1 = p2
        else:
            if th1 < th2:
                P_1 = p1
            else:
                P_1 = p2
    # 计算大圆B和小圆的交点
    res2 = geodesic_buffer.caculate_points_cir(c_b_n, c_n)
    if res2[0] == 0:
        return 'error'
    elif res2[0] == 1:
        P_2 = res2[1][0]
    else:
        p1 = res2[1][0]
        p2 = res2[1][1]
        # 判断舍弃的point
        th1 = np.dot(np.array(p_a), np.array(p1))/(np.linalg.norm(np.array(p_a)) *np.linalg.norm(np.array(p1)))
        th2 = np.dot(np.array(p_a), np.array(p2))/(np.linalg.norm(np.array(p_a)) *np.linalg.norm(np.array(p2)))
        if not is_far:
            if th1 > th2:
                P_2 = p1
            else:
                P_2 = p2
        else:
            if th1 < th2:
                P_2 = p1
            else:
                P_2 = p2
    res = (P_1, P_2, c_n)
    res = clear_lines(res)
    # print(f'{line}-->{res}')
    return res


def merge_line(area_list):
    # 合并整理相交的线段
    # 首先过滤掉长度为0的线段
    results = []
    for i in range(len(area_list)-1, -1, -1):
        if area_list[i][0] == area_list[i][1]:
            del area_list[i]
    while True:
        area_list_copy = area_list.copy()
        i = 0
        while i < len(area_list):
            now_line = area_list[i]
            for j in range(i+1,len(area_list)):
                if j >= len(area_list):
                    break
                need_line = area_list[j]
                (ret, res) = geodesic_buffer.caculate_points(now_line,need_line)
                if ret == 0: # 不相交
                    continue
                if ret == 2: # 两个交点随机取第一个
                    res = res[0]
                if isinstance(res, (list, tuple)) and len(res) == 3:
                    point = (res[0], res[1], res[2])
                else:
                    raise ValueError(f"Error: res 不是一个包含三个元素的可迭代对象，res = {res}")
                dis_in = abs(i - j) - 1 # 内部距离
                dis_out = len(area_list) - 2 - dis_in # 外部距离
                dis_all = min(dis_in, dis_out) # 最小距离
                area_list[j] = list(area_list[j])
                area_list[i] = list(area_list[i])
                if dis_all == 0: # 间隔为0，直接改变端点
                    if dis_in == 0: # 内部为0
                        area_list[i][1] = point
                        area_list[j][0] = point
                    elif dis_out == 0: # 外部为0
                        area_list[i][0] = point
                        area_list[j][1] = point
                elif dis_all < 3: # 间隔0~3，无需裂变，删除间隔
                    if dis_in < dis_out: # 删除内部
                        area_list = area_list[:i+1] + area_list[j:]
                        area_list[i][1] = point
                        area_list[i+1][0] = point
                    elif dis_in > dis_out: # 删除外部
                        area_list = area_list[i:j+1]
                        area_list[0][0] = point
                        area_list[len(area_list)-1][1] = point
                    else: # 相等再次判断
                        # area_list = area_list[:i+1] + area_list[j:]
                        # area_list[i][1] = point
                        # area_list[i+1][0] = point

                        # area_list = area_list[i:j+1]
                        # area_list[0][0] = point
                        # area_list[len(area_list)-1][1] = point

                        points_extend_in = 0
                        for kk in range(i+1,j):
                            if abs(area_list[kk][2][1]) > 0.9:
                                points_extend_in += 1
                        points_extend_out = 0
                        for kk in range(0,i):
                            if abs(area_list[kk][2][1]) > 0.9:
                                points_extend_out += 1
                        for kk in range(j,len(area_list)):
                            if abs(area_list[kk][2][1]) > 0.9:
                                points_extend_out += 1
                        if points_extend_out == 1:
                            area_list = area_list[i:j+1]
                            area_list[0][0] = point
                            area_list[len(area_list)-1][1] = point
                        elif points_extend_in == 1:
                            area_list = area_list[:i+1] + area_list[j:]
                            area_list[i][1] = point
                            area_list[i+1][0] = point
                        else:
                            if points_extend_out < points_extend_in:
                                area_list = area_list[:i+1] + area_list[j:]
                                area_list[i][1] = point
                                area_list[i+1][0] = point
                            else:
                                area_list = area_list[i:j+1]
                                area_list[0][0] = point
                                area_list[len(area_list)-1][1] = point
                else: # 间隔大于3，需要裂变
                    area_list_zreo = area_list[i:j+1]
                    area_list_zreo[0][0] = point
                    area_list_zreo[len(area_list_zreo)-1][1] = point



                    area_list_one = area_list[:i+1] + area_list[j:]
                    area_list_one[i][1] = point
                    area_list_one[i+1][0] = point


                    # area_list[i][1] = point
                    # area_list[j][0] = point
                    

                    # return [area_list_one,area_list_zreo]
                    k0 = merge_line(area_list_zreo)
                    k1 = merge_line(area_list_one)
                    for k in k0:
                        results.append(k)
                    for k in k1:
                        results.append(k)
                    return results
            i = i+1
        if area_list_copy == area_list:
            break
    for i in range(len(area_list)-1, -1, -1):
        if area_list[i][0] == area_list[i][1]:
            del area_list[i]
    results.append(area_list)
    return results

def extend(area_list,distance):
    # 区域大小拓展
    # area_list:原区域构成(使用线段描述)
    # distance:需要拓展的距离
    area_list_new = []
    # 拓展原有线段
    for l in area_list:
        n_l = trans_line(l, distance)
        if n_l == 'error':
            return ('error', f'error in trans_line:{l}, {distance})')
        area_list_new.append(n_l)
    # return ('ok', area_list_new)
    # 增加新线段
    area_list_new2 = []
    for i in range(0,len(area_list_new)-1,1):
        area_list_new2.append(area_list_new[i])
        p_1 = area_list_new[i][1]
        p_2 = area_list_new[i+1][0]
        if p_1 != p_2:
            p = area_list[i][1]
            n_l = export_point(p_1,p_2,p)
            area_list_new2.append(n_l)
    area_list_new2.append(area_list_new[len(area_list_new)-1])
    p_1 = area_list_new[len(area_list_new)-1][1]
    p_2 = area_list_new[0][0]
    if p_1 != p_2:
        p = area_list[0][0]
        n_l = export_point(p_1,p_2,p)
        area_list_new2.append(n_l)
    # return ('ok', [area_list_new2])
    area = merge_line(area_list_new2)
    return ('ok', area)

    