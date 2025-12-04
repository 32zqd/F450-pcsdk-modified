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
lat_target, lon_target, alt_target = 39.9042, 116.4075, 50
X1, Y1, Z1 = transformer.transform(lon_target, lat_target, alt_target)   # 目标位置 ECEF
print(f"目标ECEF坐标: X={X1:.2f}, Y={Y1:.2f}, Z={Z1:.2f}")

# 计算相对于原点的xyz坐标
dx = X1 - X0  # 东向
dy = Y1 - Y0  # 北向  
dz = Z1 - Z0  # 上向

print(f"相对坐标: dx={dx:.2f}m, dy={dy:.2f}m, dz={dz:.2f}m")

# 创建3D可视化
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 绘制原点
ax.scatter(0, 0, 0, color='red', s=100, label='原点 (天安门)', marker='o')

# 绘制目标点
ax.scatter(dx, dy, dz, color='blue', s=100, label='目标位置', marker='^')

# 绘制连接线
ax.plot([0, dx], [0, dy], [0, dz], 'g--', alpha=0.7, linewidth=2)

# 绘制原点的xyz坐标轴
axis_length = max(abs(dx), abs(dy), abs(dz)) * 0.5  # 坐标轴长度

# X轴 (东向) - 红色
ax.plot([0, axis_length], [0, 0], [0, 0], 'r-', linewidth=3, label='X-axis (East)')
ax.text(axis_length*1.1, 0, 0, 'X', fontsize=12, color='red', fontweight='bold')

# Y轴 (北向) - 绿色  
ax.plot([0, 0], [0, axis_length], [0, 0], 'g-', linewidth=3, label='Y-axis (North)')
ax.text(0, axis_length*1.1, 0, 'Y', fontsize=12, color='green', fontweight='bold')

# Z轴 (上向) - 蓝色
ax.plot([0, 0], [0, 0], [0, axis_length], 'b-', linewidth=3, label='Z-axis (Up)')
ax.text(0, 0, axis_length*1.1, 'Z', fontsize=12, color='blue', fontweight='bold')

# 设置坐标轴标签
ax.set_xlabel('East (m)', fontsize=12)
ax.set_ylabel('North (m)', fontsize=12)
ax.set_zlabel('Up (m)', fontsize=12)

# 设置标题
ax.set_title('3D位置可视化\n(原点: 天安门, 目标: +50m高度)', fontsize=14)

# 添加图例
ax.legend()

# 设置坐标轴范围，确保能看到所有点
max_range = max(abs(dx), abs(dy), abs(dz)) * 1.2
ax.set_xlim([-max_range, max_range])
ax.set_ylim([-max_range, max_range])
ax.set_zlim([0, max_range])

# 添加网格
ax.grid(True, alpha=0.3)

# 显示图形
plt.tight_layout()
plt.show()