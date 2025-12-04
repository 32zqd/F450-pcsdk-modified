import serial
import time
import numpy as np
from PIL import Image
import os
from datetime import datetime


def save_image_data(data, width=320, height=240, format='RGB'):
    """
    将原始图像数据转换为图像并保存

    参数:
        data: 原始图像数据
        width: 图像宽度
        height: 图像高度
        format: 图像格式，例如'RGB'或'L'(灰度图)
    """
    try:
        if format == 'RGB':
            # 如果是RGB格式，每个像素3字节
            if len(data) < width * height * 3:
                print(f"警告: 数据大小 ({len(data)}) 小于预期 ({width * height * 3})")
                # 裁剪尺寸以适应数据
                while len(data) < width * height * 3:
                    if width > height:
                        width -= 1
                    else:
                        height -= 1

            # 将原始数据转换为NumPy数组，然后重塑为图像尺寸
            img_array = np.frombuffer(data, dtype=np.uint8)
            img_array = img_array[:width * height * 3].reshape((height, width, 3))

            # 创建PIL图像
            img = Image.fromarray(img_array)

        elif format == 'L':
            # 如果是灰度图，每个像素1字节
            if len(data) < width * height:
                print(f"警告: 数据大小 ({len(data)}) 小于预期 ({width * height})")
                # 裁剪尺寸以适应数据
                while len(data) < width * height:
                    if width > height:
                        width -= 1
                    else:
                        height -= 1

            img_array = np.frombuffer(data, dtype=np.uint8)
            img_array = img_array[:width * height].reshape((height, width))

            img = Image.fromarray(img_array, mode='L')

        else:
            raise ValueError(f"不支持的图像格式: {format}")

        # 创建保存目录
        if not os.path.exists('captured_images'):
            os.makedirs('captured_images')

        # 使用时间戳命名文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"captured_images/image_{timestamp}.png"

        # 保存图像
        img.save(filename)
        print(f"已保存图像: {filename}")
        return filename

    except Exception as e:
        print(f"保存图像时出错: {e}")
        return None


def monitor_serial_and_save_images(port, baudrate=115200, timeout=1,
                                   width=320, height=240, format='RGB'):
    """
    监控串口，打印16进制数据，并保存检测到的图像

    参数:
        port: 串口名称
        baudrate: 波特率
        timeout: 超时时间(秒)
        width: 图像宽度
        height: 图像高度
        format: 图像格式
    """
    try:
        # 打开串口，设置停止位1，数据位8，校验位None
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,  # 数据位8
            parity=serial.PARITY_NONE,  # 校验位None
            stopbits=serial.STOPBITS_ONE,  # 停止位1
            timeout=timeout
        )

        print(f"已连接到 {port}, 波特率 {baudrate}")
        print("配置: 数据位8, 校验位None, 停止位1")
        print(f"图像配置: 宽度={width}, 高度={height}, 格式={format}")
        print("正在监听串口数据，按Ctrl+C停止...")

        # 帧头和帧尾
        frame_header = [0xFE, 0x01]
        frame_footer = [0xFE, 0x01]  # 假设帧尾也是FE 01，如需更改请修改这里

        buffer = bytearray()
        in_frame = False
        header_index = 0
        footer_index = 0
        byte_count = 0

        while True:
            # 读取数据
            data = ser.read(ser.in_waiting or 1)
            if not data:
                continue

            # 处理接收到的数据
            for byte in data:
                # 打印16进制数据
                hex_str = f"{byte:02X}"
                print(hex_str, end=" ")
                byte_count += 1
                if byte_count % 16 == 0:  # 每16个字节换行
                    print()

                buffer.append(byte)

                # 检查帧头
                if not in_frame:
                    if byte == frame_header[header_index]:
                        header_index += 1
                        if header_index == len(frame_header):
                            print("\n检测到帧头: FE 01")
                            in_frame = True
                            # 保留帧头
                            buffer = buffer[-len(frame_header):]
                            header_index = 0
                    else:
                        header_index = 0
                        # 如果第一个字节是0xFE，但第二个不是0x01，重新检查
                        if byte == frame_header[0]:
                            header_index = 1
                        # 清空无用数据
                        buffer = buffer[-1:] if header_index > 0 else bytearray()

                # 检查帧尾
                elif in_frame:
                    if byte == frame_footer[footer_index]:
                        footer_index += 1
                        if footer_index == len(frame_footer):
                            print("\n检测到帧尾: FE 01")
                            in_frame = False
                            footer_index = 0

                            # 提取图像数据 (移除帧头和帧尾)
                            image_data = buffer[len(frame_header):-len(frame_footer)]

                            # 检查数据是否非空
                            if image_data:
                                print(f"接收到图像数据: {len(image_data)} 字节")
                                # 保存图像
                                save_image_data(image_data, width, height, format)
                            else:
                                print("接收到空图像数据")

                            # 清空缓冲区
                            buffer.clear()
                    else:
                        footer_index = 0
                        # 如果第一个字节是0xFE，但第二个不是0x01，重新检查
                        if byte == frame_footer[0]:
                            footer_index = 1

            # 短暂延时，以降低CPU占用
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"\n发生错误: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("串口已关闭")


def main():
    """程序入口点"""
    # 这些参数可以根据需要调整
    port = "COM10"  # 根据您的实际串口更改
    baudrate = 115200
    width = 320
    height = 240
    img_format = 'RGB'  # 或 'L' 用于灰度图

    monitor_serial_and_save_images(port, baudrate, width=width, height=height, format=img_format)


if __name__ == "__main__":
    main()
