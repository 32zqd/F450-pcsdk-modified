import asyncio
import time
import os
from datetime import datetime
from mavsdk import System
from mavsdk.offboard import PositionNedYaw

# 初始化连接函数 - 只运行一次
async def initialize_drone():
    drone = System(mavsdk_server_address='localhost', port=50051) #仿真需要注释，真机解开注释
    print("等待连接...")
    await drone.connect(system_address="udp://:14540")
   
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- 连接成功!")
            break

    print("GPS定点估算...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
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
    print("开始持续读取位置信息...")
    
    # 确保log文件夹存在
    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件名（包含日期时间）
    log_filename = os.path.join(log_dir, f"gps_position_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # 频率统计变量
    read_count = 0
    start_time = time.time()
    last_stats_time = start_time
    
    # 数据缓存列表
    data_buffer = []
    
    # 写入TXT文件头
    with open(log_filename, 'w', encoding='utf-8') as txtfile:
        txtfile.write("GPS位置数据记录\n")
        txtfile.write("=" * 80 + "\n")
        txtfile.write("格式: 时间戳 | 纬度(度) | 经度(度) | 相对高度(米) | GPS高度(米) | 读取次数 | 频率(Hz)\n")
        txtfile.write("=" * 80 + "\n\n")
    
    async for position in drone.telemetry.position():
        # 获取当前时间戳
        current_time = datetime.now()
        timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 精确到毫秒
        
        x1 = position.latitude_deg 
        y1 = position.longitude_deg
        z1 = position.relative_altitude_m
        g1 = position.absolute_altitude_m
        
        # 更新频率统计
        read_count += 1
        current_timestamp = time.time()
        
        # 将数据添加到缓存
        data_buffer.append({
            'timestamp': timestamp,
            'latitude': x1,
            'longitude': y1,
            'relative_altitude': z1,
            'gps_altitude': g1,
            'count': read_count
        })
        
        # 计算频率（每5秒统计一次并写入文件）
        if current_timestamp - last_stats_time >= 5.0:
            elapsed_time = current_timestamp - start_time
            frequency = read_count / elapsed_time if elapsed_time > 0 else 0
            last_stats_time = current_timestamp
            
            print(f"GPS坐标（相对高度与GPS高）{x1}, {y1}, {z1}, {g1} | 读取次数: {read_count} | 频率: {frequency:.2f} Hz")
            
            # 一次性写入缓存中的所有数据到TXT文件
            with open(log_filename, 'a', encoding='utf-8') as txtfile:
                txtfile.write(f"\n--- 频率统计时间: {timestamp} | 总读取次数: {read_count} | 当前频率: {frequency:.2f} Hz ---\n")
                for data in data_buffer:
                    txtfile.write(f"{data['timestamp']} | {data['latitude']:.7f} | {data['longitude']:.7f} | {data['relative_altitude']:.3f} | {data['gps_altitude']:.3f} | {data['count']} | {frequency:.2f}\n")
                txtfile.write("\n")
            
            # 清空缓存
            data_buffer = []
        else:
            print(f"GPS坐标（相对高度与GPS高）{x1}, {y1}, {z1}, {g1}")
        
        # 添加短暂延时避免输出过快
        await asyncio.sleep(0.5)

# 主运行函数
async def main():
    # 初始化连接 - 只运行一次
    drone = await initialize_drone()
    
    # 持续读取位置信息
    await read_position_continuously(drone)

# 执行程序
if __name__ == "__main__":
    asyncio.run(main())

