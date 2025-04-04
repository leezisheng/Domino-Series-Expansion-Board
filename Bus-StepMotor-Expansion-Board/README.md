### `bus_step_motor.py`
该文件实现了对步进电机的控制。通过PCA9685芯片，可以实现多个步进电机的独立控制，支持正反转、角度控制及定步运动。

- **驱动模式选择**：步进电机支持单相、双相和半步驱动模式，允许根据精度和扭矩要求选择合适的模式。
- **非阻塞式控制**：通过软件定时器实现非阻塞式方法，允许在电机运动过程中执行其他任务，提高系统的响应能力。
- **定步运动**：步进电机支持定步运动功能，能够按照用户设定的步数精确控制电机位置。

![BusStepMotor](../../image/BusStepMotor.png)

#### 主要类
**BusStepMotor**：
- 控制步进电机的正反转、角度控制和定步运动。通过PCA9685芯片控制PWM信号。

  **方法**：
  - `__init__(pca9685: PCA9685, motor_count: int = 2)`：构造函数，初始化电机控制类。
  - `_next_step(motor_id: int)`：计算并更新指定电机的步进状态。
  - `_start_timer(motor_id: int, speed: int)`：启动定时器并设置回调函数，以控制电机连续运动。
  - `_stop_timer(motor_id: int)`：停止指定电机的定时器，停止运动。
  - `start_continuous_motion(motor_id: int, direction: int, driver_mode: int, speed: int)`：启动电机进行连续运动。
  - `stop_continuous_motion(motor_id: int)`：停止电机的连续运动。
  - `start_step_motion(motor_id: int, direction: int, driver_mode: int, speed: int, steps: int)`：启动步进电机的定步运动，按照指定步数执行。

- 支持多种步进电机的驱动模式（单相、双相、半步驱动），并且通过使用定时器和回调机制精确控制每个电机的步进过程。每个电机的状态（包括方向、步进模式、速度等）都被单独管理，使得电机的控制更加灵活，并且能够精确地执行定步运动或连续运动。

#### 主要功能
* **多电机控制：** 支持同时控制最多4个步进电机，独立配置每个电机的转速、方向和驱动模式。
* **驱动模式：** 提供单相、双相和半步三种驱动模式，以满足不同精度和扭矩需求。
* **角度和步数控制：** 该类支持连续步进和定步控制，可以根据用户设定的步数进行精确的定位。
* **非阻塞式方法：** 通过软件定时器实现在控制电机时继续执行其他任务

- **电机驱动模式选择**：选择合适的驱动模式对步进电机至关重要。不同的驱动模式会影响电机的精度、扭矩和功率消耗，建议根据应用需求选择适合的模式。
- **过载保护**：为避免电机驱动电路过载，使用合适的限流保护措施，并确保电机的工作在其额定负载范围内。
- **步进电机步数控制**：步进电机的定步控制应确保在实际使用中不会超过最大步数范围，以避免电机跳步或位置错误。