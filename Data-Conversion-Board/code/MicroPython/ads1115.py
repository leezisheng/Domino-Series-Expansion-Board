# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2024/10/7 下午2:24   
# @Author  : 李清水            
# @File    : ads1115.py       
# @Description : 外置ADC芯片ADS1115驱动类
# 参考代码：https://github.com/robert-hh/ads1x15
# 这部分代码由 robert-hh 开发，采用 MIT 协议发布。

# ======================================== 导入相关模块 =========================================

# 导入时间相关模块
import time
# 导入MicroPython相关模块
from micropython import const
import micropython
# 导入硬件相关模块
from machine import Pin, I2C

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

# 自定义ADS1115类
class ADS1115:
    """
    ADS1115类用于控制ADS1115外置ADC芯片，通过I2C接口与传感器进行数据交互，读取模拟信号并转换为数字信号。

    Attributes:
        i2c (machine.I2C): 用于与ADS1115通信的I2C接口对象。
        address (int): ADS1115的I2C地址，默认为0x48。
        gain_index (int): 当前增益设置的索引值。
        alert_pin (Pin, optional): 警报引脚，提供外部中断通知。默认为None。
        callback (Callable, optional): 警报触发时的回调函数。默认为None。

    Class Variables:
        REGISTER_CONVERT (const): 转换寄存器的地址。
        REGISTER_CONFIG (const): 配置寄存器的地址。
        REGISTER_LOWTHRESH (const): 低阈值寄存器的地址。
        REGISTER_HITHRESH (const): 高阈值寄存器的地址。
        OS_MASK (const): 操作状态掩码。
        OS_SINGLE (const): 启动单次转换。
        OS_BUSY (const): 读取时转换进行中。
        OS_NOTBUSY (const): 读取时转换完成。
        MUX_MASK (const): 多路复用掩码。
        MUX_DIFF_0_1 (const): 差分输入：AIN0 - AIN1。
        MUX_DIFF_0_3 (const): 差分输入：AIN0 - AIN3。
        MUX_DIFF_1_3 (const): 差分输入：AIN1 - AIN3。
        MUX_DIFF_2_3 (const): 差分输入：AIN2 - AIN3。
        MUX_SINGLE_0 (const): 单端输入：AIN0。
        MUX_SINGLE_1 (const): 单端输入：AIN1。
        MUX_SINGLE_2 (const): 单端输入：AIN2。
        MUX_SINGLE_3 (const): 单端输入：AIN3。
        PGA_MASK (const): 程度增益掩码。
        PGA_6_144V (const): +/-6.144V 范围，增益 2/3。
        PGA_4_096V (const): +/-4.096V 范围，增益 1。
        PGA_2_048V (const): +/-2.048V 范围，增益 2。
        PGA_1_024V (const): +/-1.024V 范围，增益 4。
        PGA_0_512V (const): +/-0.512V 范围，增益 8。
        PGA_0_256V (const): +/-0.256V 范围，增益 16。
        MODE_MASK (const): 模式掩码。
        MODE_CONTIN (const): 连续转换模式。
        MODE_SINGLE (const): 单次转换模式。
        DR_MASK (const): 数据速率掩码。
        DR_8SPS (const): 8采样每秒。
        DR_16SPS (const): 16采样每秒。
        DR_32SPS (const): 32采样每秒。
        DR_64SPS (const): 64采样每秒。
        DR_128SPS (const): 128采样每秒。
        DR_250SPS (const): 250采样每秒。
        DR_475SPS (const): 475采样每秒。
        DR_860SPS (const): 860采样每秒。
        CMODE_MASK (const): 比较模式掩码。
        CMODE_TRAD (const): 传统比较器模式，带迟滞。
        CMODE_WINDOW (const): 窗口比较器模式。
        CPOL_MASK (const): 比较器极性掩码。
        CPOL_ACTVLOW (const): ALERT/RDY 引脚低电平激活。
        CPOL_ACTVHI (const): ALERT/RDY 引脚高电平激活。
        CLAT_MASK (const): 比较器锁存掩码。
        CLAT_NONLAT (const): 非锁存比较器。
        CLAT_LATCH (const): 锁存比较器。
        CQUE_MASK (const): 比较器队列掩码。
        CQUE_1CONV (const): 一次转换后触发 ALERT/RDY。
        CQUE_2CONV (const): 两次转换后触发 ALERT/RDY。
        CQUE_4CONV (const): 四次转换后触发 ALERT/RDY。
        CQUE_NONE (const): 禁用比较器，将 ALERT/RDY 拉高。
        GAINS (tuple): 增益设置对应的寄存器值。
        GAINS_V (tuple): 增益对应的电压范围。
        CHANNELS (dict): 通道对应的多路复用配置。
        RATES (tuple): 数据速率设置对应的寄存器值。

    Methods:
        __init__(i2c: machine.I2C, address: int = 0x48, gain: int = 2, alert_pin: Optional[int] = None, callback: Optional[Callable] = None):
            初始化 ADS1115 实例，并设置 I2C 地址、增益、警报引脚和回调函数。通过检查传入的 I2C 地址和增益值，确保其在有效范围内。

        _get_gain_register_value(gain: float) -> int:
            根据增益值返回对应的寄存器配置值。该方法用于将增益值映射为设备的寄存器配置。

        _irq_handler(pin: machine.Pin):
            内部中断处理程序。当警报引脚触发时，调用此方法执行回调函数（如果设置了回调函数）。

        read(rate: int = 4, channel1: int = 0, channel2: Optional[int] = None) -> int:
            从指定通道读取 ADC 转换结果，并返回原始值。根据设置的采样速率和通道，执行一次 ADC 转换。

        set_conv(rate: int = 4, channel1: int = 0, channel2: Optional[int] = None):
            设置转换速率和通道。配置 ADC 转换速率和所需的输入通道。

        raw_to_v(raw: int) -> float:
            将原始 ADC 值转换为电压值。使用设备的增益和量程，将原始读取值转换为相应的电压值。

        alert_start(rate: int = 4, channel1: int = 0, channel2: Optional[int] = None,
                    threshold_high: int = 0x4000, threshold_low: int = 0, latched: bool = False):
            启动警报并设置阈值。该方法配置警报功能，并定义警报触发的高/低阈值以及是否采用锁存模式。

        alert_read() -> int:
            读取警报触发的 ADC 值。通过读取警报引脚的状态，返回相关的 ADC 数据。

    ==================================================

    The ADS1115 class is used to control the ADS1115 external ADC chip, which communicates with sensors via I2C interface
    to read analog signals and convert them into digital signals.

    Attributes:
        i2c (machine.I2C): The I2C interface object used to communicate with the ADS1115.
        address (int): The I2C address of the ADS1115, default is 0x48.
        gain_index (int): The index value of the current gain setting.
        alert_pin (Pin, optional): The alert pin that provides external interrupt notifications, default is None.
        callback (Callable, optional): The callback function triggered by the alert, default is None.

    Class Variables:
        REGISTER_CONVERT (const): The address of the conversion register.
        REGISTER_CONFIG (const): The address of the configuration register.
        REGISTER_LOWTHRESH (const): The address of the low threshold register.
        REGISTER_HITHRESH (const): The address of the high threshold register.
        OS_MASK (const): The operation status mask.
        OS_SINGLE (const): Start a single conversion.
        OS_BUSY (const): Conversion in progress when reading.
        OS_NOTBUSY (const): Conversion complete when reading.
        MUX_MASK (const): The multiplexer mask.
        MUX_DIFF_0_1 (const): Differential input: AIN0 - AIN1 (default).
        MUX_DIFF_0_3 (const): Differential input: AIN0 - AIN3.
        MUX_DIFF_1_3 (const): Differential input: AIN1 - AIN3.
        MUX_DIFF_2_3 (const): Differential input: AIN2 - AIN3.
        MUX_SINGLE_0 (const): Single-ended input: AIN0.
        MUX_SINGLE_1 (const): Single-ended input: AIN1.
        MUX_SINGLE_2 (const): Single-ended input: AIN2.
        MUX_SINGLE_3 (const): Single-ended input: AIN3.
        PGA_MASK (const): The programmable gain amplifier mask.
        PGA_6_144V (const): +/-6.144V range, gain 2/3.
        PGA_4_096V (const): +/-4.096V range, gain 1.
        PGA_2_048V (const): +/-2.048V range, gain 2.
        PGA_1_024V (const): +/-1.024V range, gain 4.
        PGA_0_512V (const): +/-0.512V range, gain 8.
        PGA_0_256V (const): +/-0.256V range, gain 16.
        MODE_MASK (const): The mode mask.
        MODE_CONTIN (const): Continuous conversion mode.
        MODE_SINGLE (const): Single conversion mode.
        DR_MASK (const): The data rate mask.
        DR_8SPS (const): 8 samples per second.
        DR_16SPS (const): 16 samples per second.
        DR_32SPS (const): 32 samples per second.
        DR_64SPS (const): 64 samples per second.
        DR_128SPS (const): 128 samples per second (default).
        DR_250SPS (const): 250 samples per second.
        DR_475SPS (const): 475 samples per second.
        DR_860SPS (const): 860 samples per second.
        CMODE_MASK (const): The comparator mode mask.
        CMODE_TRAD (const): Traditional comparator mode with hysteresis (default).
        CMODE_WINDOW (const): Window comparator mode.
        CPOL_MASK (const): The comparator polarity mask.
        CPOL_ACTVLOW (const): ALERT/RDY pin is active low.
        CPOL_ACTVHI (const): ALERT/RDY pin is active high.
        CLAT_MASK (const): The comparator latch mask.
        CLAT_NONLAT (const): Non-latching comparator (default).
        CLAT_LATCH (const): Latching comparator.
        CQUE_MASK (const): The comparator queue mask.
        CQUE_1CONV (const): Trigger ALERT/RDY after one conversion.
        CQUE_2CONV (const): Trigger ALERT/RDY after two conversions.
        CQUE_4CONV (const): Trigger ALERT/RDY after four conversions.
        CQUE_NONE (const): Disable comparator and pull ALERT/RDY high.
        GAINS (tuple): The register values corresponding to gain settings.
        GAINS_V (tuple): The voltage ranges corresponding to each gain setting.
        CHANNELS (dict): The multiplexer configurations corresponding to the channels.
        RATES (tuple): The register values corresponding to the data rates.

    Methods:
        __init__(i2c: machine.I2C, address: int = 0x48, gain: int = 2, alert_pin: Optional[int] = None, callback: Optional[Callable] = None):
            Initializes the ADS1115 instance, setting the I2C address, gain, alert pin, and callback function. It ensures that the provided I2C address and gain values are within valid ranges.

        _get_gain_register_value(gain: float) -> int:
            Returns the corresponding register value for the given gain. This method maps the gain value to the device's register configuration.

        _irq_handler(pin: machine.Pin):
            Internal interrupt handler. When the alert pin is triggered, this method calls the callback function (if one is set).

        read(rate: int = 4, channel1: int = 0, channel2: Optional[int] = None) -> int:
            Reads the ADC conversion result from the specified channel and returns the raw value. It performs an ADC conversion based on the set sampling rate and channels.

        set_conv(rate: int = 4, channel1: int = 0, channel2: Optional[int] = None):
            Configures the conversion rate and channels. It sets the ADC conversion rate and the desired input channels.

        raw_to_v(raw: int) -> float:
            Converts the raw ADC value to a voltage. It uses the device's gain and range to convert the raw reading to the corresponding voltage value.

        alert_start(rate: int = 4, channel1: int = 0, channel2: Optional[int] = None,
                    threshold_high: int = 0x4000, threshold_low: int = 0, latched: bool = False):
            Starts the alert and sets the threshold values. This method configures the alert functionality and defines the high/low thresholds for triggering the alert, as well as whether it uses a latched mode.

        alert_read() -> int:
            Reads the ADC value triggered by the alert. It returns the corresponding ADC data by reading the status of the alert pin.
    """

    # 寄存器地址常量
    REGISTER_CONVERT = const(0x00)       # 转换寄存器
    REGISTER_CONFIG = const(0x01)        # 配置寄存器
    REGISTER_LOWTHRESH = const(0x02)     # 低阈值寄存器
    REGISTER_HITHRESH = const(0x03)      # 高阈值寄存器

    # 配置寄存器位掩码和常量
    OS_MASK = const(0x8000)              # 操作状态掩码
    OS_SINGLE = const(0x8000)            # 写入：启动单次转换
    OS_BUSY = const(0x0000)              # 读取：转换进行中
    OS_NOTBUSY = const(0x8000)           # 读取：转换完成

    MUX_MASK = const(0x7000)             # 多路复用掩码
    MUX_DIFF_0_1 = const(0x0000)         # 差分输入：AIN0 - AIN1（默认）
    MUX_DIFF_0_3 = const(0x1000)         # 差分输入：AIN0 - AIN3
    MUX_DIFF_1_3 = const(0x2000)         # 差分输入：AIN1 - AIN3
    MUX_DIFF_2_3 = const(0x3000)         # 差分输入：AIN2 - AIN3
    MUX_SINGLE_0 = const(0x4000)         # 单端输入：AIN0
    MUX_SINGLE_1 = const(0x5000)         # 单端输入：AIN1
    MUX_SINGLE_2 = const(0x6000)         # 单端输入：AIN2
    MUX_SINGLE_3 = const(0x7000)         # 单端输入：AIN3

    PGA_MASK = const(0x0E00)             # 程度增益掩码
    PGA_6_144V = const(0x0000)           # +/-6.144V 范围，增益 2/3
    PGA_4_096V = const(0x0200)           # +/-4.096V 范围，增益 1
    PGA_2_048V = const(0x0400)           # +/-2.048V 范围，增益 2（默认）
    PGA_1_024V = const(0x0600)           # +/-1.024V 范围，增益 4
    PGA_0_512V = const(0x0800)           # +/-0.512V 范围，增益 8
    PGA_0_256V = const(0x0A00)           # +/-0.256V 范围，增益 16

    MODE_MASK = const(0x0100)            # 模式掩码
    MODE_CONTIN = const(0x0000)          # 连续转换模式
    MODE_SINGLE = const(0x0100)          # 单次转换模式（默认）

    DR_MASK = const(0x00E0)              # 数据速率掩码
    DR_8SPS = const(0x0000)              # 8 采样每秒
    DR_16SPS = const(0x0020)             # 16 采样每秒
    DR_32SPS = const(0x0040)             # 32 采样每秒
    DR_64SPS = const(0x0060)             # 64 采样每秒
    DR_128SPS = const(0x0080)            # 128 采样每秒（默认）
    DR_250SPS = const(0x00A0)            # 250 采样每秒
    DR_475SPS = const(0x00C0)            # 475 采样每秒
    DR_860SPS = const(0x00E0)            # 860 采样每秒

    CMODE_MASK = const(0x0010)           # 比较模式掩码
    CMODE_TRAD = const(0x0000)           # 传统比较器模式，带迟滞（默认）
    CMODE_WINDOW = const(0x0010)         # 窗口比较器模式

    CPOL_MASK = const(0x0008)            # 比较器极性掩码
    CPOL_ACTVLOW = const(0x0000)         # ALERT/RDY 引脚低电平激活（默认）
    CPOL_ACTVHI = const(0x0008)          # ALERT/RDY 引脚高电平激活

    CLAT_MASK = const(0x0004)            # 比较器锁存掩码
    CLAT_NONLAT = const(0x0000)          # 非锁存比较器（默认）
    CLAT_LATCH = const(0x0004)           # 锁存比较器

    CQUE_MASK = const(0x0003)            # 比较器队列掩码
    CQUE_1CONV = const(0x0000)           # 一次转换后触发 ALERT/RDY
    CQUE_2CONV = const(0x0001)           # 两次转换后触发 ALERT/RDY
    CQUE_4CONV = const(0x0002)           # 四次转换后触发 ALERT/RDY
    CQUE_NONE = const(0x0003)            # 禁用比较器，将 ALERT/RDY 拉高（默认）

    # 增益设置对应的寄存器值
    GAINS = (
        PGA_6_144V,  # 2/3x
        PGA_4_096V,  # 1x
        PGA_2_048V,  # 2x
        PGA_1_024V,  # 4x
        PGA_0_512V,  # 8x
        PGA_0_256V   # 16x
    )

    # 增益对应的电压范围
    GAINS_V = (
        6.144,  # 2/3x
        4.096,  # 1x
        2.048,  # 2x
        1.024,  # 4x
        0.512,  # 8x
        0.256   # 16x
    )

    # 通道对应的多路复用配置
    CHANNELS = {
        (0, None): MUX_SINGLE_0,
        (1, None): MUX_SINGLE_1,
        (2, None): MUX_SINGLE_2,
        (3, None): MUX_SINGLE_3,
        (0, 1): MUX_DIFF_0_1,
        (0, 3): MUX_DIFF_0_3,
        (1, 3): MUX_DIFF_1_3,
        (2, 3): MUX_DIFF_2_3,
    }

    # 数据速率设置对应的寄存器值
    RATES = (
        DR_8SPS,     # 8 采样每秒
        DR_16SPS,    # 16 采样每秒
        DR_32SPS,    # 32 采样每秒
        DR_64SPS,    # 64 采样每秒
        DR_128SPS ,  # 128 采样每秒（默认）
        DR_250SPS,   # 250 采样每秒
        DR_475SPS,   # 475 采样每秒
        DR_860SPS    # 860 采样每秒
    )

    def __init__(self, i2c: I2C, address: int = 0x48, gain: int = 2, alert_pin: int =None, callback: callable = None) -> None:
        """
        初始化 ADS1115 实例。

        该方法用于初始化 ADS1115 模块的基本设置，包括 I2C 地址、增益值、警报引脚以及警报回调函数。

        Args:
            i2c (machine.I2C): I2C 对象，用于与 ADS1115 通信。
            address (int, optional): ADS1115 的 I2C 地址，默认 0x48。
            gain (int, optional): 增益设置，决定输入电压范围，默认值为 2，对应 +/-2.048V。
            alert_pin (int, optional): 警报引脚编号，当设置时，用于接收警报信号。默认为 None。
            callback (callable, optional): 当警报引脚触发时，调用的回调函数。默认为 None。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的增益值或I2C通信地址不在预定的范围内，将抛出该异常。

        ============================================

        Initialize the ADS1115 instance.

        This method initializes the basic settings of the ADS1115 module, including the I2C address, gain value, alert pin, and alert callback function.

        Args:
            i2c (machine.I2C): The I2C object used for communication with the ADS1115.
            address (int, optional): The I2C address of the ADS1115, default is 0x48.
            gain (int, optional): The gain setting that determines the input voltage range. The default value is 2, corresponding to +/-2.048V.
            alert_pin (int, optional): The pin number for the alert signal. When set, it is used to receive the alert signal. Default is None.
            callback (callable, optional): A callback function that is called when the alert pin is triggered. Default is None.

        Returns:
            None: This method has no return value.

        Raises:
            ValueError: This exception is raised if the provided gain value or I2C communication address is outside the valid range.

        """

        # 判断ads1115的I2C通信地址是否为0x48、0x49、0x4A或0x4B
        if not 0x48 <= address <= 0x4B:
            raise ValueError("Invalid I2C address: 0x{:02X}".format(address))

        # 判断增益是否为2/3、1、2、4、8或16
        if gain not in (2/3, 1, 2, 4, 8, 16):
            raise ValueError("Invalid gain: {}".format(gain))

        # 存储 I2C 对象
        self.i2c = i2c
        # 存储设备地址
        self.address = address
        # 存储增益设置的索引
        try:
            self.gain_index = ADS1115.GAINS.index(self._get_gain_register_value(gain))
        except ValueError:
            raise ValueError("Gain setting not found in GAINS tuple.")

        # 临时存储字节数组，用于读写操作
        self.temp2 = bytearray(2)

        # 如果设置了警报引脚
        if alert_pin is not None:
            # 设置 ALERT 引脚为输入
            self.alert_pin = Pin(alert_pin, Pin.IN)
            # 存储用户回调函数
            self.callback = callback
            # 默认触发模式为下降沿
            self.alert_trigger = Pin.IRQ_FALLING
            # 设置中断处理程序
            self.alert_pin.irq(handler=lambda p: self._irq_handler(p), trigger=self.alert_trigger)

    def _get_gain_register_value(self, gain: float) -> int:
        """
        根据增益值返回对应的寄存器配置值。

        该方法将增益值映射到相应的 ADS1115 寄存器配置值。

        Args:
            gain (float): 增益值，可能的值为 2/3、1、2、4、8、16。

        Returns:
            int: 对应的寄存器配置值。

        Raises:
            KeyError: 如果传入的增益值不在预定义的增益映射表中，抛出该异常。

        ============================================

        Returns the corresponding register configuration value based on the gain value.

        This method maps the gain value to the corresponding ADS1115 register configuration value.

        Args:
            gain (float): The gain value, possible values are 2/3, 1, 2, 4, 8, 16.

        Returns:
            int: The corresponding register configuration value.

        Raises:
            KeyError: This exception is raised if the provided gain value is not in the predefined gain mapping table.

        """

        gain_map = {
            2/3: ADS1115.GAINS[0],
            1:   ADS1115.GAINS[1],
            2:   ADS1115.GAINS[2],
            4:   ADS1115.GAINS[3],
            8:   ADS1115.GAINS[4],
            16:  ADS1115.GAINS[5]
        }
        return gain_map[gain]

    def _irq_handler(self, pin: Pin) -> None:
        """
        内部中断处理程序，使用 micropython.schedule 调度用户回调。

        当中断触发时，调用用户定义的回调函数（如果存在），通过
        micropython.schedule 安排回调函数的执行。

        Args:
            pin (machine.Pin): 触发中断的引脚对象。

        Returns:
            None: 此方法没有返回值。

        ============================================

        Internal interrupt handler, uses micropython.schedule to schedule the user callback.

        When the interrupt is triggered, the user-defined callback function (if any) is called,
        and the execution of the callback function is scheduled via micropython.schedule.

        Args:
            pin (machine.Pin): The pin object that triggered the interrupt.

        Returns:
            None: This method does not return any value.

        """
        if hasattr(self, 'callback') and self.callback:
            micropython.schedule(self.callback, pin)

    def _write_register(self, register: int, value: int) -> None:
        """
        写入寄存器。

        该方法将指定值写入到给定的寄存器地址。

        Args:
            register (int): 寄存器地址。
            value (int): 要写入的值。

        Returns:
            None: 此方法没有返回值。

        ============================================

        Write to a register.

        This method writes the specified value to the given register address.

        Args:
            register (int): The register address.
            value (int): The value to be written.

        Returns:
            None: This method does not return any value.

        """
        # 取value的高八字节
        self.temp2[0] = (value >> 8) & 0xFF
        # 取value的低八字节
        self.temp2[1] = value & 0xFF
        # 写入寄存器
        self.i2c.writeto_mem(self.address, register, self.temp2)

    def _read_register(self, register: int) -> int:
        """
        读取寄存器的值。

        该方法从指定的寄存器读取数据，并将其返回。

        Args:
            register (int): 寄存器地址。

        Returns:
            int: 读取到的寄存器值。

        ============================================

        Read the value of a register.

        This method reads data from the specified register and returns it.

        Args:
            register (int): The register address.

        Returns:
            int: The value read from the register.

        """
        # 读取寄存器
        self.i2c.readfrom_mem_into(self.address, register, self.temp2)
        # 合并高低字节并返回
        return (self.temp2[0] << 8) | self.temp2[1]

    def raw_to_v(self, raw: int) -> float:
        """
        将原始 ADC 值转换为电压。

        该方法将原始 ADC 值转换为对应的电压值。

        Args:
            raw (int): 原始 ADC 值。

        Returns:
            float: 转换后的电压值。

        ============================================

        Convert raw ADC value to voltage.

        This method converts the raw ADC value to the corresponding voltage.

        Args:
            raw (int): The raw ADC value.

        Returns:
            float: The converted voltage value.

        """
        # 计算每位电压值
        v_p_b = ADS1115.GAINS_V[self.gain_index] / 32768
        # 返回转换后的电压
        return raw * v_p_b

    def set_conv(self, rate: int = 4, channel1: int = 0, channel2: int = None) -> None:
        """
        设置转换速率和通道。

        该方法配置数据采样速率和选择要使用的输入通道。根据给定的参数配置转换器的工作模式。

        Args:
            rate (int, optional): 数据速率索引，默认 4 对应 128 SPS。
            channel1 (int, optional): 主通道编号，默认 0。
            channel2 (int, optional): 差分通道编号，默认为 None。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果采样率或通道设置无效，则抛出异常。

        ===========================================

        Set the conversion rate and channels.

        This method configures the data sampling rate and selects the input channels to be used.
        It sets up the converter's operation mode based on the provided parameters.

        Args:
            rate (int, optional): The data rate index, default is 4, corresponding to 128 SPS.
            channel1 (int, optional): The primary channel number, default is 0.
            channel2 (int, optional): The differential channel number, default is None.

        Returns:
            None: This method has no return value.

        Raises:
            ValueError: If the sampling rate or channel settings are invalid, an exception is raised.

        """
        # 判断采样率是否设置正确
        if rate not in range(len(ADS1115.RATES)):
            raise ValueError("Invalid rate: {}".format(rate))
        # 判断通道是否设置正确
        if channel1 not in range(4) or (channel2 is not None and channel2 not in range(4)):
            raise ValueError("Invalid channel: {}".format(channel1))

        # 配置寄存器值
        self.mode = (ADS1115.CQUE_NONE      | ADS1115.CLAT_NONLAT |
                     ADS1115.CPOL_ACTVLOW   | ADS1115.CMODE_TRAD |
                     ADS1115.RATES[rate]    | ADS1115.MODE_SINGLE |
                     ADS1115.OS_SINGLE      | ADS1115.GAINS[self.gain_index] |
                     ADS1115.CHANNELS.get((channel1, channel2), ADS1115.MUX_SINGLE_0))

    def read(self, rate: int = 4, channel1: int = 0, channel2: int = None) -> int:
        """
        读取指定通道的 ADC 值。

        该方法根据给定的速率和通道配置读取 ADC 转换结果，并返回转换结果的原始值。

        Args:
            rate (int, optional): 数据速率索引，默认 4 对应 128 SPS。
            channel1 (int, optional): 主通道编号，默认 0。
            channel2 (int, optional): 差分通道编号，默认为 None。

        Returns:
            int: ADC 原始值，如果为负值则进行补偿。

        Raises:
            ValueError: 如果采样率或通道设置无效，则抛出异常。

        ============================================

        Read the ADC value from the specified channel.

        This method reads the ADC conversion result based on the given rate and channel configuration
        and returns the raw conversion result.

        Args:
            rate (int, optional): The data rate index, default is 4, corresponding to 128 SPS.
            channel1 (int, optional): The primary channel number, default is 0.
            channel2 (int, optional): The differential channel number, default is None.

        Returns:
            int: The raw ADC value, with compensation if the value is negative.

        Raises:
            ValueError: If the sampling rate or channel settings are invalid, an exception is raised.

        """
        # 判断采样率是否设置正确
        if rate not in range(len(ADS1115.RATES)):
            raise ValueError("Invalid rate: {}".format(rate))

        # 判断通道是否设置正确
        if channel1 not in range(4) or (channel2 is not None and channel2 not in range(4)):
            raise ValueError("Invalid channel: {}".format(channel1))

        # 写入配置寄存器，启动转换
        self._write_register(
            ADS1115.REGISTER_CONFIG,
            (ADS1115.CQUE_NONE      | ADS1115.CLAT_NONLAT |
             ADS1115.CPOL_ACTVLOW   | ADS1115.CMODE_TRAD |
             ADS1115.RATES[rate]    | ADS1115.MODE_SINGLE |
             ADS1115.OS_SINGLE      | ADS1115.GAINS[self.gain_index] |
             ADS1115.CHANNELS.get((channel1, channel2), ADS1115.MUX_SINGLE_0))
        )
        # 等待转换完成
        while not (self._read_register(ADS1115.REGISTER_CONFIG) & ADS1115.OS_NOTBUSY):
            # 每次等待 1 毫秒
            time.sleep_ms(1)
        # 读取转换结果
        res = self._read_register(ADS1115.REGISTER_CONVERT)
        # 返回有符号结果
        return res if res < 32768 else res - 65536

    def read_rev(self) -> int:
        """
        读取转换结果并启动下一个转换。

        该方法读取最新的转换结果，并自动启动下一个转换。

        Returns:
            int: ADC 原始值，如果为负值则进行补偿。

        ============================================

        Read the conversion result and start the next conversion.

        This method reads the latest conversion result and automatically starts the next conversion.

        Returns:
            int: The raw ADC value, with compensation if the value is negative.

        """
        # 读取转换结果
        res = self._read_register(ADS1115.REGISTER_CONVERT)
        # 启动下一个转换
        self._write_register(ADS1115.REGISTER_CONFIG, self.mode)
        # 返回有符号结果
        return res if res < 32768 else res - 65536

    def alert_start(self, rate: int = 4, channel1: int = 0, channel2: int = None,
                    threshold_high: int = 0x4000, threshold_low: int = 0, latched: bool = False) -> None:
        """
        启动持续测量，并设置 ALERT 引脚的阈值。

        该方法用于启动一个持续的测量过程，并且设置 ALERT 引脚的高低阈值，当采样值超出这些阈值时会触发警报。

        Args:
            rate (int, optional): 数据速率索引，默认 4 对应 1600/128 SPS。
            channel1 (int, optional): 主通道编号，默认为 0。
            channel2 (int, optional): 差分通道编号，默认为 None，表示不使用差分通道。
            threshold_high (int, optional): 高阈值，默认为 0x4000。
            threshold_low (int, optional): 低阈值，默认为 0。
            latched (bool, optional): 是否锁存 ALERT 引脚，默认为 False，不锁存。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的采样率、通道或阈值设置不正确，将抛出该异常。

        ============================================

        Start continuous measurement and set the ALERT pin thresholds.

        This method starts a continuous measurement process and sets the high and low thresholds for the ALERT pin.
        An alert will be triggered when the sampled value exceeds these thresholds.

        Args:
            rate (int, optional): Data rate index, default is 4 corresponding to 1600/128 SPS.
            channel1 (int, optional): Primary channel number, default is 0.
            channel2 (int, optional): Differential channel number, default is None, indicating no differential channel.
            threshold_high (int, optional): High threshold, default is 0x4000.
            threshold_low (int, optional): Low threshold, default is 0.
            latched (bool, optional): Whether to latch the ALERT pin, default is False (no latch).

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: If the provided sampling rate, channel, or threshold settings are invalid, this exception will be raised.

        """

        # 判断采样率是否设置正确
        if rate not in range(len(ADS1115.RATES)):
            raise ValueError("Invalid rate: {}".format(rate))

        # 判断通道是否设置正确
        if channel1 not in range(4) or (channel2 is not None and channel2 not in range(4)):
            raise ValueError("Invalid channel: {}".format(channel1))

        # 判断阈值是否正确设置
        if threshold_high < threshold_low:
            raise ValueError("Invalid threshold: {} > {}".format(threshold_high, threshold_low))

        # 设置低阈值寄存器
        self._write_register(ADS1115.REGISTER_LOWTHRESH, threshold_low)
        # 设置高阈值寄存器
        self._write_register(ADS1115.REGISTER_HITHRESH, threshold_high)

        # 配置 ALERT 引脚和比较器
        self._write_register(
            ADS1115.REGISTER_CONFIG,
            (ADS1115.CQUE_1CONV |
             (ADS1115.CLAT_LATCH if latched else ADS1115.CLAT_NONLAT) |
             ADS1115.CPOL_ACTVLOW | ADS1115.CMODE_TRAD |
             ADS1115.RATES[rate] | ADS1115.MODE_CONTIN |
             ADS1115.GAINS[self.gain_index] |
             ADS1115.CHANNELS.get((channel1, channel2), ADS1115.MUX_SINGLE_0))
        )

    def conversion_start(self, rate: int = 4, channel1: int = 0, channel2: int = None) -> None:
        """
        启动持续测量，基于 ALERT/RDY 引脚触发。

        该方法启动持续的 ADC 转换，通过 ALERT/RDY 引脚触发结果。

        Args:
            rate (int, optional): 数据速率索引，默认 4 对应 1600/128 SPS。
            channel1 (int, optional): 主通道编号，默认为 0。
            channel2 (int, optional): 差分通道编号，默认为 None，表示不使用差分通道。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的采样率或通道设置不正确，将抛出该异常。

        ===================================================

        Start continuous measurement triggered by ALERT/RDY pin.

        This method starts continuous ADC conversion, with the results triggered by the ALERT/RDY pin.

        Args:
            rate (int, optional): Data rate index, default is 4 corresponding to 1600/128 SPS.
            channel1 (int, optional): Primary channel number, default is 0.
            channel2 (int, optional): Differential channel number, default is None, meaning no differential channel.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: If the provided sampling rate or channel settings are incorrect, this exception will be raised.

        """
        # 判断采样率是否设置正确
        if rate not in range(len(ADS1115.RATES)):
            raise ValueError("Invalid rate: {}".format(rate))

        # 判断通道是否设置正确
        if channel1 not in range(4) or (channel2 is not None and channel2 not in range(4)):
            raise ValueError("Invalid channel: {}".format(channel1))

        # 设置低阈值为 0
        self._write_register(ADS1115.REGISTER_LOWTHRESH, 0)
        # 设置高阈值为 0x8000
        self._write_register(ADS1115.REGISTER_HITHRESH, 0x8000)

        # 配置 ALERT 引脚和比较器，启动转换
        self._write_register(
            ADS1115.REGISTER_CONFIG,
            (ADS1115.CQUE_1CONV | ADS1115.CLAT_NONLAT |
             ADS1115.CPOL_ACTVLOW | ADS1115.CMODE_TRAD |
             ADS1115.RATES[rate] | ADS1115.MODE_CONTIN |
             ADS1115.GAINS[self.gain_index] |
             ADS1115.CHANNELS.get((channel1, channel2), ADS1115.MUX_SINGLE_0))
        )

    def alert_read(self) -> int:
        """
        从持续测量中获取最后一次读取的转换结果。

        该方法用于从 ADC 获取最后一次转换的结果，如果返回的是负值，将进行补偿处理。

        Returns:
            int: ADC 原始值，若为负值则进行补偿，范围 -32768 到 32767。

        Raises:
            None: 该方法没有引发异常。

        ============================================

        Retrieve the last conversion result from continuous measurement.

        This method is used to get the most recent conversion result from the ADC. If the result is negative, compensation will be applied.

        Returns:
            int: Raw ADC value, with compensation applied if negative, range -32768 to 32767.

        Raises:
            None: This method does not raise any exceptions.

        """

        # 读取转换结果
        res = self._read_register(ADS1115.REGISTER_CONVERT)
        # 返回有符号结果
        return res if res < 32768 else res - 65536

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ============================================