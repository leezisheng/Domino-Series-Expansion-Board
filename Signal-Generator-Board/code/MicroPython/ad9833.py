# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2024/9/3 下午2:20   
# @Author  : 李清水            
# @File    : ad9833.py       
# @Description : DDS信号芯片AD9833驱动模块
# 代码参考：https://github.com/owainm713/AD9833-MicroPython-Module/blob/main/AD9833example.py#L54
# 这部分代码由 owainm713 开发，采用 GNU General Public License v3.0 License.

# ======================================== 导入相关模块 =========================================

# 导入硬件相关模块
import machine
# 导入数字信号处理相关模块
from math import pi, radians

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

# DDS信号芯片AD9833自定义类
class AD9833:
    """
    AD9833类用于控制AD9833波形发生器芯片，通过SPI接口与主控芯片进行通信，配置输出的波形、频率和相位。

    该类提供了控制AD9833的各种功能，包括设置输出波形类型（正弦波、方波、三角波）、调整频率、相位，并且允许在运行时动态修改波形的参数。

    Attributes:
        fmclk (int): 主时钟频率，单位为Hz，默认为25MHz。
        sdo (machine.Pin): SPI数据输出引脚，用于传输数据。
        clk (machine.Pin): SPI时钟引脚，控制数据传输的时序。
        cs (machine.Pin): SPI片选引脚，用于选择AD9833芯片。
        spi (machine.SPI): SPI通信对象，用于与AD9833进行数据传输。
        mode (str): 当前模式，默认为"RESET"，控制AD9833的工作状态。
        writeMode (str): 写入模式，默认为同时写入MSB和LSB，用于设置频率和相位。
        freq0 (int): 频率寄存器0的值，用于存储设置的频率。
        freq1 (int): 频率寄存器1的值，用于存储设置的频率。
        phase0 (int): 相位寄存器0的值，用于控制信号相位。
        phase1 (int): 相位寄存器1的值，用于控制信号相位。

    Methods:
        __init__(sdo: int, clk: int, cs: int, fmclk: int = 25):
            初始化AD9833实例并设置SPI通信对象和主时钟频率。

        set_control_reg(**kwargs) -> None:
            设置AD9833的控制寄存器，控制芯片的工作模式，如复位、波形类型等。

        write_data(data: int) -> None:
            向AD9833写入指定的数据。

        set_frequency(reg: int, freq: int) -> None:
            设置AD9833的频率寄存器，控制输出波形的频率。

        set_phase(reg: int, phase: int) -> None:
            设置AD9833的相位寄存器，控制输出波形的相位。

        reset() -> None:
            复位AD9833，重新初始化所有寄存器和设置。

    ==================================================

    The AD9833 class is used to control the AD9833 waveform generator chip, communicating with the main microcontroller via the SPI interface to configure the output waveform, frequency, and phase.

    This class provides various functions to control the AD9833, including setting the output waveform type (sine wave, square wave, triangle wave), adjusting frequency and phase, and allowing dynamic modification of the waveform parameters at runtime.

    Attributes:
        fmclk (int): The main clock frequency in Hz, default is 25MHz.
        sdo (machine.Pin): The SPI data output pin, used for transmitting data.
        clk (machine.Pin): The SPI clock pin, controlling the timing of data transfer.
        cs (machine.Pin): The SPI chip select pin, used to select the AD9833 chip.
        spi (machine.SPI): The SPI communication object, used for data transmission with the AD9833.
        mode (str): The current mode, default is "RESET", controlling the AD9833's working state.
        writeMode (str): The write mode, default is writing both MSB and LSB simultaneously, used for setting frequency and phase.
        freq0 (int): The value of frequency register 0, used to store the set frequency.
        freq1 (int): The value of frequency register 1, used to store the set frequency.
        phase0 (int): The value of phase register 0, used to control the signal's phase.
        phase1 (int): The value of phase register 1, used to control the signal's phase.

    Methods:
        __init__(sdo: int, clk: int, cs: int, fmclk: int = 25):
            Initializes the AD9833 instance and sets up the SPI communication object and the main clock frequency.

        set_control_reg(**kwargs) -> None:
            Sets the control register of the AD9833, controlling the chip's working mode, such as reset and waveform type.

        write_data(data: int) -> None:
            Writes the specified data to the AD9833.

        set_frequency(reg: int, freq: int) -> None:
            Sets the frequency register of the AD9833, controlling the output waveform's frequency.

        set_phase(reg: int, phase: int) -> None:
            Sets the phase register of the AD9833, controlling the output waveform's phase.

        reset() -> None:
            Resets the AD9833, reinitializing all registers and settings.
    """

    def __init__(self, sdo: int, clk: int, cs: int, fmclk: int = 25) -> None:
        """
        初始化AD9833实例。

        该方法用于初始化AD9833模块的基本设置，包括SPI通信引脚和主时钟频率。

        Args:
            sdo (int): SDATA引脚对应编号。
            clk (int): CLK引脚对应编号。
            cs (int): CS引脚对应编号。
            fmclk (int, optional): 主时钟频率，实际工作频率为 fmclk MHz，默认为25 MHz。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的sdo、clk或cs参数不是有效的数字引脚编号，则抛出该异常。

        ================================================

        Initializes the AD9833 instance.

        This method initializes the basic settings of the AD9833 module, including the SPI communication pins and the main clock frequency.

        Args:
            sdo (int): The pin index corresponding to the SDATA (data output) pin.
            clk (int): The pin index corresponding to the CLK (clock) pin.
            cs (int): The pin index corresponding to the CS (chip select) pin.
            fmclk (int, optional): The main clock frequency in MHz, the actual operating frequency is fmclk MHz, default is 25 MHz.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the passed sdo, clk, or cs parameters are not valid pin numbers, this exception will be raised.

        """

        # 如果输入的sdo、clk、cs参数不是数字引脚编号，则报错
        if not isinstance(sdo, int) or not isinstance(clk, int) or not isinstance(cs, int):
            raise ValueError("sdo、clk、cs must be int")

        # 设置时钟频率（默认为25 MHz）
        self.fmclk = fmclk * 10 ** 6

        # 设置SPI引脚的相关参数
        self.sdo = machine.Pin(sdo)
        self.clk = machine.Pin(clk)
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        # 初始化片选引脚为高电平，表示没有开始通信
        self.cs.value(1)
        # 设置SPI通信参数
        self.spi = machine.SPI(0, baudrate=4000000, polarity=1, phase=1, sck=self.clk, mosi=self.sdo)
        # 初始化控制寄存器，设置为复位状态，并且频率寄存器写模式为28位数据写入模式
        self.set_control_reg(B28=1, RESET=1)

        # 初始化模式为复位
        self.mode = "RESET"
        # 初始化写入模式为同时写入MSB和LSB
        self.writeMode = "BOTH"
        # 初始化频率寄存器0和寄存器1的值
        self.freq0 = 0
        self.freq1 = 0
        # 初始化相位寄存器0和寄存器1的值
        self.phase0 = 0
        self.phase1 = 0

    def write_data(self, data: int) -> None:
        """
        将数据写入AD9833寄存器。

        该方法用于将给定的整数数据写入AD9833的寄存器，以便更新其配置或控制波形。

        Args:
            data (int): 写入到AD9833寄存器的相关数据，必须为一个整数。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的data参数不是整数类型，则抛出该异常。

        ==============================================

        Writes data to the AD9833 register.

        This method writes the provided integer data to the AD9833 register to update its configuration or control the waveform.

        Args:
            data (int): The data to be written to the AD9833 register, must be an integer.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the passed data is not of integer type, this exception will be raised.

        """

        # 将数据转换为字节数组
        data = bytearray(data)

        # 将片选引脚拉低，开始通信
        self.cs.value(0)
        # 调整SPI速率
        self.spi.init(baudrate=4000000)
        # 通过SPI写入数据
        self.spi.write(data)
        # 将片选引脚拉高，结束通信
        self.cs.value(1)

        return

    def set_control_reg(self, B28: int = 1, HLB: int = 0, FS: int = 0, PS: int = 0,
                        RESET: int = 0, SLP1: int = 0, SLP12: int = 0, OP: int = 0, DIV2: int = 0, MODE: int = 0) -> None:
        """
        设置控制寄存器的各个位值，用于配置AD9833的工作状态。

        该方法根据传入的参数，设置AD9833控制寄存器中的各个位，以控制设备的复位状态、输出模式、频率寄存器和相位寄存器等功能。

        Args:
            B28 (int, optional): 设置B28位，用于频率寄存器写入模式，默认为 1。
            HLB (int, optional): 设置HLB位，用于高/低字节切换，默认为 0。
            FS (int, optional): 设置FS位，选择频率寄存器，默认为 0。
            PS (int, optional): 设置PS位，选择相位寄存器，默认为 0。
            RESET (int, optional): 设置RESET位，复位状态控制，默认为 0。
            SLP1 (int, optional): 设置SLP1位，用于睡眠模式，默认为 0。
            SLP12 (int, optional): 设置SLP12位，用于睡眠模式，默认为 0。
            OP (int, optional): 设置OP位，用于输出模式选择，默认为 0。
            DIV2 (int, optional): 设置DIV2位，输出频率减半，默认为 0。
            MODE (int, optional): 设置MODE位，选择输出波形模式，默认为 0。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的参数不是0或1的整数值，将抛出该异常。

        ==============================================

        Sets the bit values in the control register to configure the AD9833's operation state.

        This method sets various bits in the AD9833 control register based on the passed parameters to control the reset state, output mode, frequency and phase register selection, etc.

        Args:
            B28 (int, optional): Set the B28 bit for frequency register write mode, default is 1.
            HLB (int, optional): Set the HLB bit for high/low byte switching, default is 0.
            FS (int, optional): Set the FS bit to select the frequency register, default is 0.
            PS (int, optional): Set the PS bit to select the phase register, default is 0.
            RESET (int, optional): Set the RESET bit for reset state control, default is 0.
            SLP1 (int, optional): Set the SLP1 bit for sleep mode, default is 0.
            SLP12 (int, optional): Set the SLP12 bit for sleep mode, default is 0.
            OP (int, optional): Set the OP bit for output mode selection, default is 0.
            DIV2 (int, optional): Set the DIV2 bit for halving the output frequency, default is 0.
            MODE (int, optional): Set the MODE bit for selecting output waveform mode, default is 0.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If any of the passed parameters is not an integer value of 0 or 1, this exception will be raised.

        """

        # 如果输入的寄存器参数不是0或1，则抛出异常
        if B28 != 0 and B28 != 1:
            raise ValueError("B28 must be 0 or 1")
        if HLB != 0 and HLB != 1:
            raise ValueError("HLB must be 0 or 1")
        if FS != 0 and FS != 1:
            raise ValueError("FS must be 0 or 1")
        if PS != 0 and PS != 1:
            raise ValueError("PS must be 0 or 1")
        if RESET != 0 and RESET != 1:
            raise ValueError("RESET must be 0 or 1")
        if SLP1 != 0 and SLP1 != 1:
            raise ValueError("SLP1 must be 0 or 1")
        if SLP12 != 0 and SLP12 != 1:
            raise ValueError("SLP12 must be 0 or 1")
        if OP != 0 and OP != 1:
            raise ValueError("OP must be 0 or 1")
        if DIV2 != 0 and DIV2 != 1:
            raise ValueError("DIV2 must be 0 or 1")
        if MODE != 0 and MODE != 1:
            raise ValueError("MODE must be 0 or 1")

        # 设置控制寄存器参数
        self.B28 = B28
        self.HLB = HLB
        self.FS = FS
        self.PS = PS
        self.RESET = RESET
        self.SLP1 = SLP1
        self.SLP12 = SLP12
        self.OP = OP
        self.DIV2 = DIV2
        self.MODE = MODE

        # 将所有位拼接成控制寄存器的值
        controlReg = (B28 << 13) + (HLB << 12) + (FS << 11) + (PS << 10) + (RESET << 8) + (SLP1 << 7) + (SLP12 << 6) + (
                    OP << 5) + (DIV2 << 3) + (MODE << 1)

        # 将控制寄存器值拆分为两个字节，通过两次SPI写入进行发送
        controlRegList = [(controlReg & 0xFF00) >> 8, controlReg & 0x00FF]
        # 写入控制寄存器的数据
        self.write_data(controlRegList)

        return

    def set_frequency(self, fout: int, freqSelect: int) -> None:
        """
        设置频率寄存器的值，选择并更新AD9833的输出频率。

        根据传入的输出频率和选择的频率寄存器，计算并更新AD9833的频率寄存器。支持选择频率寄存器0或1进行更新。

        Args:
            fout (int): 设定的信号输出频率，单位为Hz，范围为0至12.5MHz。
            freqSelect (int): 选择要写入的频率寄存器，取值为0或1，表示频率寄存器0或1。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的`freqSelect`不是0或1，或者`fout`不在有效频率范围内（0至12.5MHz），则抛出该异常。

        ==============================================

        Sets the frequency register value to select and update the AD9833 output frequency.

        This method calculates and updates the frequency register based on the given output frequency and selected frequency register. It supports updating either frequency register 0 or 1.

        Args:
            fout (int): The desired output frequency in Hz, within the range of 0 to 12.5 MHz.
            freqSelect (int): The frequency register to update, where 0 selects frequency register 0 and 1 selects frequency register 1.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the `freqSelect` is not 0 or 1, or if `fout` is outside the valid frequency range (0 to 12.5 MHz), this exception will be raised.

        """
        # 如果freqSelect不是0或者1，则抛出异常
        if freqSelect != 0 and freqSelect != 1:
            raise ValueError("freqSelect must be 0 or 1")

        # 判断输入频率是否在0到12.5MHz之间，若不是则抛出异常
        if fout < 0 or fout > 12500000:
            raise ValueError("fout must be 0 to 12.5MHz")

        # 计算频率寄存器需要写入的值
        freqR = int((fout * pow(2, 28)) / self.fmclk)

        # 将频率寄存器的值拆分为两个14位段：fMSB高14位和fLSB低14位
        fMSB = (freqR & 0xFFFC000) >> 14
        fLSB = freqR & 0x3FFF

        # 添加寄存器地址到每个14位段
        if freqSelect == 0:
            # 选择频率寄存器0
            addr = 0b01
            # 存储设置的频率值
            self.freq0 = fout
        else:
            # 选择频率寄存器1
            addr = 0b10
            # 存储设置的频率值
            self.freq1 = fout

        # 高14位段加上寄存器地址
        fMSB = fMSB + (addr << 14)
        # 低14位段加上寄存器地址
        fLSB = fLSB + (addr << 14)

        # 将fMSB和fLSB各自拆分为两个8位段
        fLSBList = [(fLSB & 0xFF00) >> 8, fLSB & 0x00FF]
        fMSBList = [(fMSB & 0xFF00) >> 8, fMSB & 0x00FF]
        fBoth = fLSBList + fMSBList

        # 仅写入高14位
        if self.writeMode == 'MSB':
            self.write_data(fMSBList)
        # 仅写入低14位
        elif self.writeMode == 'LSB':
            self.write_data(fLSBList)
        # 写入全部14位
        else:
            self.write_data(fBoth)

        return

    def set_phase(self, pout: int, phaseSelect: int, rads: bool = True) -> None:
        """
        设置相位寄存器的值，选择并更新AD9833的输出相位。

        根据传入的相位值、选择的相位寄存器和是否使用弧度制，计算并更新AD9833的相位寄存器。支持选择相位寄存器0或1进行更新。

        Args:
            pout (int): 设定的信号输出相位，单位为角度（如果rads为False）或弧度（如果rads为True）。
            phaseSelect (int): 选择要写入的相位寄存器，取值为0或1，表示相位寄存器0或1。
            rads (bool): 是否将输入的相位值视为弧度制（默认为True），如果为False，则输入值为角度制。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果传入的`phaseSelect`不是0或1，则抛出该异常。

        ==============================================

        Sets the phase register value to select and update the AD9833 output phase.

        This method calculates and updates the phase register based on the given phase value, selected phase register, and whether to use radians or degrees. It supports updating either phase register 0 or 1.

        Args:
            pout (int): The desired output phase, in degrees (if `rads` is False) or radians (if `rads` is True).
            phaseSelect (int): The phase register to update, where 0 selects phase register 0 and 1 selects phase register 1.
            rads (bool): Whether to interpret the input phase value as radians (default is True). If False, the input value is treated as degrees.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the `phaseSelect` is not 0 or 1, this exception will be raised.

        """

        # 如果phaseSelect不是0或1，则抛出异常
        if phaseSelect != 0 and phaseSelect != 1:
            raise ValueError("phaseSelect must be 0 or 1")

        # 计算相位寄存器的值
        if rads == False:
            # 将角度转换为弧度
            pout = radians(pout)

        # 根据弧度计算相位寄存器的值
        phaseR = int(pout * 4096 / (2 * pi))

        # 将相位值与地址合并
        phaseR = phaseR + (0b11 << 14) + (phaseSelect << 13)

        # 将phaseR拆分为8位段
        phaseRList = [(phaseR & 0xFF00) >> 8, phaseR & 0x00FF]

        # 写入相位寄存器的数据
        self.write_data(phaseRList)

        return

    def set_mode(self, mode: str = 'SIN') -> None:
        """
        设置AD9833输出波形的类型，根据输入的模式选择不同的波形。

        根据传入的`mode`参数设置AD9833输出信号的波形类型。支持的波形包括：正弦波、三角波、方波、二分之一频率的方波、复位和关闭模式。

        Args:
            mode (str): 选择输出波形的类型，支持的值有：
                - 'SIN': 正弦波
                - 'TRIANGLE': 三角波
                - 'SQUARE': 方波
                - 'SQUARE/2': 二分之一频率的方波
                - 'RESET': 复位模式
                - 'OFF': 关闭模式 (使设备进入低功耗状态)

                默认值是'SIN'（正弦波）。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果`mode`参数不在支持的选项范围内，则抛出该异常。

        ==============================================

        Sets the output waveform type of the AD9833, selecting different waveforms based on the input mode.

        This method configures the AD9833 to generate different types of output signals based on the provided `mode` parameter. Supported waveforms include: sine wave, triangle wave, square wave, half-frequency square wave, reset, and off mode.

        Args:
            mode (str): The type of output waveform to select. Supported values are:
                - 'SIN': Sine wave
                - 'TRIANGLE': Triangle wave
                - 'SQUARE': Square wave
                - 'SQUARE/2': Square wave at half frequency
                - 'RESET': Reset mode
                - 'OFF': Off mode (puts the device into low power state)

            Default value is 'SIN' (sine wave).

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the `mode` parameter is not within the supported options, this exception will be raised.
        """

        # 判断输入波形模式是否为SIN、TRIANGLE、SQUARE、SQUARE/2、RESET或OFF
        if mode != 'SIN' and mode != 'TRIANGLE' and mode != 'SQUARE' and mode != 'SQUARE/2' and mode != 'RESET' and mode != 'OFF':
            raise ValueError("mode must be 'SIN', 'TRIANGLE', 'SQUARE', 'SQUARE/2', 'RESET' or 'OFF'")

        # 存储当前的模式
        self.mode = mode

        # 正弦波模式
        if mode == 'SIN':
            self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=self.FS, PS=self.PS, RESET=0, MODE=0)
        # 三角波模式
        elif mode == 'TRIANGLE':
            self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=self.FS, PS=self.PS, RESET=0, MODE=1)
        # 方波模式
        elif mode == 'SQUARE':
            self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=self.FS, PS=self.PS, RESET=0, SLP12=1,
                                 OP=1, DIV2=1, MODE=0)
        # 二分之一频率的方波模式
        elif mode == 'SQUARE/2':
            self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=self.FS, PS=self.PS, RESET=0, SLP12=1,
                                 OP=1, DIV2=0, MODE=0)
        # 复位模式
        elif mode == 'RESET':
            self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=self.FS, PS=self.PS, RESET=1)
        # 关闭模式
        elif mode == 'OFF':
            self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=self.FS, PS=self.PS, RESET=1, SLP1=1, SLP12=1)

        return

    def set_write_mode(self, writeMode: str = 'BOTH') -> None:
        """
        设置频率寄存器的写入模式。

        该方法用于配置频率寄存器的写入方式，支持三种模式：
        - 'BOTH'：同时写入MSB和LSB；
        - 'MSB'：只写入高14位（MSB）；
        - 'LSB'：只写入低14位（LSB）。

        Args:
            writeMode (str): 写入模式。支持的选项有：
                - 'BOTH'：同时写入频率寄存器的MSB和LSB；
                - 'MSB'：只写入频率寄存器的高14位；
                - 'LSB'：只写入频率寄存器的低14位。
                默认值是'BOTH'。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果`writeMode`参数不在支持的选项范围内，则抛出该异常。

        ==============================================

        Sets the write mode for the frequency register.

        This method configures the way the frequency register is written. Three modes are supported:
        - 'BOTH': Writes both MSB (Most Significant Byte) and LSB (Least Significant Byte) at the same time.
        - 'MSB': Writes only the high 14 bits (MSB) of the frequency register.
        - 'LSB': Writes only the low 14 bits (LSB) of the frequency register.

        Args:
            writeMode (str): The write mode. Supported options are:
                - 'BOTH': Write both the MSB and LSB of the frequency register simultaneously.
                - 'MSB': Write only the high 14 bits of the frequency register.
                - 'LSB': Write only the low 14 bits of the frequency register.
            Default value is 'BOTH'.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the `writeMode` parameter is not within the supported options, this exception will be raised.
        """

        # 判断写入模式是否为BOTH、MSB或LSB，若不是则抛出异常
        if writeMode != 'BOTH' and writeMode != 'MSB' and writeMode != 'LSB':
            raise ValueError("writeMode must be 'BOTH', 'MSB' or 'LSB'")

        # 初始化 B28 位为 1，表示同时写入频率寄存器的 MSB 和 LSB
        B28 = 1
        # 初始化 HLB 位为 0，表示选择写入的部分，默认为全写
        HLB = 0
        # 默认写入模式为 'BOTH'，即同时写入 MSB 和 LSB
        self.writeMode = 'BOTH'

        #  如果写入模式为 'MSB'，则只写入频率寄存器的高 14 位
        if writeMode == 'MSB':
            # 设置B28位为0，HLB为1
            B28 = 0
            HLB = 1
            self.writeMode = 'MSB'
        # 如果写入模式为 'LSB'，则只写入频率寄存器的低 14 位
        elif writeMode == 'LSB':
            # 设置B28位为0，HLB为0
            B28 = 0
            HLB = 0
            self.writeMode = 'LSB'

        # 根据选择的 B28 和 HLB 位更新控制寄存器
        self.set_control_reg(B28=B28, HLB=HLB, FS=self.FS, PS=self.PS, RESET=self.RESET, SLP1=self.SLP1,
                             SLP12=self.SLP12, OP=self.OP, DIV2=self.DIV2, MODE=self.MODE)

        return

    def select_freq_phase(self, FS: int, PS: int) -> None:
        """
        选择频率寄存器和相位寄存器。

        此方法根据给定的频率寄存器选择 (FS) 和相位寄存器选择 (PS) 更新控制寄存器。
        选择的寄存器将用于后续的频率和相位设置。

        Args:
            FS (int): 选择频率寄存器。可选值为0或1，表示选择频率寄存器的不同部分。
            PS (int): 选择相位寄存器。可选值为0或1，表示选择相位寄存器的不同部分。

        Returns:
            None: 此方法没有返回值。

        Raises:
            ValueError: 如果`FS`或`PS`的值不在有效范围内（即不为0或1），则抛出该异常。

        ==============================================

        Select frequency register and phase register.

        This method updates the control register based on the given frequency register select (FS) and phase register select (PS).
        The selected registers will be used for subsequent frequency and phase settings.

        Args:
            FS (int): Select the frequency register. Valid values are 0 or 1, indicating different parts of the frequency register.
            PS (int): Select the phase register. Valid values are 0 or 1, indicating different parts of the phase register.

        Returns:
            None: This method does not return any value.

        Raises:
            ValueError: If the value of `FS` or `PS` is not within the valid range (i.e., not 0 or 1), this exception will be raised.
        """

        # 判断输入FS的值是否为0或1，若不是则抛出异常
        if FS != 0 and FS != 1:
            raise ValueError("FS must be 0 or 1")
        # 判断输入PS的值是否为0或1，若不是则抛出异常
        if PS != 0 and PS != 1:
            raise ValueError("PS must be 0 or 1")

        # 根据指定的频率选择 (FS) 和相位选择 (PS) 更新控制寄存器
        self.set_control_reg(B28=self.B28, HLB=self.HLB, FS=FS, PS=PS, RESET=self.RESET, SLP1=self.SLP1,
                             SLP12=self.SLP12, OP=self.OP, DIV2=self.DIV2, MODE=self.MODE)

        return

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================