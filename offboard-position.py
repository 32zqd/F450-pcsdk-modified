import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError,PositionNedYaw,VelocityNedYaw,VelocityBodyYawspeed,AttitudeRate)


#END坐标，高度为-数，以下程序做了修改，正常数输入即可
#本历程包含位置，速度，机体，姿态控制
async def move_right(drone):
    #确保安全
    x=0
    i=0
    while True:
        print("输入起飞高度") 
        x=int(input())
        print(x)
        if x > 0:
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
    #初始化变量，获取航向位置
    var1, var2, var3, var4 = 0, 0, 0, 0
    await drone.action.takeoff()
    async for heading in drone.telemetry.attitude_euler():
        print(heading.yaw_deg)
        break
    #相应安全设置并切换offboard发布位置
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, heading.yaw_deg)) 
    if i==1:
        print("-- Arm")
        await drone.action.arm()
        x=-x
        await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, x, heading.yaw_deg))
    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"切换 offboard mode 失败，错误代码: \
            {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return
    #执行循环指点代码，q退出
    while True:
        
        input_str = input("输入X轴,Y轴,高度,航向角(注意：高度为相对高度，输入负数意味着低于起飞高度)   空格隔开 ")
        #END坐标，将高度正数化
        try:
            var1, var2, var3, var4 = map(float, input_str.split())
            if var3>0:
                var33=-var3
            else:
                var33=-var3 
        except ValueError:
            print("输入无效，请重试.")
            continue
        if var1 != 0 or var2 != 0 or var33 != 0 or var4 != 0 :
                print(var1,var2,var3,var4)
                print("-- 执行")
                await drone.offboard.set_position_ned(PositionNedYaw(var1, var2, var33, var4))  
                #END坐标下航点及航向，按q退出
                # await drone.offboard.set_velocity_body(VelocityBodyYawspeed(var1, var2, var33, var4))
                # await asyncio.sleep(5)
                # break
                #END机体坐标下设置速度与偏航向角度，运行5秒退出
                #await drone.offboard.set_velocity_ned(VelocityNedYaw(var1, var2, var33, var4))
                # await asyncio.sleep(5)
                # break
                #NED坐标和偏航设置速度，运行5秒退出
                #await drone.offboard.set_attitude_rate(AttitudeRate(var1, var2, var33, var4))
                # await asyncio.sleep(5)
                # break
                #END坐标设置姿态角度及油门杆量，运行5秒退出
        input_str = input("输入 回车继续，'q' 退出: ")
        if input_str == 'q':
            break
#链接无人机
async def run():
    drone = System()
    #drone = System(mavsdk_server_address='localhost', port=50051)   #仿真需要注释，真机解开注释
    await drone.connect(system_address="udp://:14540")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- OK")
            break
    await drone.action.arm()
    async for heading in drone.telemetry.attitude_euler():
        print(heading.yaw_deg)
        break
    #执行循环主题
    await move_right(drone)
    #判断offboard是否成功
    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"停止板外模式失败，出现错误代码: \
              {error._result.result}")
    #进入悬停
    print("-- hold")
    await drone.action.hold()
    #返航模式设置
    f=0
    g=0
    while True:
        print("输入返航高度") 
        f=int(input())
        print(f)
        if f > 0:
            await drone.action.set_return_to_launch_altitude(f)
        else:
            print("数据无效")
        print("输入1返航")
        g=int(input())
        print(g)
        if g==1:
            break
        else:
            print("重新输入")
    gao = await drone.action.get_return_to_launch_altitude() 
    print("返航高度",gao)
    await drone.action.return_to_launch()
#执行程序
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
