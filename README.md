# mavsdk

#### 介绍
  Mavlink是Pixhawk的通讯协议，mavlink很简单。而MavSDK可以发送Mavlink信号到飞控然后控制飞控的工具包，就不再需要自己写mavlink了。

  MAVSDK特点

  跨平台的：Linux、macOS、Windows、Android 和 iOS。

  多语言的: c++，swift，python，java，Go，JavaScript，CSharp，Rust。

  在使用时可以通过串口或者tcp或者udp建立连接然后就可以控制Pixhawk飞控。在此之前可以在Ubuntu下建立Pixhawk的源码然后并创建模拟器，然后在mavsdk控制模拟器里的飞机进行控制。


#### 安装教程
1.选择Ubuntu20.04版本系统，安装PX4-Autopilot

2.先mkdir一个文件夹，在该文件夹下进行源码下载（因为在github下载很慢，所以后续到PX4-Autopilot目录下再单独下载子模块）

    git clone http://github.com/PX4/PX4-Autopilot

3.下载完后，到PX4-Autopilot目录下检查子模块是否下载完成，没反应说明安装成功

    cd PX4-Autopilot/
    git submodule update --init --recursive

4.可能出现执行3中命令没反应，但make的时候报错的情况，找到对应路径删掉，再执行上面那个命令

5.回到上一级目录，执行以下安装脚本

    bash ./PX4-Autopilot/Tools/setup/ubuntu.sh

6.运行完按提示重新登陆或者重启，然后可以update一下

	sudo apt-get update
    sudo apt-get upgrade

7.进入目录编译源码进入仿真

    cd PX4-Autopilot/
    make px4_sitl jmavsim

8.安装打开QGC地面站

下载地址： 

    https://dl.amovlab.com:30443/MFP450/pixhawk%206c/UBUNTU20.04%E5%9C%B0%E9%9D%A2%E7%AB%99/

也可选择官网下载：

    https://docs.qgroundcontrol.com/master/en/getting_started/download_and_install.html

打开终端，给予权限：

    chmod +x ./QGroundControl.AppImage
    ./QGroundControl.AppImage  (or double click)

9.安装python3.7以上版本后下载MAVSDK库

    pip3 install mavsdk

目前提供程序为python版本

10.下载VScode

    https://code.visualstudio.com/Download
在VScode运行程序仿真（python3 ./xxx.py）即可





