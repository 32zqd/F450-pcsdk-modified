import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 关键：配置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]  # 适配不同系统的中文字体
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 读取CSV文件
df = pd.read_csv("gps_trajectory_complete.csv")

# 提取数据并转换为NumPy数组
lat = df["latitude"].to_numpy()
lon = df["longitude"].to_numpy()
alt = df["altitude"].to_numpy()

# 采样：每5个点取1个
sample_interval = 5
lat_sample = lat[::sample_interval]
lon_sample = lon[::sample_interval]
alt_sample = alt[::sample_interval]

# 绘制二维轨迹图
plt.figure(figsize=(10, 8))
scatter = plt.scatter(lon_sample, lat_sample, c=alt_sample, cmap="viridis", s=10)
plt.plot(lon, lat, color="blue", linewidth=1, alpha=0.5)
plt.scatter(lon[0], lat[0], color="red", s=100, label="起飞点", zorder=5)
plt.scatter(lon[-1], lat[-1], color="green", s=100, label="降落点", zorder=5)

# 添加颜色条
cbar = plt.colorbar(scatter)
cbar.set_label("相对高度 (m)")

# 图表设置（中文标签）
plt.xlabel("经度 (deg)")
plt.ylabel("纬度 (deg)")
plt.title("无人机圆形轨迹飞行图（采样优化）")
plt.legend()
plt.grid(True, alpha=0.3)
plt.axis("equal")
plt.savefig("trajectory_2d_sampled.png", dpi=300, bbox_inches="tight")
plt.show()