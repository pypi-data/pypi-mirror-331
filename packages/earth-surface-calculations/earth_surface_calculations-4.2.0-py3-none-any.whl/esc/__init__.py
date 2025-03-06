"""
关于地球球面几何的计算
~~~~~~~~~~~~~~~~~~~~~~~~~
导入模块:
   >>> import esc
计算两点之间的距离:
   >>> esc.point_distance(point1, point2, method='haversine')
计算点到线段的距离:
   >>> esc.point_to_segment_distance(line, point)
计算轨迹的距离:
   >>> esc.trajectory_distance(traj1, traj2, metric='hausdorff', **kwargs)
插值轨迹:
   >>> esc.trajectory_interpolation(traj, length)
稀释轨迹（按距离）:
   >>> esc.trajectory_simplify(traj, tolerance)
稀释轨迹（按点数）:
   >>> esc.trajectory_dilution(traj, count)
扩展区域:
   >>> esc.area_extend(area, distance)
"""

from .point_distance import point_distance
from .point_segment import point_to_segment_distance
from .trajectory_distance import trajectory_distance
from .trajectory_process import trajectory_interpolation, trajectory_simplify, trajectory_dilution
from .area_extend import area_extend

__all__ = [
    'point_distance',
    'point_to_segment_distance',
    'trajectory_dilution',
    'trajectory_interpolation',
    'trajectory_simplify',
    'trajectory_distance',
    'area_extend'
]
