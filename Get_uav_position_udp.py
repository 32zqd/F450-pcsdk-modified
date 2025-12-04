import asyncio
import time
import os
import socket
import json
from datetime import datetime
from mavsdk import System
from mavsdk.offboard import PositionNedYaw

# UDP配置
UDP_IP = "192.168.137.3"  # 目标IP地址
UDP_PORT = 12346      # 目标端口

# 初始化连接函数 - 只运行一次
async def initialize_drone():
    drone = System(mavsdk_server_address='localhost', port=50051) 
    print("等待连接...")
    await drone.connect(system_address="udp://:14540")
   
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- 连接成功!")
            break

    print("GPS定点估算...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("-- GPS位置就绪")
            break

    #电池电压百分比
    async for bat in drone.telemetry.battery():
        x4 = bat.voltage_v
        y4 = bat.remaining_percent
        print('%.2f'%x4,"V",'%.1f'%y4,"%")
        break
    #GPS状态及卫星数量
    async for a1 in drone.telemetry.gps_info(): 
        x5=a1.fix_type
        y5=a1.num_satellites
        print("gps：",x5,y5)
        break
    
    return drone

# 持续读取位置信息函数
async def read_position_continuously(drone):
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    async for position in drone.telemetry.position():
        x1 = position.latitude_deg 
        y1 = position.longitude_deg
        z1 = position.absolute_altitude_m  # 使用z1替代g1
    
        print(f"{x1}, {y1}, {z1}")
        
        # 准备UDP数据
        position_data = {
            "x1": x1,
            "y1": y1, 
            "z1": z1,
            "timestamp": datetime.now().isoformat()
        }
        
        # 发送UDP数据
        try:
            message = json.dumps(position_data)
            sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT))
            print(f"UDP发送: {message}")
        except Exception as e:
            print(f"UDP发送错误: {e}")
        
# 主运行函数
async def main():
    # 初始化连接 - 只运行一次
    drone = await initialize_drone()
    
    # 持续读取位置信息
    await read_position_continuously(drone)

# 执行程序
if __name__ == "__main__":
    asyncio.run(main())

