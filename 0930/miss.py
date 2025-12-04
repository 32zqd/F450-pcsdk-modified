import asyncio
import math
import numpy as np
import time
import threading
from mavsdk.offboard import PositionNedYaw
from mavsdk import System, mission

def generate_circle_points(radius,center=(0,0),num_points=20):
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)

    return x,y
async def run():
    # 连接无人机
    drone = System()
    drone = System(mavsdk_server_address='localhost', port=50051)  #仿真需要注释，真机解开注释
    await drone.connect(system_address="udp://:14540")

    # 等待连接
    print("等待连接...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"链接成功!")
            break

    async for att in drone.telemetry.attitude_euler():
        heading_deg = att.yaw_deg
        print(f"Current heading: {heading_deg} degrees")
        break

    g = 3  # 起飞高度
    i = 1  # 起飞指令

    # 打印GPS位置信息
    async for position in drone.telemetry.position():
        x = position.latitude_deg
        y = position.longitude_deg
        z = position.relative_altitude_m
        print(x, y, z)
        break

    # 初始化变量，发布解锁起飞悬停命令
    x, y, z, s, time_1, yaw_1 = 0, 0, 0, -1, -1, -1
    await drone.action.set_takeoff_altitude(g)
    print("-- Arming")
    await drone.action.arm()
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(5)

    # 等待飞机真正升到空中
    async for in_air in drone.telemetry.in_air():
        if in_air:
            print("In air!")
            break
        else :
            print("Not in air!")

    # await asyncio.sleep(g)
    print("hold")

    # 创建航线任务，并添加航点，按q执行
    # mission_items = []
    input_str_list = ['0,0,3,0.5,1,0',
                      '0,4,3,0.5,1,0',
                      ]
    input_str_list=[]
    mission_x,mission_y = generate_circle_points(radius=2, num_points=20)
    for i in range(len(mission_x)):
        input_str_list.append(f'{mission_x[i]},{mission_y[i]},{g},-1,1,0')


    for i in range(len(input_str_list)):
        input_str = input_str_list[i]
        if len(input_str) > 1:
            try:
                # delta_x, delta_y, delta_z, s, time_1, yaw_1 = map(int, input_str.split(','))
                delta_x, delta_y, delta_z, s, time_1, yaw_1 = map(float, input_str.split(','))
            except ValueError:
                print("输入无效，请重试.")
                continue
            if delta_x != 0 or delta_y != 0 or delta_z > 0 or s > 0 or time_1 > 0 or yaw_1 > 0:
                # print(x, y, z, s, time_1, yaw_1)
                async for position in drone.telemetry.position():
                    x = position.latitude_deg + delta_x / 111111.0
                    y = position.longitude_deg + delta_y / 111111.0
                    z = position.relative_altitude_m + delta_z
                    # print(x, y, z)
                    break
                print("-- 保存")
                print(x, y, z)
                mission_items.append(mission.MissionItem(x, y, z, s, True, float('nan'), float('nan'),
                                                         mission.MissionItem.CameraAction.NONE, time_1, 1.0, 0, yaw_1,
                                                         0))
        else:
            if input_str == 'q':
                break
                break

    # 设置航线任务
    mission_plan = mission.MissionPlan(mission_items)
    # await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_plan)
    await drone.mission.start_mission()




    recording_file = "gps_recording.csv"
    with open(recording_file, 'w') as f:
        f.write("X,Y,Z\n")

        while True:
            position = drone.telemetry.position()
            async for data in position:
                position_data = data
                break

            latitude = position_data.latitude_deg
            longitude = position_data.longitude_deg
            altitude = position_data.relative_altitude_m
            f.write(f"{latitude},{longitude},{altitude}\n")
            f.flush()
            print(f"X: {latitude}, Y: {longitude}, Z: {altitude}")
            time.sleep(0.1)

    input1 = input("'t' 清除任务: 任意则保存：")

    if input1 == 't':
        await drone.mission.clear_mission()
        print("任务已清除")
    else:
        print("保存任务")


# 执行程序
if __name__ == "__main__":
    # 执行的第二种方法
    asyncio.get_event_loop().run_until_complete(run())
