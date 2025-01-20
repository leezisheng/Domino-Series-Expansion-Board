# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-        
# @Time    : 2025/1/16 上午11:14   
# @Author  : 李清水            
# @File    : bus_dc_motor.py
# @Description : 总线直流电机驱动模块，使用PCA9685芯片控制电机驱动芯片

# ======================================== 导入相关模块 =========================================

# 导入PCA9685模块
from pca9685 import PCA9685

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

# 自定义总线直流电机驱动类
class BusDCMotor:
    """
    BusDCMotor类，用于控制直流电机的正转、反转和调速。

    该类通过与PCA9685的接口交互，使用PWM信号控制四个电机的速度和转向。

    Attributes:
        pca9685 (PCA9685): 用于控制PWM信号的PCA9685实例。
        motor_count (int): 电机数量，这里假设最多控制4个电机。

    Methods:
        set_motor_speed(motor_id: int, speed: int, direction: int = 0) -> None:
            设置指定编号电机的速度和转向。
        stop_motor(motor_id: int) -> None:
            停止指定编号电机。

    =============================================

    BusDCMotor class for controlling the direction and speed of DC motors.

    This class communicates with the PCA9685 to control the speed and direction of up to four motors via PWM signals.

    Attributes:
        pca9685 (PCA9685): The PCA9685 instance for controlling PWM signals.
        motor_count (int): Number of motors to control, assuming up to 4 motors.

    Methods:
        set_motor_speed(motor_id: int, speed: int, direction: int = 0) -> None:
            Set the speed and direction of the specified motor.
        stop_motor(motor_id: int) -> None:
            Stop the specified motor.
    """

    def __init__(self, pca9685: PCA9685, motor_count: int = 4):
        """
        构造函数，初始化电机控制类。

        Args:
            pca9685 (PCA9685): PCA9685实例，用于控制PWM信号。
            motor_count (int): 需要控制的电机数量。默认值为4个电机。

        Raises:
            ValueError: 如果电机数量超出范围（1-4）或传入的pca9685不是PCA9685实例。

        ============================================

        Constructor to initialize the motor control class.

        Args:
            pca9685 (PCA9685): PCA9685 instance to control PWM signals.
            motor_count (int): Number of motors to control. Default is 4 motors.

        Raise:
            ValueError: If motor count is out of range (1-4) or pca9685 is not an instance of PCA9685.
        """
        # 电机数量不可能大于八个
        if motor_count > 8:
            raise ValueError(f"Invalid motor_count: {motor_count}. Motor count must be between 1 and 4.")

        # 判断pca9685是否为PCA9685实例
        if not isinstance(pca9685, PCA9685):
            raise ValueError("Invalid pca9685. pca9685 must be an instance of PCA9685.")

        self.pca9685 = pca9685
        self.motor_count = motor_count

    def set_motor_speed(self, motor_id: int, speed: int, direction: int = 0) -> None:
        """
        设置指定编号电机的速度和转向。

        根据电机编号和方向，调整对应PWM引脚的占空比，以控制电机的转动方向和速度。

        Args:
            motor_id (int): 电机的编号（1至4）。
            speed (int): 电机的速度，占空比范围为0到4095。
            direction (int, optional): 电机转向，0表示前进，1表示后退。默认为0（前进）。

        Raises:
            ValueError: 如果电机编号超出范围（1-4）或者速度值超出范围（0-4095）。

        =============================================

        Set the speed and direction of the specified motor.

        Adjust the PWM duty cycle of the corresponding pins based on motor ID and direction to control the motor's rotation direction and speed.

        Args:
            motor_id (int): Motor ID (1 to 4).
            speed (int): Motor speed, PWM duty cycle range from 0 to 4095.
            direction (int, optional): Motor direction, 0 for forward and 1 for backward. Default is 0 (forward).

        Raises:
            ValueError: If motor ID is out of range (1-4) or speed is out of range (0-4095).
        """
        if motor_id < 1 or motor_id > self.motor_count:
            raise ValueError(f"Invalid motor_id: {motor_id}. Motor ID must be between 1 and {self.motor_count}.")

        if not 0 <= speed <= 4095:
            raise ValueError(f"Invalid speed: {speed}. Speed must be between 0 and 4095.")

        # 根据电机编号选择对应的PWM引脚
        pwm_index = motor_id - 1  # 将电机编号转为对应的PWM通道（0到3）

        # 设置前进（direction = 0）或后退（direction = 1）的方向
        if direction == 0:
            # 控制前进，FI引脚
            self.pca9685.duty(pwm_index, speed)
            # 设置后退BI引脚为0
            self.pca9685.duty(pwm_index + 1, 0)
        elif direction == 1:
            # 控制后退，BI引脚
            self.pca9685.duty(pwm_index + 1, speed)
            # 设置前进FI引脚为0
            self.pca9685.duty(pwm_index, 0)
        else:
            raise ValueError("Invalid direction. Use 0 for forward or 1 for backward.")

    def stop_motor(self, motor_id: int) -> None:
        """
        停止指定编号电机的转动，设置PWM信号为0。

        Args:
            motor_id (int): 电机的编号（1至4）。

        Raise:
            ValueError: 如果电机编号超出范围（1-4）。

        =============================================

        Stop the motor with the specified ID by setting the PWM duty cycle to 0.

        Args:
            motor_id (int): Motor ID (1 to 4).

        Raise:
            ValueError: If motor ID is out of range (1-4).
        """
        if motor_id < 1 or motor_id > self.motor_count:
            raise ValueError(f"Invalid motor_id: {motor_id}. Motor ID must be between 1 and {self.motor_count}.")

        # 将电机的两个方向引脚都设置为0，停止电机
        pwm_index = motor_id - 1
        self.pca9685.duty(pwm_index, 0)
        self.pca9685.duty(pwm_index + 1, 0)

# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================