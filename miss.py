import asyncio
import math
from mavsdk.offboard import PositionNedYaw
from mavsdk import System, mission

#END坐标，高度为-数，以下程序做了修改，正常数输入即可

async def run():
    # 连接无人机
    drone = System()
    #drone = System(mavsdk_server_address='localhost', port=50051)
    await drone.connect(system_address="udp://:14540")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"321.!")
            break
    async for att in drone.telemetry.attitude_euler():
        heading_deg = att.yaw_deg
        print(f"Current heading: {heading_deg} degrees")
        break
        
    async for position in drone.telemetry.position():
        la = position.latitude_deg
        lo = position.longitude_deg
        al = position.relative_altitude_m
        print(la,lo,al)
        break
    print("-- Arming")
    await drone.action.arm()
    g,i=0,0
    while True:
        print("输入起飞高度") 
        g=int(input())
        print(g)
        if g > 0:
            await drone.action.set_takeoff_altitude(g)
        else:
            print("数据无效")
        print("输入1起飞，任意输入返回起飞输入")
        i=int(input())
        print(i)
        if i==1:
            break
        else:
            print("重新输入")
    

            
    await drone.action.set_takeoff_altitude(g)

    print("-- Taking off")
    await drone.action.takeoff()
    print(g)
    z1 = 0
    while (z1!=g):
        await drone.action.set_takeoff_altitude(g)
        await drone.action.arm()
        await drone.action.takeoff()
        async for position in drone.telemetry.position():
            z1 = position.relative_altitude_m
            z1=int(z1)
            break
#确保起飞高度

    print(g,z1)
    x,y,z,s,time_1,yaw_1=0,0,0,-1,-1,-1
    # 创建航线任务，并添加航点
    mission_items = []
    
    while True:

        input_str = input("输入北东地（地坐标已转换正数）--X轴,Y轴,高度,速度，悬停时间，航向角\n(注意：高度为相对高度，共6个参数，注意参数描述，高度输入负数意味着低于起飞高度,且需要两个航点任务)   空格隔开\n ")
        try:
            x,y,z,s,time_1, yaw_1 = map(float, input_str.split( ))
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
                    print(x,y,z)
                    break
                print("-- 保存")
                mission_items.append(mission.MissionItem(x, y, z, s, True, float('nan'), float('nan'), mission.MissionItem.CameraAction.NONE, time_1, 1.0,0,yaw_1,0))
                print(mission_items)

                input_str = input("输入 回车继续，'q' 执行: ")
                if input_str == 'q':
                    break

   
    
    # 设置航线任务
    mission_plan = mission.MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(mission_plan)
    
    await drone.mission.start_mission()
    while(1):
        input1=input("'t' 清除任务: 任意则保存:")
        if input1=='t':
            await drone.mission.clear_mission()
            break 
        else:
            break    
    
    
    
    

if __name__ == "__main__":
    #asyncio.ensure_future()
    #asyncio.get_event_loop().run_forever()
    asyncio.get_event_loop().run_until_complete(run())
