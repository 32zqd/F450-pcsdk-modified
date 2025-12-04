import socket
import json
import time
import rospy
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Header

# UDP接收配置
UDP_IP = "192.168.137.3"
UDP_PORT = 12346

# ROS配置
MAX_PATH_POINTS = 1000  # 最大路径点数量，避免内存过度使用
TOPIC_NAME = '/uav_path'  # ROS topic名称

def main():
    # 初始化ROS节点
    rospy.init_node('uav_path_publisher', anonymous=True)
    
    # 创建Path发布器
    path_pub = rospy.Publisher(TOPIC_NAME, Path, queue_size=10)
    
    # 初始化Path消息
    path_msg = Path()
    path_msg.header.frame_id = "map"  # 设置坐标系
    
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 设置端口重用选项
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 尝试绑定端口，如果失败则尝试其他端口
    port_to_try = UDP_PORT
    max_attempts = 10
    
    for attempt in range(max_attempts):
        try:
            sock.bind((UDP_IP, port_to_try))
            print(f"成功绑定到端口 {port_to_try}")
            break
        except OSError as e:
            if e.errno == 10048:  # 端口已被占用
                print(f"端口 {port_to_try} 已被占用，尝试端口 {port_to_try + 1}")
                port_to_try += 1
            else:
                print(f"绑定端口时发生错误: {e}")
                sock.close()
                return
    else:
        print(f"尝试了 {max_attempts} 个端口都失败，程序退出")
        sock.close()
        return
    
    print(f"UDP接收器启动，监听 {UDP_IP}:{port_to_try}")
    print("等待接收无人机位置数据...")
    print(f"ROS Path发布器已启动，topic: {TOPIC_NAME}")
    
    try:
        while True and not rospy.is_shutdown():
            # 接收数据
            data, addr = sock.recvfrom(1024)
            
            try:
                # 解析JSON数据
                position_data = json.loads(data.decode('utf-8'))
                x = position_data['x1']
                y = position_data['y1'] 
                z = position_data['z1']
                
                print(f"收到位置数据: x1={x}, y1={y}, z1={z}")
                print(f"时间戳: {position_data['timestamp']}")
                print(f"发送方: {addr}")
                
                # 创建PoseStamped消息
                pose_stamped = PoseStamped()
                pose_stamped.header.stamp = rospy.Time.now()
                pose_stamped.header.frame_id = "map"
                
                # 设置位置信息
                pose_stamped.pose.position.x = x
                pose_stamped.pose.position.y = y
                pose_stamped.pose.position.z = z
                
                # 设置方向（这里设置为默认值，如果有方向数据可以修改）
                pose_stamped.pose.orientation.x = 0.0
                pose_stamped.pose.orientation.y = 0.0
                pose_stamped.pose.orientation.z = 0.0
                pose_stamped.pose.orientation.w = 1.0
                
                # 添加到路径中
                path_msg.poses.append(pose_stamped)
                
                # 限制路径点数量，避免内存过度使用
                if len(path_msg.poses) > MAX_PATH_POINTS:
                    path_msg.poses.pop(0)  # 移除最旧的点
                
                path_msg.header.stamp = rospy.Time.now()
                
                # 发布Path消息
                path_pub.publish(path_msg)
                
                print(f"已发布Path消息，当前路径点数: {len(path_msg.poses)}")
                print("-" * 50)
                
            except json.JSONDecodeError:
                print(f"收到非JSON数据: {data.decode('utf-8')}")
            except KeyError as e:
                print(f"JSON数据缺少必要字段: {e}")
                
    except KeyboardInterrupt:
        print("\n接收器停止")
    finally:
        sock.close()

if __name__ == "__main__":
    main()