# Python env   : MicroPython v1.23.0 on Raspberry Pi Pico
# -*- coding: utf-8 -*-        
# @Time    : 2025/1/19 上午10:57   
# @Author  : 李清水            
# @File    : main.py       
# @Description : ADC和DAC测试程序：1.使用ADS1115外置ADC芯片采集数据，定时器触发采集；2.使用MCP4725外置DAC芯片输出波形。

# ======================================== 导入相关模块 =========================================

# 导入硬件相关模块
from machine import Pin, I2C, Timer, UART
# 导入时间相关模块
import time
# 导入外部ADC相关模块
from ads1115 import ADS1115
# 导入二进制数据和原生数据类型打包解包模块
import struct
# 导入mcp4725模块用于控制DAC芯片
from mcp4725 import MCP4725
# 导入波形发生器类
from dac_waveformgenerator import WaveformGenerator

# ======================================== 全局变量 ============================================

# 外置ADC地址
ADC_ADDRESS = 0
# 使用的ADC通道
POT_CHANNEL = 0

# 滑动均值滤波器相关变量
FILTER_SIZE   = 20
filter_buffer = []
filter_sum = 0

# mcp4725芯片地址
DAC_ADDRESS = 0
# 电压转换系数
adc_conversion_factor = 3.3 / (65535)

# ======================================== 功能函数 ============================================

# 定义定时器回调函数
def timer_callback(timer):
    '''
    定时器回调函数，用于定时采样
    :param timer    [machine.Timer]: 定时器对象
    :return : None
    '''
    # 声明全局变量
    global adc, POT_CHANNEL, FILTER_SIZE

    # 采集数据
    try:
        # 设置当前转换速率和通道
        adc.set_conv(rate=7, channel1=POT_CHANNEL)
        # 读取采样数据并启动下一次转换
        raw_adc = adc.read_rev()
        # 将原始值转换为电压
        voltage = adc.raw_to_v(raw_adc)
        # 打印采样数据
        print(f"Channel AIN{POT_CHANNEL}: {voltage:.4f} V (Raw: {raw_adc})")

        # 将原始ADC值存储为int16
        adc_value = int(raw_adc)
        # 使用独立的滑动均值滤波器函数
        average = moving_average_filter(adc_value, FILTER_SIZE)

        # 构建并发送数据帧，传递原始值和滤波值
        send_data_frames(raw_adc, average)
    except Exception as e:
        print("Error in timer_callback:", e)

# 串口数据帧打包函数
def send_data_frames(raw_adc, average):
    '''
    串口发送数据函数，发送原始ADC值和滤波后的平均值
    :param raw_adc     [int]: 原始ADC采集的值
    :param average     [int]: 滤波后的平均值
    :return : None
    '''
    global uart

    try:
        # 构建数据帧
        # 帧头为0xAA 0xBB，后面是两个16位数据，使用小端模式
        frame_header = struct.pack('<2B', 0xAA, 0xBB)
        frame_data = struct.pack('<2H', raw_adc & 0xFFFF, average & 0xFFFF)
        frame_full = frame_header + frame_data
        # 发送数据帧
        uart.write(frame_full)
    except Exception as e:
        print("Error in send_data_frames:", e)

# 滑动均值滤波函数
def moving_average_filter(new_value, filter_size):
    '''
    滑动均值滤波器
    :param new_value    [int]: 新采样值
    :param filter_size  [int]: 滤波器窗口大小
    :return [int]: 当前滑动均值
    '''
    # 声明全局变量
    global filter_buffer, filter_sum

    # 将新值加入缓冲区
    filter_buffer.append(new_value)
    filter_sum += new_value

    # 如果缓冲区超过滤波器大小，移除最旧的值
    if len(filter_buffer) > filter_size:
        removed = filter_buffer.pop(0)
        filter_sum -= removed

    # 计算并返回滑动平均值
    return filter_sum // len(filter_buffer)

# ======================================== 自定义类 ============================================

# ======================================== 初始化配置 ==========================================

# 上电延时3s
time.sleep(3)
# 打印调试消息
print("FreakStudio: Using ADS1115 acquire signal and MCP4725 output waveform")

# 创建串口对象，设置波特率为256000
uart = UART(0, 256000)
# 初始化uart对象，波特率为256000，数据位为8，无校验位，停止位为1
# 设置接收引脚为GPIO1，发送引脚为GPIO0
# 设置串口超时时间为100ms
uart.init(baudrate  = 256000,
          bits      = 8,
          parity    = None,
          stop      = 1,
          tx        = 0,
          rx        = 1,
          timeout   = 100)

# 创建硬件I2C的实例，使用I2C1外设，时钟频率为400KHz，SDA引脚为6，SCL引脚为7
i2c = I2C(id=1, sda=Pin(6), scl=Pin(7), freq=400000)

# 开始扫描I2C总线上的设备，返回从机地址的列表
devices_list = i2c.scan()
print('START I2C SCANNER')

# 若devices_list为空，则没有设备连接到I2C总线上
if len(devices_list) == 0:
    print("No i2c device !")
# 若非空，则打印从机设备地址
else:
    print('i2c devices found:', len(devices_list))
    # 遍历从机设备地址列表
    for device in devices_list:
        # 判断地址是否在0x48到0x4B之间，如果是，则为ADS1115芯片地址
        if 0x48 <= device <= 0x4B:
            print("ADC I2C hexadecimal address: ", hex(device))
            ADC_ADDRESS = device
        # 判断地址是否在0x60到0x63之间，如果是，则为MCP4725芯片地址
        elif 0x60 <= device <= 0x63:
            print("DAC I2C hexadecimal address: ", hex(device))
            DAC_ADDRESS = device

# 创建ADC相关实例，增益系数设置为1
adc = ADS1115(i2c, ADC_ADDRESS, 1)
# 创建DAC对象，使用I2C0外设，地址为DAC_ADDRESS
dac = MCP4725(i2c, DAC_ADDRESS)

# ========================================  主程序  ===========================================
# 读取DAC的配置信息
eeprom_write_busy, power_down, value, eeprom_power_down, eeprom_value = dac.read()
print(eeprom_write_busy, power_down, value, eeprom_power_down, eeprom_value)
# 配置DAC：取消电源关断模式，输出电压为0V，写入EEPROM
dac.config(power_down='Off',value=0,eeprom=True)
# 延时50ms，配置完成后立即读取会发生错误
time.sleep_ms(50)
# 读取DAC的配置信息
eeprom_write_busy, power_down, value, eeprom_power_down, eeprom_value = dac.read()
print(eeprom_write_busy, power_down, value, eeprom_power_down, eeprom_value)

# 生成正弦波
print("FreakStudio : Generate Sine Waveform : 10Hz, 1.5V, 1.5V")
# 初始化波形生成器
wave = WaveformGenerator(dac, frequency=10, amplitude=1.5, offset=1.5, waveform='sine')
# 启动波形生成
wave.start()

# 初始化ADC采样的软件定时器，设置周期为10毫秒（100Hz）
timer = Timer(-1)
timer.init(period=2, mode=Timer.PERIODIC, callback=timer_callback)

# 无限循环：无具体操作
while True:
    # 延时1s
    time.sleep(1)