# 测试代码
import numpy as np
from extend_main import points2points
from translate import vectopoint

def plot_globe(a,b,c,r,dense=1000):
    t1=np.linspace(0,np.pi,dense)
    t2=np.linspace(0,np.pi*2,dense)
    t1,t2=np.meshgrid(t1,t2)
    x=a+r*np.sin(t1)*np.cos(t2)
    y=b+r*np.sin(t1)*np.sin(t2)
    z=c+r*np.cos(t1)
    return x,y,z


def points_to_xyz(points):
    point_new = []
    for p in points:
        point_new.append(vectopoint(p))
    all_points = []
    for i in point_new:
        if i not in all_points:
            all_points.append(i)
    x = []
    y = []
    z = []
    for k in all_points:
        x.append(k[0])
        y.append(k[1])
        z.append(k[2])
    x.append(x[0])
    y.append(y[0])
    z.append(z[0])
    return x,y,z

if __name__ == '__main__':
    d = 100
    # points0 = [(29.9196242,-17.9848621),(14.4809086,-21.8950647),(22.2545412,-24.5452473),
    #         (12.4752538,-30.9500536),(13.7087707,-22.1720298),
    #         (4.5905515,-37.6918250),(20.9409868,-37.6691432)]
    # points0 = [(10.4366604, 26.6844217), (12.4763377, 40.1007597),(4.3476407, 37.4251972),
    #            (11.1167429, 36.7006615), (5.8170143, 34.5482610),(8.1517150, 29.6110603),(1.7449093, 30.7261102),
    #            (4.9698729, 34.8465099),(-2.92653205, 32.6375112),(3.5226976,36.8887275),(-10.6984455,32.2419939)]
    # points0 = [(10.4366604, 26.6844217), (12.4763377, 40.1007597),(-10.6984455,32.2419939)]
    decimalCoordinates = [
        [30.111411, 122.182999],
        [30.112284, 122.184193],
        [30.112541, 122.184358],
        [30.113281, 122.184175],
        [30.115016, 122.183269],
        [30.114833, 122.182806],
        [30.113103, 122.183709],
        [30.112546, 122.184100],
        [30.112396, 122.184023],
        [30.111543, 122.182856],
        [30.111478, 122.182929]
    ]
    # # decimalCoordinates = decimalCoordinates[::-1]
    # lat, lon = zip(*decimalCoordinates)
    points0 = decimalCoordinates# list(zip(lon, lat))
    points1 = points2points(points0, d)
    # points2 = points2points(points1, d)
    print(points1)

    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    # 定义坐标系
    fig = plt.figure(1)
    ax = fig.add_axes(Axes3D(fig))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # 绘制球面
    x,y,z = plot_globe(a=0,b=0,c=0,r=1)
    ax.plot_surface(x,y,z,color="b",alpha=0.3)
    # 绘制原先的曲线
    x,y,z = points_to_xyz(points0)
    ax.plot(x, y, z, c='g')
    # 绘制拓展后曲线
    for p in points1:
        x,y,z = points_to_xyz(p)
        ax.plot(x, y, z, c='r')
    # 绘制二次拓展后曲线
    # x,y,z = points_to_xyz(points1[1])
    # ax.plot(x, y, z, c='y')
    plt.show()
