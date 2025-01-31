# Python env   : MicroPython v1.23.0 on Raspberry Pi Pico
# -*- coding: utf-8 -*-        
# @Time    : 2025/1/19 上午10:57   
# @Author  : 李清水            
# @File    : main.py       
# @Description : 幅度可调DDS信号发生模块测试程序

# ======================================== 导入相关模块 =========================================

# 导入DDS信号发生AD9833类
from ad9833 import AD9833
# 导入数字电位器MCP41010类
from mcp41010 import MCP41010
# 导入时间相关模块
import time

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

# ======================================== 初始化配置 ==========================================

# 上电延时3s
time.sleep(3)
# 打印调试消息
print("FreakStudio: Using AD9833 and MCP41010 to implement DDS signal generator")

# # 创建AD9833芯片实例，使用SPI0外设：MOSI-GP3、SCLK-GP2、CS-GP27
ad9833 = AD9833(sdo=3, clk=2, cs=27, fmclk=25, spi_id=0)
# # 创建MCP41010芯片实例，使用SPI0外设：MOSI-GP3、SCLK-GP2、CS-GP26
mcp41010 = MCP41010(clk_pin=2, cs_pin=26, mosi_pin=3, spi_id=0, max_value=255)

# ========================================  主程序  ===========================================

# 设置AD9833芯片的频率和相位
# 设置频率寄存器0和相位寄存器0的数据
ad9833.set_frequency(5000,0)
ad9833.set_phase(0, 0, rads = False)
# 设置频率寄存器1和相位寄存器1的数据
ad9833.set_frequency(1300, 1)
ad9833.set_phase(180, 1, rads = False)
# 选择AD9833芯片的频率和相位
ad9833.select_freq_phase(0, 0)

# 设置MCP41010芯片的电位器值
mcp41010.set_value(125)

# 选择频率寄存器0和相位寄存器0，设置DDS信号发生器的输出模式为正弦波
ad9833.select_freq_phase(0,0)
ad9833.set_mode('SIN')

# # 调节电位器值，观察DDS信号发生器的输出波形
# mcp41010.set_value(20)
#
# # 选择频率寄存器0和相位寄存器0，设置DDS信号发生器的输出模式为方波
# ad9833.select_freq_phase(0,0)
# ad9833.set_mode('SQUARE')
#
# # 选择频率寄存器0和相位寄存器0，设置DDS信号发生器的输出模式为频率减半的方波
# ad9833.select_freq_phase(0,0)
# ad9833.set_mode('SQUARE/2')
#
# # 选择频率寄存器0和相位寄存器0，设置DDS信号发生器的输出模式为三角波
# ad9833.select_freq_phase(0,0)
# ad9833.set_mode('TRIANGLE')
#
# # 选择频率寄存器1和相位寄存器1，设置DDS信号发生器的输出模式为三角波
# ad9833.select_freq_phase(1,1)
# ad9833.set_mode('TRIANGLE')