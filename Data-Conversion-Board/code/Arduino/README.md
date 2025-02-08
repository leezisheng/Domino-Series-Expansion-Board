该数据转换板使用ADS1115四通道模数转换芯片进行数据采集，使用MCP4725数模转换芯片进行电压输出，你可以参考我们的MicroPython代码构建你自己的波形发生类，同时可以使用两个压缩包中的驱动库编写相关例程。
其中ADS1115芯片驱动程序来自于：https://github.com/baruch/ADS1115
MCP4725芯片驱动程序来自于：https://github.com/RobTillaart/MCP4725
这两个驱动程序我们已经验证过，可以使用没有问题。

This data conversion board uses the ADS1115 four-channel analog-to-digital converter (ADC) chip for data acquisition and the MCP4725 digital-to-analog converter (DAC) chip for voltage output. You can refer to our MicroPython code to build your own waveform generation class, and use the driver libraries from the two compressed packages to write related examples.

The ADS1115 chip driver is sourced from: https://github.com/baruch/ADS1115
The MCP4725 chip driver is sourced from: https://github.com/RobTillaart/MCP4725

These two driver programs have been verified and are confirmed to work without issues.