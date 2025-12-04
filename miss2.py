#!/usr/bin/env python3
import asyncio
import numpy as np
from mavsdk import System, mission
from mavsdk.mission import MissionItem


# 生成闭合圆形航点（含起飞点返回）
def generate_circle_waypoints(center_lat, center_lon, radius, num_points=20, altitude=3):
    waypoints = []
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=True)  # 包含2π，闭合圆形
    # 经纬度换算系数：1米≈1/111111度（经度需按纬度修正）
    lat_per_m = 1 / 111111.0
    lon_per_m = 1 / (111111.0 * np.cos(np.radians(center_lat)))
    
    for angle in angles:
        delta_x = radius * np.cos(angle)  # 东向偏移（X轴）
        delta_y = radius * np.sin(angle)  # 北向偏移（Y轴）
        lat = center_lat + delta_y * lat_per_m
        lon = center_lon + delta_x * lon_per_m
        waypoints.append(MissionItem(
            lat, lon, altitude, 0.5,  # 纬度、经度、高度、速度（0.5m/s）
            True, float('nan'), float('nan'),
            mission.MissionItem.CameraAction.NONE,
            float('nan'), 1.0, 0, 0, 0,
            mission.MissionItem.VehicleAction.NONE
        ))
    
    # 添加起飞点作为最后一个航点，确保返回原点
    waypoints.append(MissionItem(
        center_lat, center_lon, altitude, 2.0,
        True, float('nan'), float('nan'),
        mission.MissionItem.CameraAction.NONE,
        float('nan'), 1.0, 0, 0, 0,
        mission.MissionItem.VehicleAction.NONE
    ))
    return waypoints


async def run():
    # 连接无人机
    drone = System()
    drone = System(mavsdk_server_address='localhost', port=50051)  #仿真需要注释，真机解开注释
    await drone.connect(system_address="udp://:14540")
    print("等待连接...")
    
    # 等待无人机连接
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- 连接成功!")
            break

    # 等待GPS就绪（并确保系统可解锁）
    print("GPS定点估算...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- GPS位置就绪")
            break

    # 等待系统可以解锁（is_armable 为 True）
    print("等待系统可解锁 (is_armable)...")
    async for health in drone.telemetry.health():
        if getattr(health, 'is_armable', False):
            print("-- 系统可解除锁定")
            break

    # 获取起飞点GPS坐标（作为圆心和返回点）
    async for position in drone.telemetry.position():
        center_lat = position.latitude_deg
        center_lon = position.longitude_deg
        takeoff_alt = position.relative_altitude_m + 3  # 起飞后目标高度（相对高度+3米）
        print(f"起飞点坐标：{center_lat:.6f}, {center_lon:.6f}，目标高度：{takeoff_alt}米")
        break

    # 生成闭合圆形航点（含返回起飞点）
    mission_items = generate_circle_waypoints(center_lat, center_lon, 5, 20, takeoff_alt)
    if not mission_items:
        print("错误：未生成航点！")
        return
    print(f"生成{len(mission_items)}个航点（含返回起飞点）")

    # 解锁并起飞（带重试与状态确认）
    print("-- Arming")
    armed = False
    for attempt in range(3):
        try:
            await drone.action.arm()
            # 确认已解锁
            for _ in range(20):
                async for is_armed in drone.telemetry.armed():
                    if is_armed:
                        armed = True
                    break
                if armed:
                    break
                await asyncio.sleep(0.25)
            if armed:
                print("-- 已解锁 (armed)")
                break
            else:
                print(f"尝试解锁 {attempt+1} 成功发送命令，但尚未报告解锁，重试...")
        except Exception as e:
            print(f"尝试解锁失败 ({attempt+1}): {e}")
            await asyncio.sleep(1)

    if not armed:
        print("错误：无法解锁（arming failed / TIMEOUT）。请检查飞控、遥控器安全开关或仿真配置。")
        return

    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(10)  # 等待升至目标高度

    # 上传并启动任务
    mission_plan = mission.MissionPlan(mission_items)
    await drone.mission.upload_mission(mission_plan)
    print("-- 启动航点任务（圆形轨迹+返回原点）")
    await drone.mission.start_mission()

    # 实时记录GPS轨迹（非阻塞异步任务）
    async def record_gps():
        with open("gps_trajectory_complete.csv", 'w') as f:
            f.write("latitude,longitude,altitude,timestamp\n")
            while True:
                async for position in drone.telemetry.position():
                    ts = asyncio.get_event_loop().time()
                    f.write(f"{position.latitude_deg:.6f},{position.longitude_deg:.6f},{position.relative_altitude_m:.2f},{ts:.2f}\n")
                    f.flush()
                    print(f"当前位置：{position.latitude_deg:.6f}, {position.longitude_deg:.6f}, 高度：{position.relative_altitude_m:.2f}m")
                    break
                await asyncio.sleep(0.1)  # 10Hz记录频率

    # 启动GPS记录任务
    record_task = asyncio.create_task(record_gps())

    # 监听任务完成状态
    async for mission_progress in drone.mission.mission_progress():
        print(f"任务进度：{mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("-- 航点任务完成（已返回原点），开始降落")
            await drone.action.land()
            record_task.cancel()  # 停止GPS记录
            break

    # 等待降落完成
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("-- 无人机已降落至起飞点")
            break


if __name__ == "__main__":
    asyncio.run(run())