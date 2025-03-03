# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-
# @Time    : 2024/7/28 下午3:00
# @Author  : 李清水
# @File    : main.py
# @Description : ESP32 WiFi 继电器点灯例程

# ======================================== 导入相关模块 ========================================

# 导入WiFi模块
import network
# 导入socket模块
import socket
# 导入硬件相关的模块
from machine import Pin
# 导入时间相关的模块
import time

# ======================================== 全局变量 ============================================

# 定义继电器连接的GPIO引脚-继电器控制LED
RELAY_PIN_NUM = 7
# 定义WiFi的SSID和密码
WIFI_SSID = "CU_VXt4_5G"
WIFI_PASSWORD = "p395m7hs"

# ======================================== 功能函数 ============================================

def connect_wifi(ssid: str, password: str) -> None:
    """
    连接WiFi网络。

    Args:
        ssid (str): WiFi的SSID。
        password (str): WiFi的密码。

    Returns:
        None

    Description:
        该函数用于连接指定的WiFi网络，并在连接成功后打印IP地址。
    """
    # 创建WLAN对象
    wlan = network.WLAN(network.STA_IF)
    # 激活WLAN接口
    wlan.active(True)
    # 如果未连接WiFi，则尝试连接
    if not wlan.isconnected():
        print("正在连接WiFi...")
        # 连接WiFi
        wlan.connect(ssid, password)
        # 等待连接成功
        while not wlan.isconnected():
            time.sleep(1)
    # 打印连接成功信息
    print("WiFi连接成功！")
    print("IP地址:", wlan.ifconfig()[0])


def start_web_server(led: Pin) -> None:
    """
    启动Web服务器，用于控制LED。

    Args:
        led (machine.Pin): 控制LED的GPIO引脚对象。

    Returns:
        None

    Description:
        该函数启动一个简单的Web服务器，用户可以通过网页控制LED的开关。
    """
    # 创建socket对象
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    sock = socket.socket()
    # 绑定地址和端口
    sock.bind(addr)
    # 开始监听
    sock.listen(1)
    print("Web服务器已启动，等待连接...")

    while True:
        # 接受客户端连接
        conn, addr = sock.accept()
        print("客户端连接来自:", addr)
        # 接收客户端请求
        request = conn.recv(1024)
        request = str(request)
        print("请求内容:", request)

        # 解析请求
        if "GET /ledon" in request:
            # 打开LED
            led.value(1)
            response = "LED已打开"
        elif "GET /ledoff" in request:
            # 关闭LED
            led.value(0)
            response = "LED已关闭"
        else:
            response = "未知请求"

        # 发送HTTP响应
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(response)
        # 关闭连接
        conn.close()


# ======================================== 自定义类 ============================================

# ======================================== 初始化配置 ==========================================

# 上电延时3s
time.sleep(3)
# 打印调试信息
print("FreakStudio: ESP32 WiFi 点灯例程")

# 初始化RELAY_PIN继电器引脚
RELAY_PIN = Pin(RELAY_PIN_NUM, Pin.OUT)
# 连接WiFi
connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# ========================================  主程序  ===========================================

# 启动Web服务器
start_web_server(RELAY_PIN)