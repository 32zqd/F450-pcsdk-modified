#生成预期圆轨迹图，包含圆心和半径线，解决中文显示问题
import matplotlib.pyplot as plt
import numpy as np
import platform

# 解决中文显示问题 - 跨平台字体检测
def set_chinese_font():
    system = platform.system()
    if system == 'Windows':
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
    elif system == 'Darwin':  # macOS
        plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'STHeiti']
    else:  # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'DejaVu Sans']
    
    plt.rcParams['axes.unicode_minus'] = False

# 设置中文字体
set_chinese_font()

# 创建图形和坐标轴
fig, ax = plt.subplots(figsize=(8, 8))

# 圆形参数
center_x, center_y = 0, 0
radius = 5  # 半径5米

# 生成圆的坐标点
theta = np.linspace(0, 2 * np.pi, 100)
x = center_x + radius * np.cos(theta)
y = center_y + radius * np.sin(theta)

# 绘制圆形
ax.plot(x, y, color='blue', linewidth=2, label=f'圆形 (r={radius}m)')

# 绘制从圆心到x轴正方向的半径线（同色实线）
ax.plot([center_x, radius], [center_y, center_y], 
        color='blue', linewidth=2, linestyle='-')

# 绘制圆心点
ax.plot(center_x, center_y, 'ko', markersize=6)

# 设置图形属性
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.7)
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)

# 设置坐标轴范围
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

# 添加标签和标题
ax.set_xlabel('X 轴 (米)', fontsize=12)
ax.set_ylabel('Y 轴 (米)', fontsize=12)
ax.set_title('设定圆形轨迹', fontsize=14)
ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.show()