from .point_distance import point_distance
from scipy.spatial import KDTree

def _dtw_distance(traj_a, traj_b):
    """
    动态时间规整算法实现（滚动数组优化）
    时间复杂度O(n*m) 空间复杂度O(min(n,m))
    """
    m, n = len(traj_a), len(traj_b)
    if m > n:
        traj_a, traj_b = traj_b, traj_a
        m, n = n, m

    prev = [0.0] * (n + 1)
    for j in range(1, n+1):
        prev[j] = prev[j-1] + point_distance(traj_a[0], traj_b[j-1])

    for i in range(1, m+1):
        curr = [float('inf')] * (n + 1)
        curr[0] = float('inf')
        for j in range(1, n+1):
            cost = point_distance(traj_a[i-1], traj_b[j-1])
            curr[j] = cost + min(prev[j], prev[j-1])
        prev = curr

    return prev[n]


def _frechet_distance(traj_a, traj_b):
    """
    Fréchet距离计算（动态规划+空间压缩）
    时间复杂度O(nm) 空间复杂度O(n)
    """
    m, n = len(traj_a), len(traj_b)
    dp = [float('inf')] * (n + 1)
    
    for i in range(m+1):
        new_dp = [float('inf')] * (n + 1)
        for j in range(n+1):
            if i == 0 and j == 0:
                new_dp[j] = point_distance(traj_a[0], traj_b[0])
            elif i > 0 and j > 0:
                cost = point_distance(traj_a[i-1], traj_b[j-1])
                new_dp[j] = max(min(dp[j], dp[j-1], new_dp[j-1]), cost)
            # 边界条件处理
            elif i > 0:
                new_dp[j] = max(dp[j], point_distance(traj_a[i-1], traj_b[j-1]))
            elif j > 0:
                new_dp[j] = max(new_dp[j-1], point_distance(traj_a[i-1], traj_b[j-1]))
        dp = new_dp
    
    return dp[n]


def _directed_hausdorff(traj_a, traj_b):
    def compute_nearest_distances(points, tree):
        max_distance = 0
        max_index = (-1, -1)
        for i, point in enumerate(points):
            distance, j = tree.query(point)
            if distance > max_distance:
                max_distance = distance
                max_index = (i, int(j))
        return max_distance, max_index

    tree_B = KDTree(traj_b)
    tree_A = KDTree(traj_a)
    
    d_A_to_B, i_A_to_B = compute_nearest_distances(traj_a, tree_B)
    d_B_to_A, i_B_to_A = compute_nearest_distances(traj_b, tree_A)

    if d_A_to_B > d_B_to_A:
        idm = point_distance(traj_a[i_A_to_B[0]], traj_b[i_A_to_B[1]])  
    else:
        idm = point_distance(traj_a[i_B_to_A[1]], traj_b[i_B_to_A[0]])

    return idm


def _mean_distance(traj_a, traj_b):
    total = 0
    count = 0
    for p1 in traj_a:
        for p2 in traj_b:
            total += point_distance(p1, p2)
            count += 1
    return total / count if count > 0 else 0

def _lcss_distance(traj_a, traj_b, epsilon):
    """
    LCSS相似度计算（空间优化版）
    时间复杂度O(nm) 空间复杂度O(min(n,m))
    """
    m, n = len(traj_a), len(traj_b)
    if m < n:
        traj_a, traj_b = traj_b, traj_a
        m, n = n, m
    original_min = min(m, n)

    prev = [0] * (n + 1)
    for i in range(1, m+1):
        curr = [0] * (n + 1)
        for j in range(1, n+1):
            if point_distance(traj_a[i-1], traj_b[j-1]) <= epsilon:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev = curr
    return prev[n] / original_min


def _edr_distance(traj_a, traj_b, epsilon):
    """
    编辑距离实时计算（滚动数组优化）
    时间复杂度O(nm) 空间复杂度O(min(n,m))
    """
    m, n = len(traj_a), len(traj_b)
    if m > n:
        traj_a, traj_b = traj_b, traj_a
        m, n = n, m

    prev = list(range(n+1))
    for i in range(1, m+1):
        curr = [i] + [0]*n
        for j in range(1, n+1):
            cost = 0 if point_distance(traj_a[i-1], traj_b[j-1]) <= epsilon else 1
            curr[j] = min(prev[j]+1, curr[j-1]+1, prev[j-1]+cost)
        prev = curr
    return prev[n]


def _owd_distance(traj_a, traj_b):
    """
    单向距离计算（One Way Distance）
    时间复杂度O(nm) 空间复杂度O(1)
    """
    total = 0
    for p in traj_a:
        min_dist = min(point_distance(p, q) for q in traj_b)
        total += min_dist
    return total / len(traj_a)


def _lip_distance(traj_a, traj_b):
    """
    最长递增路径相似度（贪心优化）
    时间复杂度O(nlogn) 空间复杂度O(n)
    """
    from bisect import bisect_left
    
    pairs = sorted(
        [(point_distance(a, b), i, j) for i, a in enumerate(traj_a) for j, b in enumerate(traj_b)],
        key=lambda x: (x[1], x[0])
    )
    
    tails = []
    for d, i, j in pairs:
        idx = bisect_left(tails, (j, ))
        if idx == len(tails):
            tails.append((j, ))
        else:
            tails[idx] = (j, )
    return 1 - len(tails) / max(len(traj_a), len(traj_b))


def trajectory_distance(traj1, traj2, metric='hausdorff', **kwargs):
    """
    计算两条轨迹之间的空间距离
    
    参数:
    metric: 支持'lcss', 'edr', 'owd', 'lip', 'hausdorff', 'mean', 'dtw', 'frechet'
    kwargs: 不同算法需要的参数，如LCSS需要epsilon
    """
    match metric:
        case 'lcss':
            return _lcss_distance(traj1, traj2, kwargs.get('epsilon', 0.1))
        case 'edr':
            return _edr_distance(traj1, traj2, kwargs.get('epsilon', 0.1))
        case 'owd':
            return _owd_distance(traj1, traj2)
        case 'lip':
            return _lip_distance(traj1, traj2)
        case 'hausdorff':
            return max(_directed_hausdorff(traj1, traj2), _directed_hausdorff(traj2, traj1))
        case 'mean':
            return _mean_distance(traj1, traj2)
        case 'dtw':
            return _dtw_distance(traj1, traj2)
        case 'frechet':
            return _frechet_distance(traj1, traj2)
        case _:
            raise ValueError("不支持的度量方法，请使用'hausdorff'或'dtw'")
