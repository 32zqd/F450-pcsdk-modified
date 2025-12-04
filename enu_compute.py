import pyproj
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建WGS84到ECEF的转换器
transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)

# 基站原点 (北京天安门)
lat_origin, lon_origin, alt_origin = 39.9042, 116.4074, 0
X0, Y0, Z0 = transformer.transform(lon_origin, lat_origin, alt_origin)   # 基站原点 ECEF
print(f"原点ECEF坐标: X={X0:.2f}, Y={Y0:.2f}, Z={Z0:.2f}")

# 目标位置
lat_target, lon_target, alt_target = 39.9042, 116.4073, 60
X_target, Y_target, Z_target = transformer.transform(lon_target, lat_target, alt_target)   # 目标位置 ECEF
print(f"目标ECEF坐标: X={X_target:.2f}, Y={Y_target:.2f}, Z={Z_target:.2f}")

# ECEF到ENU坐标转换函数
def ecef_to_enu(x, y, z, lat0, lon0, alt0):
    """
    将ECEF坐标转换为ENU坐标
    """
    # 转换为弧度
    lat0_rad = np.radians(lat0)
    lon0_rad = np.radians(lon0)
    
    # 计算相对于原点的ECEF坐标差
    dx = x - X0
    dy = y - Y0
    dz = z - Z0
    
    # ENU转换矩阵
    sin_lat = np.sin(lat0_rad)
    cos_lat = np.cos(lat0_rad)
    sin_lon = np.sin(lon0_rad)
    cos_lon = np.cos(lon0_rad)
    
    # 转换到ENU坐标系
    east = -sin_lon * dx + cos_lon * dy
    north = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
    up = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
    
    return east, north, up

# 计算目标位置的ENU坐标
east_target, north_target, up_target = ecef_to_enu(X_target, Y_target, Z_target, lat_origin, lon_origin, alt_origin)
print(f"目标ENU坐标: East={east_target:.2f}, North={north_target:.2f}, Up={up_target:.2f}")

# 创建3D图形
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# 绘制基站原点 (ENU坐标系原点)
ax.scatter(0, 0, 0, c='red', s=100, marker='o', label='Base Station (Origin)')

# 绘制目标位置
ax.scatter(east_target, north_target, up_target, c='blue', s=100, marker='^', label='Target Position')

# 绘制ENU坐标系轴
axis_length = max(abs(east_target), abs(north_target), abs(up_target)) * 0.8

# East轴 (红色)
ax.plot([0, axis_length], [0, 0], [0, 0], 'r-', linewidth=3, label='East Axis')
ax.text(axis_length*1.1, 0, 0, 'East', fontsize=12, color='red')

# North轴 (绿色)
ax.plot([0, 0], [0, axis_length], [0, 0], 'g-', linewidth=3, label='North Axis')
ax.text(0, axis_length*1.1, 0, 'North', fontsize=12, color='green')

# Up轴 (蓝色)
ax.plot([0, 0], [0, 0], [0, axis_length], 'b-', linewidth=3, label='Up Axis')
ax.text(0, 0, axis_length*1.1, 'Up', fontsize=12, color='blue')

# 绘制从原点到目标的连线
ax.plot([0, east_target], [0, north_target], [0, up_target], 'k--', alpha=0.6, linewidth=2, label='Distance Vector')

# 设置坐标轴标签
ax.set_xlabel('East (m)', fontsize=12)
ax.set_ylabel('North (m)', fontsize=12)
ax.set_zlabel('Up (m)', fontsize=12)

# 设置标题
ax.set_title('ENU坐标系下基站与目标位置关系', fontsize=14, fontweight='bold')

# 设置图例
ax.legend(loc='upper right')

# 设置坐标轴等比例
max_range = max(abs(east_target), abs(north_target), abs(up_target))
ax.set_xlim([-max_range*0.2, max_range*1.2])
ax.set_ylim([-max_range*0.2, max_range*1.2])
ax.set_zlim([0, max_range*1.2])

# 添加网格
ax.grid(True, alpha=0.3)

# 显示距离信息
distance = np.sqrt(east_target**2 + north_target**2 + up_target**2)
ax.text2D(0.02, 0.98, f'Distance: {distance:.2f} m\nEast: {east_target:.2f} m\nNorth: {north_target:.2f} m\nUp: {up_target:.2f} m', 
          transform=ax.transAxes, fontsize=10, verticalalignment='top',
          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.show()