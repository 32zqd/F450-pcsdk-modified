import pandas as pd
import folium

# 读取CSV文件
df = pd.read_csv("gps_trajectory_complete.csv")

# 提取经纬度，取中点作为地图中心
center_lat = (df["latitude"].min() + df["latitude"].max()) / 2
center_lon = (df["longitude"].min() + df["longitude"].max()) / 2

# 创建地图对象（初始缩放级别18，可根据轨迹范围调整）
m = folium.Map(location=[center_lat, center_lon], zoom_start=18)

# 添加轨迹线
points = list(zip(df["latitude"], df["longitude"]))
folium.PolyLine(points, color="blue", weight=3, opacity=0.7, tooltip="飞行轨迹").add_to(m)

# 标记起飞点和降落点
folium.Marker(
    location=[df["latitude"].iloc[0], df["longitude"].iloc[0]],
    popup="起飞点",
    icon=folium.Icon(color="red", icon="plane")
).add_to(m)

folium.Marker(
    location=[df["latitude"].iloc[-1], df["longitude"].iloc[-1]],
    popup="降落点",
    icon=folium.Icon(color="green", icon="flag")
).add_to(m)

# 保存地图为HTML文件
m.save("trajectory_map.html")
print("地图已保存为 trajectory_map.html，可在浏览器中打开查看")