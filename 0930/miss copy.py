import asyncio
import math
from mavsdk.offboard import PositionNedYaw
from mavsdk import System, mission
import numpy as np
import matplotlib.pyplot as plt

# 全局变量
record_current_position = []

def  generate_position():
    center = np.array([1, 0, 2])
    radius = 10
    num_points = 100
    # Generate points for the circle in 3D
    theta = np.linspace(0, 2 * np.pi, num_points)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    z = np.full(num_points, center[2])
    return x,y,z

async def run():
    # 连接无人机
    drone = System()
    drone = System(mavsdk_server_address='localhost', port=50051)  #仿真需要注释，真机解开注释
    await drone.connect(system_address="udp://:14540")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"链接成功!")
            break
    async for att in drone.telemetry.attitude_euler():
        heading_deg = att.yaw_deg
        print(f"Current heading: {heading_deg} degrees")
        break
    #确保安全
    g,i=0,0
    while True:
        print("输入起飞高度") 
        g=int(input())
        print(g)
        if g > 0:
            pass
        else:
            print("数据无效")
        print("输入1起飞")
        i=int(input())
        print(i)
        if i==1:
            break
        else:
            print("重新输入")
    #打印GPS位置信息
    async for position in drone.telemetry.position():
        x = position.latitude_deg
        y = position.longitude_deg
        z = position.relative_altitude_m
        print(x,y,z)
        break
    #初始化变量，发布解锁起飞悬停命令
    x,y,z,s,time_1,yaw_1=0,0,0,-1,-1,-1
    await drone.action.set_takeoff_altitude(g)
    print("-- Arming")
    await drone.action.arm()
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(5)
    await asyncio.sleep(g)
    print("hold")
    # 创建航线任务，并添加航点，按q执行
    mission_items = []

    trajectory_x,trajectory_y,trajectory_z=generate_position()

    for ponit_num in range(len(trajectory_x)):

        input_str = input("输入X轴,Y轴,高度,速度，悬停时间，航向角\n(注意：高度为相对高度，输入负数意味着低于起飞高度,且需要两个航线任务)   空格隔开 ")
        try:
            x,y,z,s,time_1, yaw_1 = map(int, input_str.split( ))
            # x, y, z, s, time_1, yaw_1 = trajectory_x[ponit_num],trajectory_y[ponit_num],trajectory_z[ponit_num],1,1,1
        except ValueError:
            print("输入无效，请重试.")
            continue
        else:
            if x != 0 or y != 0 or z > 0 or s > 0 or time_1 > 0 or yaw_1 > 0:
                print(x,y,z,s,time_1,yaw_1)
                async for position in drone.telemetry.position():
                    x = position.latitude_deg + x / 111111.0
                    y = position.longitude_deg + y / 111111.0
                    z = position.relative_altitude_m + z
                    # print(x,y,z)
                    break
                # print("-- 保存")
                mission_items.append(mission.MissionItem(x, y, z, s, True, float('nan'), float('nan'), mission.MissionItem.CameraAction.NONE, time_1, 1.0,0,yaw_1,0))
                # print(mission_items)
                input_str = input("输入 回车继续，'q' 执行: ")
                if input_str == 'q':
                    break
    # 设置航线任务
    mission_plan = mission.MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_plan)
    
    await drone.mission.start_mission()

    # 实时打印当前位置信息
    async for position in drone.telemetry.position():
        x = round(position.latitude_deg,8) 
        y = round(position.longitude_deg,8) 
        z = round(position.relative_altitude_m,8) 
        record_current_position.append([x,y,z])
        print(x,y,z)

    # 监听任务执行的进度
    # async for progress in drone.mission.mission_progress():
    #     print(f"Mission progress: {progress.current}/{progress.total} tasks completed")
    #     if progress.current == progress.total:
    #         print("Mission completed!")
    #         break
    
    # 执行绘图操作，绘制飞行后的轨迹
    x_vals = [point[0] for point in record_current_position]
    y_vals = [point[1] for point in record_current_position]
    z_vals = [point[2] for point in record_current_position]
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(x_vals,y_vals,z_vals)
    plt.show()

    # 执行结束后，自动清除任务
    await drone.mission.clear_mission()
  
#执行程序
if __name__ == "__main__":
     #执行的第一种方法
    #asyncio.ensure_future()
    #asyncio.get_event_loop().run_forever()
    #执行的第二种方法
    asyncio.get_event_loop().run_until_complete(run()) 
