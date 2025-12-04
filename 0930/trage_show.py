import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv

X = []
Y = []
Z = []

with open('gps_recording.csv', 'r', newline='', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    # 读取标题行
    header = next(csv_reader)
    print(f'列名: {header}')
    
    # 逐行读取数据
    for row in csv_reader:
        X.append(float(row[0]))
        Y.append(float(row[1]))
        Z.append(float(row[2]))

# 将列表转换为numpy数组
X = np.array(X)
Y = np.array(Y)
Z = np.array(Z)


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot(X, Y, Z)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Plot')

plt.show()
