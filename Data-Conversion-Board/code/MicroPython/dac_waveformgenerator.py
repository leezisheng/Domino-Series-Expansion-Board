# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2025/1/19 上午11:13   
# @Author  : 李清水            
# @File    : dac_waveformgenerator.py
# @Description : 使用DAC芯片生成正弦波、三角波、锯齿波的类
# 这部分代码由 leeqingshui 开发，采用CC BY-NC 4.0许可协议

# ======================================== 导入相关模块 =========================================

# 导入数学库用于计算正弦波
import math
# 导入硬件模块
from machine import Timer
# 导入mcp4725模块用于控制DAC芯片
from mcp4725 import MCP4725

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

# 自定义DAC波形发生器类
class WaveformGenerator:
    def __init__(self, dac: 'MCP4725', frequency: float = 1, amplitude: float = 1.65, offset: float = 1.65,
                 waveform: str = 'sine', rise_ratio: float = 0.5) -> None:
        """
        初始化波形发生器实例。

        该方法用于初始化波形发生器的基本设置，包括 DAC 对象、信号频率、幅度、偏移、波形类型及三角波的上升斜率。

        Args:
            dac (MCP4725): DAC芯片实例，用于生成波形信号。
            frequency (float, optional): 信号频率，默认值为 1 Hz。必须大于 0 并小于等于 10 Hz。
            amplitude (float, optional): 信号幅度，默认值为 1.65V。必须在 0 到 3.3V 之间。
            offset (float, optional): 直流偏移，默认值为 1.65V。必须在 0 到 3.3V 之间。
            waveform (str, optional): 波形类型，可以是 'sine'（正弦波）、'square'（方波）或 'triangle'（三角波），默认值为 'sine'。
            rise_ratio (float, optional): 三角波的上升斜率，默认为 0.5，值必须在 0 到 1 之间。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的参数不在预定范围内，将抛出该异常。

        ========================================

        Initializes the waveform generator instance.

        This method is used to initialize the basic settings of the waveform generator,
        including the DAC object, signal frequency, amplitude, offset, waveform type,
        and the rise slope for the triangle wave.

        Args:
            dac (MCP4725): The DAC chip instance used to generate the waveform signal.
            frequency (float, optional): The signal frequency, default is 1 Hz.
                                         It must be greater than 0 and less than or equal to 10 Hz.
            amplitude (float, optional): The signal amplitude, default is 1.65V.
                                         It must be between 0 and 3.3V.
            offset (float, optional): The DC offset, default is 1.65V.
                                      It must be between 0 and 3.3V.
            waveform (str, optional): The waveform type, which can be 'sine', 'square', or 'triangle'.
                                      The default value is 'sine'.
            rise_ratio (float, optional): The rise slope for the triangle wave, default is 0.5.
                                          The value must be between 0 and 1.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: This exception is raised if any of the input parameters are out of the valid range.

        """

        # 参数输入检查
        # 参数输入检查，确保频率在 0 到 10 Hz 之间
        if not (0 < frequency <= 10):
            raise ValueError("Frequency must be between 0 and 10 Hz.")
        # 检查幅度范围是否在 0 到 3.3V 之间
        if not (0 <= amplitude <= 3.3):
            raise ValueError("Amplitude must be between 0 and 3.3V.")
        # 检查直流偏移范围是否在 0 到 3.3V 之间
        if not (0 <= offset <= 3.3):
            raise ValueError("Offset must be between 0 and 3.3V.")
        # 确保幅度和偏移的和不超过 3.3V，防止输出超出 DAC 的范围
        if not(0 <= amplitude+offset <= 3.3):
            raise ValueError("Amplitude + offset must be between 0 and 3.3V.")
        # 检查波形类型是否是正弦波、方波或三角波
        if waveform not in ['sine', 'square', 'triangle']:
            raise ValueError("Waveform must be 'sine', 'square', or 'triangle'.")
        # 检查三角波上升沿比例是否在 0 到 1 之间
        if not (0 <= rise_ratio <= 1):
            raise ValueError("Rise ratio must be between 0 and 1.")

        # 保存DAC对象
        self.dac = dac

        # 初始化定时器对象，-1 表示在初始化时不绑定到任何硬件定时器
        self.timer = Timer(-1)

        # 保存波形生成器的参数
        self.frequency = frequency  # 信号频率
        self.amplitude = amplitude  # 信号幅度
        self.offset = offset  # 直流偏移
        self.waveform = waveform  # 波形类型
        self.rise_ratio = rise_ratio  # 三角波上升沿比例

        # 固定50个采样点，离散信号的采样点数量
        self.sample_rate = 50

        # 12位DAC的分辨率，意味着DAC输出范围是0到4095
        self.dac_resolution = 4095

        # 根据波形类型生成采样点数据
        self.samples = self.generate_samples()

        # 初始化当前采样点索引，用于逐步输出波形数据
        self.index = 0

    def generate_samples(self) -> list[int]:
        """
        根据波形类型生成采样点数据。

        该方法根据所选的波形类型（正弦波、方波、三角波）生成对应的采样点数据，并将每个采样点转换为 DAC 可接受的数值。

        Returns:
            list[int]: 包含转换为 DAC 数值的采样点列表。

        Raises:
            None: 此方法不会抛出异常。

        ========================================
        Generates sample data based on the selected waveform type.

        This method generates corresponding sample data based on the selected waveform type
        (sine wave, square wave, triangle wave) and converts each sample point to a value
        acceptable by the DAC.

        Returns:
            list[int]: A list of sample points converted to DAC values.

        Raises:
            None: This method does not raise any exceptions.

        """

        # 将电压值转换为DAC值的函数
        def to_dac_value(voltage):
            # 通过电压值计算对应的 DAC 输出值，DAC 分辨率为 4095，电压范围为 0 到 3.3V
            return int(voltage / 3.3 * self.dac_resolution)

        # 初始化一个列表用于存储生成的采样点数据
        samples = []

        # 根据选定的波形生成采样点数据
        if self.waveform == 'sine':
            # 正弦波：根据角度生成对应的电压值
            for i in range(self.sample_rate):
                # 计算当前采样点对应的角度，角度以 2π 为周期
                angle = 2 * math.pi * i / self.sample_rate
                # 根据正弦函数计算当前采样点的电压值
                voltage = self.offset + self.amplitude * math.sin(angle)
                # 将电压值转换为 DAC 对应的数值，并加入样本列表
                samples.append(to_dac_value(voltage))

        elif self.waveform == 'square':
            # 方波：根据采样点序号生成高低电平交替的电压值
            for i in range(self.sample_rate):
                # 前半周期电压为高电平，后半周期电压为低电平
                if i < self.sample_rate // 2:
                    voltage = self.offset + self.amplitude  # 高电平
                else:
                    voltage = self.offset - self.amplitude  # 低电平
                # 将电压值转换为 DAC 对应的数值，并加入样本列表
                samples.append(to_dac_value(voltage))

        elif self.waveform == 'triangle':
            # 三角波：根据上升沿和下降沿生成电压值
            for i in range(self.sample_rate):
                if i < self.sample_rate * self.rise_ratio:
                    # 上升沿，电压从 offset - amplitude 上升到 offset + amplitude
                    voltage = self.offset + 2 * self.amplitude * (
                            i / (self.sample_rate * self.rise_ratio)) - self.amplitude
                else:
                    # 下降沿，电压从 offset + amplitude 下降到 offset - amplitude
                    voltage = self.offset + 2 * self.amplitude * (
                            (self.sample_rate - i) / (self.sample_rate * (1 - self.rise_ratio))) - self.amplitude
                # 将电压值转换为 DAC 对应的数值，并加入样本列表
                samples.append(to_dac_value(voltage))

        # 返回生成的采样点数据列表
        return samples

    def update(self, t: Timer) -> None:
        """
        定时器回调函数，在定时器中断时调用，用于输出下一个采样点的数据。

        该方法在定时器中断时被调用，每次被调用时，它将当前采样点的数据写入 DAC，并更新索引以指向下一个采样点。

        Args:
            t (Timer): 定时器对象，表示触发回调的定时器。

        Returns:
            None: 此方法没有返回值。

        Raises:
            None: 此方法不会抛出异常。

        ========================================

        Timer callback function, called when the timer interrupt occurs, used to output the next sample point data.

        This method is called during a timer interrupt. Each time it is called, it writes the current sample point's data to the DAC
        and updates the index to point to the next sample point.

        Args:
            t (Timer): The timer object that triggered the callback.

        Returns:
            None: This method does not return any value.

        Raises:
            None: This method does not raise any exceptions.
        """

        # 将当前采样点的数据写入 DAC，生成对应的电压输出
        self.dac.write(self.samples[self.index])
        # 更新采样点索引，以指向下一个采样点
        self.index = (self.index + 1) % self.sample_rate

    def start(self) -> None:
        """
        启动波形生成器，开始定时器，周期性地生成并输出波形数据。

        该方法会启动定时器，在每个周期触发时调用回调函数，按预定频率输出波形数据。

        Args:
            None: 此方法不接受任何参数。

        Returns:
            None: 此方法没有返回值。

        Raises:
            None: 此方法不会抛出异常。

        =========================================

        Start the waveform generator and begin the timer to periodically generate and output waveform data.

        This method will start the timer, which triggers the callback function at each period, outputting waveform data at the predetermined frequency.

        Args:
            None: This method does not accept any arguments.

        Returns:
            None: This method does not return any value.

        Raises:
            None: This method does not raise any exceptions.
        """

        # 初始化定时器，以频率 freq*self.sample_rate 触发定时器中断
        self.timer.init(freq=self.frequency * self.sample_rate, mode=Timer.PERIODIC, callback=self.update)

    def stop(self) -> None:
        """
        停止波形生成器，停止定时器，停止波形数据的输出。

        该方法会停止定时器的工作，波形输出将暂停。

        Args:
            None: 此方法不接受任何参数。

        Returns:
            None: 此方法没有返回值。

        Raises:
            None: 此方法不会抛出异常。

        =========================================

        Stop the waveform generator, halt the timer, and stop the output of waveform data.

        This method will stop the timer, pausing the waveform output.

        Args:
            None: This method does not accept any arguments.

        Returns:
            None: This method does not return any value.

        Raises:
            None: This method does not raise any exceptions.
        """

        # 停止定时器，解除中断
        self.timer.deinit()
        # 将采样点索引复位为0，以确保下次启动时从第一个采样点开始
        self.index = 0

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================