import unittest
from esc import point_distance
from esc import point_to_segment_distance

class TestCoreFunctions(unittest.TestCase):
    def test_point_distance(self):
        # 测试赤道上的两点
        self.assertAlmostEqual(point_distance((0,0), (1,0)), 111319.5, delta=100)
        # 测试南北极
        self.assertAlmostEqual(point_distance((0,90), (0,-90)), 20003931.5, delta=1000)
        # 测试无效method参数
        with self.assertRaises(ValueError):
            point_distance((0,0), (0,0), method='invalid')

    def test_point_segment_distance(self):
        # 测试在线段上的点
        line = [(116.3975, 39.9087), (121.4737, 31.2304)]
        self.assertAlmostEqual(point_to_segment_distance(line[0], line), 0, delta=1)
        # 测试经度越界
        with self.assertRaises(ValueError):
            point_to_segment_distance((190, 50), line)
        # 测试纬度越界
        with self.assertRaises(ValueError):
            point_to_segment_distance((120, 100), line)

if __name__ == '__main__':
    unittest.main()