# 圆交点计算
import math
from .translate import pointtovect, vectopoint

R_0 = 1

class CircleOnSphere(object):
    def __init__(self, direct, d:float, R=R_0) -> None:
        self.d = d
        self.R = R
        self.direct = direct
        self.r = 0
        self.e = None
        self.calcInit()
        pass
    
    def calcInit(self):
        ''''''
        self.r = math.sqrt(abs(math.pow(self.R, 2)-math.pow(self.d, 2)))
        theta, phi = self.direct
        self.e = [math.cos(phi)*math.cos(theta), math.cos(phi)*math.sin(theta), math.sin(phi)]
    
    def dot(self, vec1, vec2, dms=3):
        rst = 0
        for i in range(dms):
            rst += vec1[i]*vec2[i]
        return rst
    
    def add(self, vec1, vec2):
        ''''''
        return [i+j for i, j in zip(vec1, vec2)]
    
    def cross(self, vec1, vec2):
        ''''''
        return [vec1[(i+1)%3]*vec2[(i+2)%3]-vec1[(i+2)%3]*vec2[(i+1)%3] for i in range(3)]
    
    def norm(self, vec):
        ''''''
        m = self.model(vec) + 1e-10
        return [i/m for i in vec]
    
    def coefficient(self, co, vec):
        ''''''
        return [co*i for i in vec]
    
    def model(self, vec):
        ''''''
        rst = 0
        for i in vec:
            rst += i**2
        return math.sqrt(rst)
    
    def RTP_XYZ(self, RTP, radiansFlag=True):
        ''''''
        R, T, P = RTP
        if not radiansFlag:
            T = math.radians(T)
            P = math.radians(P)
        return [R*math.cos(P)*math.cos(T), R*math.cos(P)*math.sin(T), R*math.sin(P)]
    
    def XYZ_RTP(self, XYZ, radiansFlag=True):
        ''''''
        X, Y, Z = XYZ
        P = math.atan2(Z, math.sqrt(X**2+Y**2))
        T = math.atan2(Y, X)
        R = math.sqrt(X**2+Y**2+Z**2)
        if not radiansFlag:
            T = math.degrees(T)
            P = math.degrees(P)
        return [R, T, P]
        
    def crossPoints(self, other):
        ''''''
        a_dot_b = self.dot(self.e, other.e)
        if abs(a_dot_b)==1:
            return False, None
        m = (self.d-other.d*a_dot_b)/(1-math.pow(a_dot_b, 2))
        n = (other.d-self.d*a_dot_b)/(1-math.pow(a_dot_b, 2))
        
        c_ = self.add(self.coefficient(m, self.e), self.coefficient(n, other.e))
        c_model = self.model(c_)
        
        l_ = None
        if c_model>self.R:
            return False, None
        else:
            l_ = math.sqrt(self.R**2-c_model**2)
        
        d_ = self.norm(self.cross(self.e, other.e))
        
        return True, [self.XYZ_RTP(self.add(c_, self.coefficient(l_, d_))), 
                      self.XYZ_RTP(self.add(c_, self.coefficient(-l_, d_)))]


def vecOp(vec1, op, vec2):
    if op=='+':
        return [i+j for i, j in zip(vec1, vec2)]
    elif op=='-':
        return [i-j for i, j in zip(vec1, vec2)]
    elif op=='·':
        sum = 0
        for i, j in zip(vec1, vec2):
            sum += i*j
        return sum
    elif op=='X':
        x1, y1, z1 = vec1
        x2, y2, z2 = vec2
        return [y1*z2-y2*z1, z1*x2-z2*x1, x1*y2-x2*y1]
    elif op=='*':
        return [i*vec2 for i in vec1]
    else:
        print('error')

class SegmentOnSphere(object):
    def __init__(self, pBgn, pEnd, direct, d:float, R=R_0) -> None:
        self.pBgn = pBgn
        self.pEnd = pEnd
        self.direct = direct
        self.d = d
        self.R = R
        self.COS = CircleOnSphere(self.direct, d)
        self.bgn = self.RTP_XYZ((self.R, pBgn[0], pBgn[1]))
        self.end = self.RTP_XYZ((self.R, pEnd[0], pEnd[1]))
        
        pass
    
    def checkIfCorrect(self):
        pass
    
    
    def RTP_XYZ(self, RTP, radiansFlag=True):
        ''''''
        R, T, P = RTP
        if not radiansFlag:
            T = math.radians(T)
            P = math.radians(P)
        return [R*math.cos(P)*math.cos(T), R*math.cos(P)*math.sin(T), R*math.sin(P)]
    
    
    def XYZ_RTP(self, XYZ, radiansFlag=True):
        ''''''
        X, Y, Z = XYZ
        P = math.atan2(Z, math.sqrt(X**2+Y**2))
        T = math.atan2(Y, X)
        R = math.sqrt(X**2+Y**2+Z**2)
        if not radiansFlag:
            T = math.degrees(T)
            P = math.degrees(P)
        return [R, T, P]
    
    def checkPointOnSegment(self, point):
        p = self.RTP_XYZ((self.R, point[0], point[1]))
        tmp = vecOp(vecOp(self.end, '-', p), 'X', vecOp(self.bgn, '-', p))
        tmp2 = vecOp(tmp, '·', self.COS.e)
        # 检查 tmp2 是否为有效的数值
        if isinstance(tmp2, (int, float)) and tmp2 >= 0:
            return True
        return False
    
    def crossPoint(self, other):
        ret, cps = self.COS.crossPoints(other.COS)
        if not ret:
            return False, None
        rst = []
        # 检查 cps 是否为 None
        if cps is not None:
            for cp in cps:
                cp = cp[1:]
                if self.checkPointOnSegment(cp) and other.checkPointOnSegment(cp):
                    rst.append(cp)
        
        if len(rst)>0:
            return True, rst
        return False, None
    

def RTP_XYZ(RTP):
    R, T, P = RTP
    X = R*math.cos(P)*math.cos(T)
    Y = R*math.cos(P)*math.sin(T)
    Z = R*math.sin(P)
    if abs(X) < 1e-5:
        X = 0
    if abs(Y) < 1e-5:
        Y = 0
    if abs(Z) < 1e-5:
        Z = 0
    return [X, Y, Z]


def caculate_points(area1, area2):
    # 弧度制，前面是经度
    p1_1 = pointtovect(area1[0])
    p1_2 = pointtovect(area1[1])
    p1_0 = pointtovect(area1[2][0])
    p2_1 = pointtovect(area2[0])
    p2_2 = pointtovect(area2[1])
    p2_0 = pointtovect(area2[2][0])

    p1_1 = (math.radians(p1_1[1]), math.radians(p1_1[0]))
    p1_2 = (math.radians(p1_2[1]), math.radians(p1_2[0]))
    p1_0 = (math.radians(p1_0[1]), math.radians(p1_0[0]))
    p2_1 = (math.radians(p2_1[1]), math.radians(p2_1[0]))
    p2_2 = (math.radians(p2_2[1]), math.radians(p2_2[0]))
    p2_0 = (math.radians(p2_0[1]), math.radians(p2_0[0]))

    d1 = area1[2][1]
    d2 = area2[2][1]

    SOS_1 = SegmentOnSphere(p1_1, p1_2, p1_0, d1)
    SOS_2 = SegmentOnSphere(p2_1, p2_2, p2_0, d2)
    result = SOS_1.crossPoint(SOS_2)

    if result[0] == True:
        if len(result[1]) == 1:
            kk = (math.degrees(result[1][0][1]), math.degrees(result[1][0][0]))
            res = vectopoint(kk)
            if res == p1_2 and res == p2_1:
                return (0, '')
            return (1, (res))
        else:
            kk1 = (math.degrees(result[1][0][1]), math.degrees(result[1][0][0]))
            res1 = vectopoint(kk1)
            kk2 = (math.degrees(result[1][1][1]), math.degrees(result[1][1][0]))
            res2 = vectopoint(kk2)
            if res1 == res2:
                if res1 == p1_2 and res1 == p2_1:
                    return (0, '')
                return (1, (res1))
            if res1 == p1_2 and res1 == p2_1:
                return (1, (res2))
            if res2 == p1_2 and res2 == p2_1:
                return (1, (res1))
            return (2, (res1, res2))
    return (0, '')


def caculate_points_cir(c1, c2):
    # 弧度制，前面是经度
    c1_d = c1[1]
    c2_d = c2[1]
    c1_v = pointtovect(c1[0])
    c2_v = pointtovect(c2[0])

    # c1_v = (round((math.radians(c1_v[1])),5), round((math.radians(c1_v[0])),5))
    # c2_v = (round((math.radians(c2_v[1])),5), round((math.radians(c2_v[0])),5))

    c1_v = (math.radians(c1_v[1]), math.radians(c1_v[0]))
    c2_v = (math.radians(c2_v[1]), math.radians(c2_v[0]))

    COS_1 = CircleOnSphere(c1_v, c1_d)
    COS_2 = CircleOnSphere(c2_v, c2_d)

    result = COS_1.crossPoints(COS_2)
    if result[0] == True:
        if len(result[1]) == 1:
            res = RTP_XYZ(result[1][0])
            return (1, (res))
        else:
            res1 = RTP_XYZ(result[1][0])
            res2 = RTP_XYZ(result[1][1])
            if res1 == res2:
                return (1, (res1))
            return (2, (res1, res2))
    return (0,'')

