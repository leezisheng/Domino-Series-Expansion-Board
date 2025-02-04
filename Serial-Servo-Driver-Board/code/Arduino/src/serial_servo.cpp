/**
  ******************************************************************************
* @Time    : 2025/1/24 下午1:59   
* @Author  : lilis           
* @File    : serial_servo.cpp    
* @version 1.0.0 
* @Description : TTL串口舵机驱动类
  ******************************************************************************
*/

/* Includes ------------------------------------------------------------------*/
#include "serial_servo.h"

/* Public variable------------------------------------------------------------*/
/** 
 * @brief  类公共变量：指令及其参数长度或返回数据长度
 * 写入指令及其对应的参数长度
 * 读取指令及其对应的参数长度和返回数据长度
 * ===================================================
 * @brief  Public class variables: Command and its parameter length or return data length
 * Write command and its corresponding parameter length
 * Read command and its corresponding parameter length and return data length
 */
//舵机立即转动写入命令
const uint8_t SerialServo::SERVO_MOVE_TIME_WRITE[2] = {1, 7};
//舵机立即转动参数读取命令
const uint8_t SerialServo::SERVO_MOVE_TIME_READ[3] = {2, 3, 7};

// 舵机延迟转动写入命令
const uint8_t SerialServo::SERVO_MOVE_TIME_WAIT_WRITE[2] = {7, 7};
// 舵机延迟转动读取命令
const uint8_t SerialServo::SERVO_MOVE_TIME_WAIT_READ[3] = {8, 3, 7};

// 舵机开启转动指令（配合SERVO_MOVE_TIME_WAIT_WRITE指令使用）
const uint8_t SerialServo::SERVO_MOVE_START[2] = {11, 3};
// 舵机停止转动指令
const uint8_t SerialServo::SERVO_MOVE_STOP[2] = {12, 3};

// 舵机ID写入命令（支持掉电保存）
const uint8_t SerialServo::SERVO_ID_WRITE[2] = {13, 4};
// 舵机ID读取命令
const uint8_t SerialServo::SERVO_ID_READ[3] = {14, 3, 4};

// 舵机偏差调节指令（不支持掉电保存）
const uint8_t SerialServo::SERVO_ANGLE_OFFSET_ADJUST[2] = {17, 4};
// 舵机偏差调节指令（支持掉电保存）
const uint8_t SerialServo::SERVO_ANGLE_OFFSET_WRITE[2] = {18, 3};
// 舵机偏差调节读取指令
const uint8_t SerialServo::SERVO_ANGLE_OFFSET_READ[3] = {19, 3, 4};

// 舵机角度限位写入命令（支持掉电保存）
const uint8_t SerialServo::SERVO_ANGLE_LIMIT_WRITE[2] = {20, 7};
// 舵机角度限位读取命令
const uint8_t SerialServo::SERVO_ANGLE_LIMIT_READ[3] = {21, 3, 7};

// 舵机电压限制写入命令（支持掉电保存）
const uint8_t SerialServo::SERVO_VIN_LIMIT_WRITE[2] = {22, 7};
// 舵机电压限制读取命令
const uint8_t SerialServo::SERVO_VIN_LIMIT_READ[3] = {23, 3, 7};

// 舵机温度限制写入命令（支持掉电保存）
const uint8_t SerialServo::SERVO_TEMP_MAX_LIMIT_WRITE[2] = {24, 4};
// 舵机温度限制读取命令
const uint8_t SerialServo::SERVO_TEMP_MAX_LIMIT_READ[3] = {25, 3, 4};

// 舵机实时温度读取指令
const uint8_t SerialServo::SERVO_TEMP_READ[3] = {26, 3, 4};
// 舵机实时电压读取指令
const uint8_t SerialServo::SERVO_VIN_READ[3] = {27, 3, 5};
// 舵机当前角度读取指令
const uint8_t SerialServo::SERVO_POS_READ[3] = {28, 3, 5};

// 舵机模式切换指令（不支持掉电保存）
const uint8_t SerialServo::SERVO_OR_MOTOR_MODE_WRITE[2] = {29, 7};
// 舵机模式及参数读取指令
const uint8_t SerialServo::SERVO_OR_MOTOR_MODE_READ[3] = {30, 3, 7};

// 舵机上电/掉电控制指令（不支持掉电保存）
const uint8_t SerialServo::SERVO_LOAD_OR_UNLOAD_WRITE[2] = {31, 4};
// 舵机上电/掉电读取指令
const uint8_t SerialServo::SERVO_LOAD_OR_UNLOAD_READ[3] = {32, 3, 4};

// 舵机LED控制指令（支持掉电保存）
const uint8_t SerialServo::SERVO_LED_CTRL_WRITE[2] = {33, 4};
// 舵机LED读取指令
const uint8_t SerialServo::SERVO_LED_CTRL_READ[3] = {34, 3, 4};

// 舵机LED报警闪烁指令
const uint8_t SerialServo::SERVO_LED_ERROR_WRITE[2] = {35, 4};
// 舵机LED报警闪烁值读取指令
const uint8_t SerialServo::SERVO_LED_ERROR_READ[3] = {36, 3, 4};


// 舵机工作模式 
// 0 代表位置控制模式
const uint8_t SerialServo::MODE_POSITION = 0;
// 1 代表电机控制模式
const uint8_t SerialServo::MODE_MOTOR = 1;

// LED报警故障类型常量赋值
// 无报警
const uint8_t SerialServo::ERROR_NO_ALARM = 0;
// 过温报警
const uint8_t SerialServo::ERROR_OVER_TEMP = 1;
// 过压报警
const uint8_t SerialServo::ERROR_OVER_VOLT = 2;
// 过温和过压报警
const uint8_t SerialServo::ERROR_OVER_TEMP_AND_VOLT = 3;
// 堵转报警
const uint8_t SerialServo::ERROR_STALL = 4;
// 过温和堵转报警
const uint8_t SerialServo::ERROR_OVER_TEMP_AND_STALL = 5;
// 过压和堵转报警
const uint8_t SerialServo::ERROR_OVER_VOLT_AND_STALL = 6;
// 过温、过压和堵转报警
const uint8_t SerialServo::ERROR_ALL = 7;

// 读取命令集合：根据指令的元组长度来确定哪些是读取命令（命令编号，参数长度，返回数据长度）
const uint8_t SerialServo::READ_COMMANDS[] = {
    2,  // SERVO_MOVE_TIME_READ
    8,  // SERVO_MOVE_TIME_WAIT_READ
    14, // SERVO_ID_READ
    19, // SERVO_ANGLE_OFFSET_READ
    21, // SERVO_ANGLE_LIMIT_READ
    23, // SERVO_VIN_LIMIT_READ
    25, // SERVO_TEMP_MAX_LIMIT_READ
    26, // SERVO_TEMP_READ
    27, // SERVO_VIN_READ
    28, // SERVO_POS_READ
    30, // SERVO_OR_MOTOR_MODE_READ
    32, // SERVO_LOAD_OR_UNLOAD_READ
    34, // SERVO_LED_CTRL_READ
    36  // SERVO_LED_ERROR_READ
};
/* Private member variables---------------------------------------------------*/\
/** 
 * @brief  串口对象指针
 * 
 * 这个私有成员变量是指向 `HardwareSerial` 类型对象的指针，用于通过硬件串口与外部设备进行通信。
 * 它封装了与串口通信相关的操作，提供了基本的发送、接收功能。
 * 作为私有成员，`uart` 只能在类的内部访问和操作，外部不能直接修改其值。
 * ===================================================
 * @brief  Serial port object pointer
 * 
 * This private member variable is a pointer to a `HardwareSerial` object used for communication with external devices via hardware serial.
 * It encapsulates the operations related to serial communication, providing basic send and receive functionalities.
 * As a private member, `uart` can only be accessed and modified within the class, and cannot be directly modified from outside.
 */
HardwareSerial* uart;

/* Function definition--------------------------------------------------------*/

/* 
 * @description : 初始化串口，设置波特率
 * @param {unsigned long} baudRate : 串口通信的波特率
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Initialize the serial port and set the baud rate.
 * @param {unsigned long} baudRate : The baud rate for serial communication.
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed.
 */
SerialServo::SerialServo(HardwareSerial& uart) {
    assert(&uart != nullptr);  // 断言传入的串口对象非空
    this->uart = &uart;        // 保存串口对象
}

/* 
 * @description : 初始化串口，设置波特率
 * @param {unsigned long} baudRate : 串口通信的波特率
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Initialize the serial port and set the baud rate.
 * @param {unsigned long} baudRate : The baud rate for serial communication.
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed.
 */
t_FuncRet SerialServo::begin(unsigned long baudRate) {
    if (uart == nullptr) {
        return Operation_Fail;  // 如果 uart 对象为空，返回失败
    }
    uart->begin(baudRate);  // 初始化串口通信，设置波特率
    return Operation_Success;  // 如果有回应，说明初始化成
}

/* 
 * @description : 计算校验和
 * @param {uint8_t*} data : 需要计算校验和的数据指针
 * @param {uint8_t} length : 数据的长度
 * @param {uint8_t&} checksum : 用于存储计算出的校验和的引用
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Calculate the checksum.
 * @param {uint8_t*} data : Pointer to the data for which checksum needs to be calculated.
 * @param {uint8_t} length : Length of the data.
 * @param {uint8_t&} checksum : Reference to store the calculated checksum.
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed.
 */
t_FuncRet SerialServo::calculate_checksum(uint8_t* data, uint8_t length, uint8_t& checksum) {
    // 使用断言库来验证数据指针和长度是否合法
    assert(data != nullptr);  // 确保数据指针不为空
    assert(length > 0);        // 确保数据长度大于零

    checksum = 0;

    // 对数据进行求和并确保结果在低8位范围内
    for (uint8_t i = 0; i < length-3; i++) {
        checksum += data[i];
    }


    // 计算取反的校验和，限制在8位
    checksum = ~(checksum & 0xFF) & 0xFF;
    // 返回成功状态
    return Operation_Success;
}

/* 
 * @description : 数据包构建函数
 * @param {uint8_t} servo_id : 舵机ID，范围在1到254之间
 * @param {uint8_t} cmd : 指令代码，用于控制舵机
 * @param {uint8_t*} params : 参数数据，用于指令
 * @param {size_t} params_length : 参数数据的长度
 * @param {byte*} packet : 存储构建好数据包的缓冲区
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Packet construction function
 * @param {uint8_t} servo_id : The ID of the servo, in the range of 1 to 254.
 * @param {uint8_t} cmd : Command code for controlling the servo.
 * @param {uint8_t*} params : Parameter data for the command.
 * @param {size_t} params_length : The length of the parameter data.
 * @param {byte*} packet : Buffer to store the constructed packet.
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed.
 */
t_FuncRet SerialServo::buildPacket(uint8_t servo_id, uint8_t cmd, uint8_t* params, size_t params_length, byte* packet) {
    // 检查舵机ID是否在合法范围内
    if (servo_id < 0 || servo_id > 254) 
    {
        return Operation_Fail;  // 舵机ID不合法，返回失败
    }

    // 数据长度
    size_t length = 2 + params_length + 1;  // id + cmd + 参数长度 + 校验和

    // 数据包长度
    size_t all_length = 2 + 3 + params_length + 1;  // 帧头+ id + cmd + 参数长度 + 指令 + 参数+ 校验和

    // 填充数据包
    packet[0] = 0x55;  // 帧头
    packet[1] = 0x55;  // 帧头
    packet[2] = servo_id;  // 舵机ID
    packet[3] = length;  // 数据长度
    packet[4] = cmd;  // 指令

    // 添加参数
    for (size_t i = 0; i < params_length; i++) {
        packet[5 + i] = params[i];
    }

    // 计算校验和，计算的数据是从ID开始到最后一个参数（不包含校验和字段）
    uint8_t checksum = 0;
    calculate_checksum(&packet[2], all_length, checksum);  // 计算校验和，不包含校验和字段本身

    // 将校验和添加到数据包的末尾
    packet[all_length - 1] = checksum;

    return Operation_Success;  // 返回成功
}

/* 
 * @description : 发送控制指令到舵机
 * @param {uint8_t} servo_id : 舵机ID，范围在1到254之间
 * @param {uint8_t} cmd : 指令代码，用于控制舵机
 * @param {uint8_t*} params : 参数数据，用于指令
 * @param {size_t} params_length : 参数数据的长度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Send control command to the servo
 * @param {uint8_t} servo_id : The ID of the servo, in the range of 1 to 254
 * @param {uint8_t} cmd : Command code for controlling the servo
 * @param {uint8_t*} params : Parameter data for the command
 * @param {size_t} params_length : The length of the parameter data
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::send_command(uint8_t servo_id, uint8_t cmd, uint8_t* params, size_t params_length) {
    if (servo_id < 0 || servo_id > 254) {
        return Operation_Fail;  // 舵机ID不合法，返回失败
    }

    // 计算实际需要的包大小：5个固定字节 + 参数长度 + 1个校验和字节
    size_t packet_length = 5 + params_length + 1;
    // 创建数据包数组
    byte packet[packet_length];
    t_FuncRet result = buildPacket(servo_id, cmd, params, params_length, packet);

    // 检查数据包构建是否成功
    if (result == Operation_Fail) {
        Serial.println("Error: Failed to build packet!");  // 打印错误信息
        delay(10);
    }

    // 发送数据包
    uart->write(packet, packet_length);  // 通过串口发送数据包
    delay(20);  // 添加延时

    // 调试输出：打印包内容
    Serial.print("Sending packet: ");
    for (size_t i = 0; i < packet_length; i++) {
        Serial.print(packet[i], HEX);
        delay(10);
        Serial.print(" ");
    }
    Serial.println();  // 换行

    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 接收并处理舵机控制命令
 * @param {uint8_t} expected_cmd : 期望接收到的命令编号
 * @param {uint8_t} expected_data_len : 期望的数据长度
 * @param {uint8_t*} params : 存储接收到的参数数据
 * @param {size_t*} params_len : 存储参数数据的长度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Receive and process the servo control command
 * @param {uint8_t} expected_cmd : The expected command number to receive
 * @param {uint8_t} expected_data_len : The expected data length
 * @param {uint8_t*} params : Store the received parameter data
 * @param {size_t*} params_len : Store the length of parameter data
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::receive_command(uint8_t expected_cmd, uint8_t expected_data_len, uint8_t* params, size_t* params_len) {
    // 1. 命令验证
    bool is_read_command = false;
    size_t num_commands = sizeof(READ_COMMANDS) / sizeof(READ_COMMANDS[0]);
    for (size_t i = 0; i < num_commands; i++) {
        if (READ_COMMANDS[i] == expected_cmd) {
            is_read_command = true;
            break;
        }
    }
    if (!is_read_command) {
        return Operation_Fail;  // 如果不是读取命令，则返回失败
    }
    // 2. 数据检查
    uint8_t data[15];  // 假设数据帧最大为256字节
    int data_len = uart->readBytes(data, sizeof(data));

    if (data_len < 6) {
        return Operation_Fail;  // 数据长度小于最小帧头大小，返回失败
    }
    if (data_len > 15) {
        return Operation_Fail;  // 数据长度小于最小帧头大小，返回失败
    }

    if (data[0] != 0x55 || data[1] != 0x55) {
        return Operation_Fail;  // 帧头不匹配，返回失败
    }

    *params_len = data[3] - 3;  // 减去3是因为前面是帧头、ID和指令
    Serial.print("params_len: ");
    Serial.println(*params_len);

    size_t all_len = 6 + *params_len;  // 总长度 = 帧头 + ID + 参数长度 + 指令 + 参数 + 校验和
    if (data_len < all_len) {
        return Operation_Fail;  // 返回数据不足，返回失败
    }

    // 3. 校验和校验
    uint8_t checksum_received = data[data_len - 1];  // 接收到的校验和
    uint8_t checksum_calculated;  // 计算得到的校验和

    // 调用计算校验和的函数，计算从数据区开始到倒数第二个字节的校验和
    t_FuncRet checksum_status = calculate_checksum(&data[2], all_len, checksum_calculated);
    if (checksum_status != Operation_Success) {
        return Operation_Fail;  // 如果计算校验和失败，返回失败
    }

    if (checksum_received != checksum_calculated) {
        return Operation_Fail;  // 校验和不匹配，返回失败
    }

    // 4. 解析参数
    for (size_t i = 0; i < *params_len; i++) {
        params[i] = data[5 + i];  // 从数据区中提取参数
    }
    // 5. 返回成功
    return Operation_Success;
}
/* 
 * @description : 接收并解析从舵机发送的命令数据
 * @param {uint8_t} expected_cmd : 期望接收到的命令编号
 * @param {uint8_t} expected_data_len : 期望的数据长度
 * @param {uint8_t*} params : 用于存放接收到的参数数据
 * @param {size_t*} params_len : 返回实际接收到的参数长度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Receive and parse the command data sent from the servo
 * @param {uint8_t} expected_cmd : Expected command number to receive
 * @param {uint8_t} expected_data_len : Expected data length
 * @param {uint8_t*} params : Used to store the received parameter data
 * @param {size_t*} params_len : Returns the actual length of received parameters
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::move_servo_immediate(uint8_t servo_id, float angle, uint16_t time_ms) {
    // 检查 servo_id 是否在合法范围内
    if (servo_id < 0 || servo_id > 254) {
        Serial.println("Servo ID must be in range 0~254.");
        return Operation_Fail;
    }

    // 检查角度是否在 0~240 度范围内
    if (angle < 0 || angle > 240) {
        Serial.println("Angle must be in range 0~240.");
        return Operation_Fail;
    }

    // 检查时间是否在 0~30000 毫秒范围内
    if (time_ms < 0 || time_ms > 30000) {
        Serial.println("Time must be in range 0~30000.");
        return Operation_Fail;
    }

    // 将角度转换为舵机控制指令所需的低八位和高八位
    uint16_t angle_value = static_cast<uint16_t>(angle / 0.24);
    uint8_t angle_low = angle_value & 0xFF;
    uint8_t angle_high = (angle_value >> 8) & 0xFF;

    // 将时间转换为低八位和高八位
    uint8_t time_low = time_ms & 0xFF;
    uint8_t time_high = (time_ms >> 8) & 0xFF;

    // 构建指令参数
    uint8_t params[] = {angle_low, angle_high, time_low, time_high};
    uint8_t params_length = sizeof(params);

    // 发送控制指令到舵机
    uint8_t cmd = SerialServo::SERVO_MOVE_TIME_WRITE[0];  // 获取命令号
    t_FuncRet result = send_command(servo_id, cmd, params, params_length);

    if (result != Operation_Success) {
        Serial.println("Failed to send the servo move command.");
    }
    // 成功发送命令后，返回成功状态 
    return Operation_Success;
}
/* 
 * @description : 控制舵机立即移动到指定角度并持续指定时间
 * @param {uint8_t} servo_id : 舵机的ID
 * @param {float} angle : 目标角度，范围为 0~240 度
 * @param {uint16_t} time_ms : 移动时间，单位毫秒，范围为 0~30000 毫秒
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Control the servo to immediately move to the specified angle and last for the specified time
 * @param {uint8_t} servo_id : The ID of the servo
 * @param {float} angle : Target angle, range 0~240 degrees
 * @param {uint16_t} time_ms : Moving time in milliseconds, range 0~30000 milliseconds
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_move_immediate(uint8_t servo_id, float* angle_value, uint16_t* time_value) {
    // 校验舵机ID范围
    if (servo_id < 0 || servo_id > 253) {
        return Operation_Fail;  // 舵机ID无效，返回失败
    }

    // 发送 SERVO_MOVE_TIME_READ 命令
    uint8_t params[] = {};  // 不需要任何额外参数
    uint8_t params_length = sizeof(params);
    uint8_t cmd = SerialServo::SERVO_MOVE_TIME_READ[0];  // 获取命令号

    t_FuncRet result_send = send_command(servo_id, cmd, params,params_length);
    delay(5);
    if (result_send != Operation_Success) {
        return Operation_Fail;  // 发送命令失败，返回失败
    }
  
    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_MOVE_TIME_READ[2] - 3;

    t_FuncRet result_rec = receive_command(cmd, expected_params_len,params_received,&params_received_len);
    if (result_rec != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;  // 接收数据失败，返回失败
    }

    // 解析角度值，低8位和高8位合并为一个16位整数
    int angle_raw = params_received[0] + (params_received[1] << 8);
    *angle_value = angle_raw * 0.24;  // 转换为角度值

    // 校验角度范围
    if (*angle_value < 0 || *angle_value > 240) {
        return Operation_Fail;  // 角度值无效，返回失败
    }

    // 解析时间值，低8位和高8位合并为一个16位整数
    uint16_t time_raw = params_received[2] + (params_received[3] << 8);
    *time_value = time_raw;

    // 校验时间范围
    if (*time_value < 0 || *time_value > 30000) {
        return Operation_Fail;  // 时间值无效，返回失败
    }

    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 获取舵机的预设角度和时间
 * @param {uint8_t} servo_id : 舵机ID
 * @param {float &} angle : 输出参数，舵机当前预设的角度
 * @param {uint16_t &} time_ms : 输出参数，舵机的预设时间
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the preset angle and time of the servo
 * @param {uint8_t} servo_id : The ID of the servo
 * @param {float &} angle : Output parameter, the preset angle of the servo
 * @param {uint16_t &} time_ms : Output parameter, the preset time of the servo
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::move_servo_with_time_delay(uint8_t servo_id, float angle, uint16_t time_ms) {
    // 断言角度范围在0~240度之间
    assert(angle >= 0 && angle <= 240);  // 如果角度不在范围内，程序会崩溃
    // 断言时间范围在0~30000毫秒之间
    assert(time_ms >= 0 && time_ms <= 30000);  // 如果时间不在范围内，程序会崩溃

    // 将角度转换为舵机控制指令所需的低八位和高八位
    uint16_t angle_value = static_cast<uint16_t>(angle / 0.24);
    uint8_t angle_low = angle_value & 0xFF;
    uint8_t angle_high = (angle_value >> 8) & 0xFF;

    // 将时间转换为低八位和高八位
    uint8_t time_low = time_ms & 0xFF;
    uint8_t time_high = (time_ms >> 8) & 0xFF;

    // 构建指令参数
    uint8_t params[] = {angle_low, angle_high, time_low, time_high};
    uint8_t params_length = sizeof(params);

    // 发送控制指令到舵机
    uint8_t cmd = SerialServo::SERVO_MOVE_TIME_WAIT_WRITE[0];  // 获取命令号
    t_FuncRet result = send_command(servo_id, cmd, params,params_length);

    if (result != Operation_Success) {
        Serial.println("Failed to send the servo move command.");
        return Operation_Fail;
    }

    // 发送开始转动命令（SERVO_MOVE_START）
    cmd = SerialServo::SERVO_MOVE_START[0];  // 获取命令号
    // 构建指令参数
    uint8_t params_2[] = {};
    uint8_t params_length_2 = sizeof(params_2);
    result = send_command(servo_id, cmd, params_2,params_length_2);  // 无参数

    if (result != Operation_Success) {
        Serial.println("Failed to send the servo start command.");
        return Operation_Fail;
    }
    return Operation_Success;  // 成功时返回成功状态
}
/* 
 * @description : 获取舵机的预设角度和时间
 * @param {uint8_t} servo_id : 舵机ID
 * @param {float &} angle : 输出参数，舵机当前预设的角度
 * @param {uint16_t &} time_ms : 输出参数，舵机的预设时间
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the preset angle and time of the servo
 * @param {uint8_t} servo_id : The ID of the servo
 * @param {float &} angle : Output parameter, the preset angle of the servo
 * @param {uint16_t &} time_ms : Output parameter, the preset time of the servo
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_move_with_time_delay(uint8_t servo_id, float &angle, uint16_t &time_ms) {
    // 校验舵机ID范围
    if (servo_id < 0 || servo_id > 253) {
        return Operation_Fail;  // 舵机ID无效，返回失败
    }

    // 发送 SERVO_MOVE_TIME_WAIT_READ 命令，读取舵机的预设角度和时间
    uint8_t params[] = {};
    uint8_t params_length = sizeof(params);
    uint8_t cmd = SerialServo::SERVO_MOVE_TIME_WAIT_READ[0];  // 获取命令号

    t_FuncRet result_send = send_command(servo_id, cmd, params , params_length);
    delay(5);
    if (result_send != Operation_Success) {
        return Operation_Fail;
    }

    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_MOVE_TIME_WAIT_READ[2] - 3;

    t_FuncRet result_rec = receive_command(cmd, expected_params_len, params_received, &params_received_len);
    delay(50);
    Serial.print("Expected params length: ");
    Serial.println(expected_params_len);
    delay(10);
    Serial.println("params_received_len.");
    Serial.println(params_received_len);

    // 如果接收失败或数据为空，返回失败状态
    if (result_rec != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;
    }

    // 解析角度值：低8位和高8位合并为16位整数
    uint16_t angle_value = params_received[0] + (params_received[1] << 8);
    angle = angle_value * 0.24;  // 将16位整数转换为实际角度

    // 校验角度范围是否合法
    if (angle < 0 || angle > 240) {
        return Operation_Fail;
    }
    // 解析时间值：低8位和高8位合并为16位整数
    time_ms = params_received[2] + (params_received[3] << 8);

    // 校验时间范围是否合法
    if (time_ms < 0 || time_ms > 30000) {
        delay(20);
        return Operation_Fail;
    }

    // 如果一切正常，返回成功状态
    return Operation_Success;
}
/* 
 * @description : 启动指定舵机的转动
 * @param {uint8_t} servo_id : 舵机ID
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Start the rotation of the specified servo
 * @param {uint8_t} servo_id : The ID of the servo
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::start_servo(uint8_t servo_id) {
    // 检查 servo_id 是否在合法范围内
    if (servo_id < 0 || servo_id > 253) {
        Serial.println("Servo ID must be in range 0~253.");
        return Operation_Fail;  // 返回失败状态
    }

    // 发送启动转动指令
    uint8_t params[] = {};  // 无额外参数
    size_t params_length = sizeof(params) / sizeof(uint8_t);   // 计算数组元素个数
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_MOVE_START[0], params,params_length);
    
    if (result != Operation_Success) {
        Serial.println("Failed to send the servo start command.");
        return Operation_Fail;  // 发送失败
    }
    
    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 停止指定舵机的转动
 * @param {uint8_t} servo_id : 要停止的舵机的 ID
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Stop the movement of the specified servo
 * @param {uint8_t} servo_id : The ID of the servo to stop
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::stop_servo(uint8_t servo_id) {
    // 检查 servo_id 是否在合法范围内
    if (servo_id < 0 || servo_id > 253) {
        Serial.println("Servo ID must be in range 0~253.");
        return Operation_Fail;  // 返回失败状态
    }

    // 发送停止转动指令
    uint8_t params[] = {};  // 无额外参数
    size_t params_length = sizeof(params) / sizeof(uint8_t);   // 计算数组元素个数
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_MOVE_STOP[0], params,params_length);
    
    if (result != Operation_Success) {
        Serial.println("Failed to send the servo stop command.");
        return Operation_Fail;  // 发送失败
    }
    
    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 设置舵机的新 ID
 * @param {uint8_t} servo_id : 当前舵机的 ID
 * @param {uint8_t} new_id : 新的舵机 ID
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set a new ID for the servo
 * @param {uint8_t} servo_id : The current ID of the servo
 * @param {uint8_t} new_id : The new ID to assign to the servo
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_id(uint8_t servo_id, uint8_t new_id) {
    // 检查 servo_id 和 new_id 是否在合法范围内
    if (servo_id < 0 || servo_id > 253 || new_id < 0 || new_id > 253) {
        Serial.println("Servo ID and New ID must be in range 0~253.");
        return Operation_Fail;  // 返回失败状态
    }

    // 发送设置新ID指令
    uint8_t params[] = {new_id};  // 设置新ID的参数
    size_t params_length = sizeof(params) / sizeof(uint8_t);  // 计算数组元素个数
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_ID_WRITE[0], params,params_length);
    
    if (result != Operation_Success) {
        Serial.println("Failed to set the new servo ID.");
        return Operation_Fail;  // 发送失败
    }
    
    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 获取当前舵机的 ID
 * @param {uint8_t} servo_id : 要读取的舵机 ID
 * @param {uint8_t*} servo_id_value : 存储获取到的舵机 ID 的指针
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the current ID of the specified servo
 * @param {uint8_t} servo_id : The ID of the servo to read from
 * @param {uint8_t*} servo_id_value : Pointer to store the fetched servo ID
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_id(uint8_t servo_id, uint8_t* servo_id_value) {
    // 检查 servo_id 是否有效
    if (servo_id < 0 || servo_id > 253) {
        Serial.println("Servo ID must be in range 0~253.");
        return Operation_Fail;  // 返回失败状态
    }
    // 发送 SERVO_ID_READ 命令
    uint8_t params[] = {};  // 无额外参数
    size_t params_length = sizeof(params) / sizeof(uint8_t);   // 计算数组元素个数
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_ID_READ[0], params,params_length);
    
    if (result != Operation_Success) {
        return Operation_Fail;  // 如果命令发送失败，返回失败
    }
    // 延迟5ms再接收数据
    delay(5);

    // 接收并解析返回的数据
    uint8_t params_r[1];  // 需要传入一个参数数组用于接收返回数据
    size_t param_len_r = 0;
    result = receive_command(SerialServo::SERVO_ID_READ[0], 1, params_r, &param_len_r);
    
    if (result != Operation_Success || sizeof(params) == 0) {
        return Operation_Fail;  // 如果没有接收到有效数据，返回失败
    }

    // 获取舵机ID值
    *servo_id_value = params[0];

    // 判断ID是否在合理范围内
    if (*servo_id_value < 0 || *servo_id_value > 253) {
        Serial.println("Invalid servo ID received.");
        return Operation_Fail;
    }
    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 设置舵机的角度偏移值，并可选择保存到内存
 * @param {uint8_t} servo_id : 要设置偏移值的舵机 ID
 * @param {float} angle : 角度值，范围为 -30° 到 30°（单位：度）
 * @param {bool} save_to_memory : 是否将偏移值保存到舵机内存中
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set the servo angle offset, and optionally save it to memory
 * @param {uint8_t} servo_id : The ID of the servo to set the offset for
 * @param {float} angle : The angle value, in the range of -30° to 30° (unit: degree)
 * @param {bool} save_to_memory : Whether to save the offset value to the servo memory
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_angle_offset(uint8_t servo_id, float angle, bool save_to_memory) {
    // 检查角度是否在合法范围内 -30°~30°
    if (angle < -30 || angle > 30) {
        return Operation_Fail;  // 如果角度不在范围内，返回失败
    }

    // 将角度转换为偏差值，偏差值的范围为 -125 到 125，每 0.24° 对应一个偏差单位
    int offset = int(angle / 0.24);

    // 强制转换偏差值为无符号字节 (0~255)
    uint8_t offset_value = (offset + 256) % 256;  // 转为 uint8_t 类型

    // 如果需要保存偏差值
    if (save_to_memory) {
        // 首先发送调整偏差值命令
        t_FuncRet result = send_command(servo_id, SerialServo::SERVO_ANGLE_OFFSET_ADJUST[0], &offset_value, 1);
        if (result != Operation_Success) {
            return Operation_Fail;  // 如果发送失败，返回失败
        }

        // 然后保存偏差值
        result = send_command(servo_id, SerialServo::SERVO_ANGLE_OFFSET_WRITE[0], nullptr, 0);
        if (result != Operation_Success) {
            return Operation_Fail;  // 如果保存失败，返回失败
        }
    } else {
        // 不需要保存，直接调整偏差值
        t_FuncRet result = send_command(servo_id, SerialServo::SERVO_ANGLE_OFFSET_ADJUST[0], &offset_value, 1);
        if (result != Operation_Success) {
            return Operation_Fail;  // 如果发送失败，返回失败
        }
    }

    return Operation_Success;  // 返回成功状态
}
/* 
 * @description : 获取舵机的角度偏移值并转换为角度
 * @param {uint8_t} servo_id : 要获取偏移值的舵机 ID
 * @param {float&} angle_offset : 返回的角度偏移值，范围为 -30° 到 30°（单位：度）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the servo angle offset and convert it to angle
 * @param {uint8_t} servo_id : The ID of the servo to get the offset for
 * @param {float&} angle_offset : The returned angle offset, in the range of -30° to 30° (unit: degree)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_angle_offset(uint8_t servo_id, float& angle_offset) {
    // 发送 SERVO_ANGLE_OFFSET_READ 命令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_ANGLE_OFFSET_READ[0], nullptr, 0);
    if (result != Operation_Success) {
        return Operation_Fail;  // 发送命令失败
    }

    // 延迟 5ms 再接收数据
    delay(5);

    // 接收并解析返回的数据
    uint8_t params[256];  // 使用 uint8_t 类型的数组，与 receive_command 函数匹配
    size_t param_count = 0;  // 初始化参数计数器
    result = receive_command(SerialServo::SERVO_ANGLE_OFFSET_READ[0], SerialServo::SERVO_ANGLE_OFFSET_READ[2], params, &param_count);

    // 如果没有接收到数据，则返回 Operation_Wait
    if (result != Operation_Success || param_count == 0) {
        return Operation_Wait;  // 等待接收数据
    }

    // 获取偏差值（无符号字节，范围 0~255）
    uint8_t offset_value = params[0]; // 使用 uint8_t 直接接收

    // 转换为有符号字节，范围为 -125 到 125
    if (offset_value > 127) {
        // 处理负值偏差
        offset_value -= 256;
    }

    // 将偏差值转换为角度范围 -30 到 30 度
    angle_offset = offset_value * (30.0 / 125.0);

    // 判断偏差角度是否在合理范围内
    if (angle_offset < -30.0 || angle_offset > 30.0) {
        return Operation_Fail;  // 偏差角度超出范围
    }

    // 返回成功状态
    return Operation_Success;
}
/* 
 * @description : 获取舵机的角度偏移值并转换为角度
 * @param {uint8_t} servo_id : 要获取偏移值的舵机 ID
 * @param {float&} angle_offset : 返回的角度偏移值，范围为 -30° 到 30°（单位：度）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the servo angle offset and convert it to angle
 * @param {uint8_t} servo_id : The ID of the servo to get the offset for
 * @param {float&} angle_offset : The returned angle offset, in the range of -30° to 30° (unit: degree)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_angle_range(uint8_t servo_id, float min_angle, float max_angle) {
    // 判断最小和最大角度是否在 0~240度范围内
    if (min_angle < 0.0 || min_angle > 240.0) {
        return Operation_Fail;  // 异常：最小角度不在范围内
    }

    if (max_angle < 0.0 || max_angle > 240.0) {
        return Operation_Fail;  // 异常：最大角度不在范围内
    }

    // 判断最小和最大角度是否合理
    if (min_angle >= max_angle) {
        return Operation_Fail;  // 异常：最大角度小于或等于最小角度
    }

    // 将角度转换为指令所需的范围 0~1000，表示 0~240°，每 0.24° 对应一个单位
    int min_value = static_cast<int>(min_angle / 0.24);
    int max_value = static_cast<int>(max_angle / 0.24);

    // 取最大角度和最小角度的低八位和高八位
    uint8_t min_value_low = min_value & 0xFF;
    uint8_t min_value_high = (min_value >> 8) & 0xFF;

    uint8_t max_value_low = max_value & 0xFF;
    uint8_t max_value_high = (max_value >> 8) & 0xFF;

    // 创建指令参数数组并发送
    uint8_t params[] = {min_value_low, min_value_high, max_value_low, max_value_high};

    // 调用 send_command 发送指令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_ANGLE_LIMIT_WRITE[0], params, sizeof(params));

    if (result != Operation_Success) {
        return Operation_Fail;  // 如果发送失败，返回失败
    }

    return Operation_Success;  // 成功设置角度范围
}
/*
 * @description : 获取舵机的角度范围，包括最小角度和最大角度
 * @param {uint8_t} servo_id : 要获取角度范围的舵机 ID
 * @param {float*} min_angle : 返回的最小角度值，单位为度
 * @param {float*} max_angle : 返回的最大角度值，单位为度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the servo angle range, including minimum and maximum angle
 * @param {uint8_t} servo_id : The ID of the servo to get the angle range for
 * @param {float*} min_angle : The returned minimum angle value, in degrees
 * @param {float*} max_angle : The returned maximum angle value, in degrees
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_angle_range(uint8_t servo_id, float* min_angle, float* max_angle) {
    // 发送SERVO_ANGLE_LIMIT_READ命令
    uint8_t cmd = SerialServo::SERVO_ANGLE_LIMIT_READ[0];
    t_FuncRet result = send_command(servo_id,cmd, nullptr, 0);
    if (result != Operation_Success) {
        return Operation_Fail;  // 如果发送命令失败，返回失败
    }
    // 延迟5ms再接收数据
    delay(5);

    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_ANGLE_LIMIT_READ[2] - 3;
    result = receive_command(cmd,expected_params_len,params_received,&params_received_len);

    if (result != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;  // 如果接收失败或者返回的数据不正确，返回失败
    }

    // 解析最小角度值，低8位和高8位合并为一个16位整数
    int min_value = params_received[0] + (params_received[1] << 8);  // 合并低8位和高8位
    // 将min_value转换为角度值
    *min_angle = min_value * 0.24;

    // 判断最小角度是否在合理范围内
    if (*min_angle < 0.0 || *min_angle > 240.0) {
        return Operation_Fail;  // 最小角度不在合理范围内
    }

    // 解析最大角度值，低8位和高8位合并为一个16位整数
    int max_value = params_received[2] + (params_received[3] << 8);  // 合并低8位和高8位
    // 将max_value转换为角度值
    *max_angle = max_value * 0.24;

    // 判断最大角度是否在合理范围内
    if (*max_angle < 0.0 || *max_angle > 240.0) {
        return Operation_Fail;  // 最大角度不在合理范围内
    }

    // 判断最小角度是否小于最大角度
    if (*min_angle >= *max_angle) {
        return Operation_Fail;  // 最小角度不能大于或等于最大角度
    }

    return Operation_Success;  // 成功获取舵机角度范围
}
/*
 * @description : 设置舵机的输入电压范围（最小电压和最大电压）
 * @param {uint8_t} servo_id : 要设置电压范围的舵机 ID
 * @param {float} min_vin : 设置的最小电压值，单位为伏特（V）
 * @param {float} max_vin : 设置的最大电压值，单位为伏特（V）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set the input voltage range of the servo (min and max voltage)
 * @param {uint8_t} servo_id : The ID of the servo to set the voltage range for
 * @param {float} min_vin : The minimum voltage value to set, in volts (V)
 * @param {float} max_vin : The maximum voltage value to set, in volts (V)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_vin_range(uint8_t servo_id, float min_vin, float max_vin) {
    // 确保电压限制在有效范围内
    if (min_vin < 4.5f || min_vin > 14.0f || max_vin < 4.5f || max_vin > 14.0f || min_vin >= max_vin) {
        return Operation_Fail;  // 电压不在有效范围或最小电压大于最大电压，返回失败
    }

    // 将电压值转换为毫伏
    int min_vin_mV = static_cast<int>(min_vin * 1000);
    int max_vin_mV = static_cast<int>(max_vin * 1000);

    // 将电压值拆分为低8位和高8位
    uint8_t min_vin_low = min_vin_mV & 0xFF;
    uint8_t min_vin_high = (min_vin_mV >> 8) & 0xFF;
    uint8_t max_vin_low = max_vin_mV & 0xFF;
    uint8_t max_vin_high = (max_vin_mV >> 8) & 0xFF;

    // 创建参数数组
    uint8_t params[4] = {min_vin_low, min_vin_high, max_vin_low, max_vin_high};
    size_t params_len = sizeof(params) / sizeof(params[0]);  // 计算数组的长度

    t_FuncRet result = send_command(servo_id,SerialServo::SERVO_VIN_LIMIT_WRITE[0], params,params_len);
    // 调用 send_command 方法
    return result;
}
/*
 * @description : 获取舵机的输入电压范围（最小电压和最大电压）
 * @param {uint8_t} servo_id : 要获取电压范围的舵机 ID
 * @param {float&} min_vin : 返回的最小电压值，单位为伏特（V）
 * @param {float&} max_vin : 返回的最大电压值，单位为伏特（V）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the input voltage range of the servo (min and max voltage)
 * @param {uint8_t} servo_id : The ID of the servo to get the voltage range for
 * @param {float&} min_vin : The minimum voltage value returned, in volts (V)
 * @param {float&} max_vin : The maximum voltage value returned, in volts (V)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_vin_range(uint8_t servo_id, float& min_vin, float& max_vin) {
    // 发送 SERVO_VIN_LIMIT_READ 命令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_VIN_LIMIT_READ[0], nullptr, 0);
    if (result != Operation_Success) {
        return Operation_Fail;  // 发送失败，返回失败
    }
    // 延迟 5ms 再接收数据
    delay(5);
    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t cmd = SerialServo::SERVO_MOVE_TIME_READ[0]; 
    uint8_t expected_params_len = SerialServo::SERVO_VIN_LIMIT_READ[2] - 3;
    result = receive_command(cmd, expected_params_len,params_received,&params_received_len);

    if (result != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;  // 接收失败或数据不足，返回失败
    }

    // 解析最小电压值，低8位和高8位合并为一个16位整数
    int min_vin_mV = params_received[0] + (params_received[1] << 8);
    // 将 min_vin 转换为伏特单位
    min_vin = min_vin_mV / 1000.0f;

    // 判断最小电压是否在合理范围内
    if (min_vin < 4.5f || min_vin > 14.0f) {
        return Operation_Fail;  // 最小电压不在有效范围，返回失败
    }

    // 解析最大电压值，低8位和高8位合并为一个16位整数
    int max_vin_mV = params_received[2] + (params_received[3] << 8);
    // 将 max_vin 转换为伏特单位
    max_vin = max_vin_mV / 1000.0f;

    // 判断最大电压是否在合理范围内
    if (max_vin < 4.5f || max_vin > 14.0f) {
        return Operation_Fail;  // 最大电压不在有效范围，返回失败
    }

    // 判断最小电压是否小于最大电压
    if (min_vin >= max_vin) {
        return Operation_Fail;  // 最小电压大于或等于最大电压，返回失败
    }

    return Operation_Success;  // 成功获取舵机的电压限制值
}
/*
 * @description : 设置舵机的最大温度限制
 * @param {uint8_t} servo_id : 要设置温度限制的舵机 ID
 * @param {int} max_temp : 要设置的最大温度，单位为摄氏度（°C）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set the maximum temperature limit for the servo
 * @param {uint8_t} servo_id : The ID of the servo to set the temperature limit for
 * @param {int} max_temp : The maximum temperature to set, in degrees Celsius (°C)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_temp_range(uint8_t servo_id, int max_temp) {
    // 确保温度限制在有效范围内
    if (max_temp < 50 || max_temp > 100) {
        return Operation_Fail;  // 温度超出范围，返回失败
    }

    // 生成指令包
    uint8_t params[1] = { static_cast<uint8_t>(max_temp & 0xFF) };
    // 获取参数数组的长度
    size_t params_len = sizeof(params) / sizeof(params[0]);

    // 调用 send_command 方法发送设置温度限制指令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_TEMP_MAX_LIMIT_WRITE[0], params,params_len);

    if (result != Operation_Success) {
        return Operation_Fail;  // 如果指令发送失败，返回失败
    }

    return Operation_Success;  // 成功设置温度限制
}
/*
 * @description : 获取舵机的最大温度限制
 * @param {uint8_t} servo_id : 要读取温度限制的舵机 ID
 * @param {int&} max_temp_limit : 存储读取到的最大温度限制值
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the maximum temperature limit for the servo
 * @param {uint8_t} servo_id : The ID of the servo to get the temperature limit from
 * @param {int&} max_temp_limit : The variable to store the retrieved maximum temperature limit
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_temp_range(uint8_t servo_id, int& max_temp_limit) {
    // 发送 SERVO_TEMP_MAX_LIMIT_READ 命令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_TEMP_MAX_LIMIT_READ[0], nullptr, 0);
    if (result != Operation_Success) {
        return Operation_Fail;  // 发送失败，返回失败
    }
    // 延迟 5ms 再接收数据
    delay(5);
    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_TEMP_MAX_LIMIT_READ[2] - 3;
    result = receive_command(SerialServo::SERVO_TEMP_MAX_LIMIT_READ[0], expected_params_len,params_received,&params_received_len);
    if (result != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;  // 接收失败或数据不足，返回失败
    }

    // 获取最高温度限制值
    max_temp_limit = static_cast<int>(params_received[0]);  // 将 uint8_t 转换为 int 类型

    // 判断温度是否在合理范围内
    if (max_temp_limit < 50 || max_temp_limit > 100) {
        return Operation_Fail;  // 温度不在有效范围，返回失败
    }

    return Operation_Success;  // 成功获取舵机的最高温度限制值
}
/*
 * @description : 读取舵机的实时温度
 * @param {uint8_t} servo_id : 要读取温度的舵机 ID
 * @param {int&} temperature : 存储读取到的舵机实时温度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Read the current temperature of the servo
 * @param {uint8_t} servo_id : The ID of the servo to read the temperature from
 * @param {int&} temperature : The variable to store the retrieved temperature
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::read_servo_temp(uint8_t servo_id, int& temperature) {
    // 发送 SERVO_TEMP_READ 命令
    t_FuncRet result_s = send_command(servo_id, SerialServo::SERVO_TEMP_READ[0], nullptr,0);
    if (result_s != Operation_Success) {
        return Operation_Fail;  // 发送失败，返回失败
    }
    // 延迟 5ms 再接收数据
    delay(5);

    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_TEMP_READ[2] - 3;
    t_FuncRet result_r = receive_command(SerialServo::SERVO_TEMP_READ[0], expected_params_len,params_received,&params_received_len);

    if (result_r != Operation_Success || params_received_len < 1) {
        return Operation_Fail;  // 接收失败或数据不足，返回失败
    }

    // 获取温度值
    temperature = params_received[0];

    // 判断温度是否在合理范围内
    if (temperature < 0 || temperature > 100) {
        return Operation_Fail;  // 温度不在有效范围，返回失败
    }

    return Operation_Success;  // 成功获取舵机的实时温度
}
/*
 * @description : 读取舵机的电压
 * @param {uint8_t} servo_id : 要读取电压的舵机 ID
 * @param {float&} voltage : 存储读取到的舵机电压
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Read the voltage of the servo
 * @param {uint8_t} servo_id : The ID of the servo to read the voltage from
 * @param {float&} voltage : The variable to store the retrieved voltage
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::read_servo_voltage(uint8_t servo_id, float& voltage) {
    // 发送 SERVO_VIN_READ 命令
    t_FuncRet result_s = send_command(servo_id, SerialServo::SERVO_VIN_READ[0], nullptr,0);
    if (result_s != Operation_Success) {
        return Operation_Fail;  // 发送失败，返回失败
    }
    // 延迟 5ms 再接收数据
    delay(5);
    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_VIN_READ[2] - 3;
    t_FuncRet result_r = receive_command(SerialServo::SERVO_VIN_READ[0], expected_params_len,params_received,&params_received_len);
    if (result_r != Operation_Success || params_received_len < expected_params_len) {
        return Operation_Fail;  // 接收失败或数据不足，返回失败
    }

    // 将电压值的低高字节合并成一个整数
    uint16_t voltage_value = static_cast<uint16_t>(params_received[0]) + (static_cast<uint16_t>(params_received[1]) << 8);

    // 将电压值转换为伏特，电压范围 4.5V 到 12.0V
    voltage = voltage_value / 1000.0;

    // 判断电压是否在合理范围内
    if (voltage < 4.5 || voltage > 12.0) {
        return Operation_Fail;  // 电压不在有效范围，返回失败
    }

    return Operation_Success;  // 成功获取电压
}
/*
 * @description : 读取舵机的位置角度
 * @param {uint8_t} servo_id : 要读取位置的舵机 ID
 * @param {float&} position_angle : 存储读取到的舵机角度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Read the position angle of the servo
 * @param {uint8_t} servo_id : The ID of the servo to read the position from
 * @param {float&} position_angle : The variable to store the retrieved angle
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::read_servo_position(uint8_t servo_id, float& position_angle) {
    // 发送 SERVO_POS_READ 命令
    t_FuncRet result_s = send_command(servo_id, SerialServo::SERVO_POS_READ[0], nullptr,0);
    if (result_s != Operation_Success) {
        return Operation_Fail;  // 发送失败，返回失败
    }
    // 延迟 5ms 再接收数据
    delay(5);

    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_POS_READ[2] - 3;

    t_FuncRet result_r = receive_command(SerialServo::SERVO_POS_READ[0], expected_params_len,params_received,&params_received_len);
    if (result_r != Operation_Success || params_received_len < 2) {
        return Operation_Fail;  // 接收失败或数据不足，返回失败
    }

    // 将角度位置的低高字节合并为一个 16 位整数
    int16_t position_value = static_cast<int16_t>(params_received[0]) + (static_cast<int16_t>(params_received[1]) << 8);

    // 判断是否为负值
    if (position_value < 0) {
        position_value += 0x10000;  // 补码转换
    }

    // 将位置值转换为角度值，映射到 0~240° 范围
    position_angle = (position_value / 1000.0) * 240.0;

    // 判断角度值是否在合理范围内
    if (position_angle < 0 || position_angle > 240) {
        return Operation_Fail;  // 角度不在有效范围，返回失败
    }

    return Operation_Success;  // 成功获取角度位置
}
/*
 * @description : 设置舵机的工作模式和速度
 * @param {uint8_t} servo_id : 要设置的舵机 ID
 * @param {int} mode : 工作模式，可能的值为 `MODE_POSITION` 或 `MODE_MOTOR`
 * @param {int} speed : 电机模式下的速度（范围：-1000 至 1000）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set the servo's mode and speed
 * @param {uint8_t} servo_id : The ID of the servo to set
 * @param {int} mode : The mode to set, either `MODE_POSITION` or `MODE_MOTOR`
 * @param {int} speed : The speed in motor mode (range: -1000 to 1000)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_mode_and_speed(uint8_t servo_id, int mode, int speed) {
    // 检查模式是否合法
    if (mode != SerialServo::MODE_POSITION && mode != SerialServo::MODE_MOTOR) {
        return Operation_Fail;  // 无效模式，返回失败
    }

    uint8_t low_byte = 0;
    uint8_t high_byte = 0;

    // 如果是电机控制模式，检查转动速度是否合法
    if (mode == SerialServo::MODE_MOTOR) {
        if (speed < -1000 || speed > 1000) {
            return Operation_Fail;  // 电机速度超出范围，返回失败
        }

        // 转动速度转换为 unsigned short int 格式
        if (speed < 0) {
            // 负数转换为补码形式
            speed = (speed + 65536) % 65536;
        }

        // 取低八位数据和高八位数据
        low_byte = static_cast<uint8_t>(speed & 0xFF);
        high_byte = static_cast<uint8_t>((speed >> 8) & 0xFF);
    }

    // 创建一个 uint8_t 数组用于发送指令
    uint8_t params[4] = {static_cast<uint8_t>(mode), 0, low_byte, high_byte};
    size_t params_len = sizeof(params) / sizeof(params[0]);  // 计算数组的长度
    // 发送指令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_OR_MOTOR_MODE_WRITE[0], params,params_len);

    if (result != Operation_Success) {
        return Operation_Fail;  // 发送失败，返回失败
    }

    return Operation_Success;  // 成功设置模式和速度
}
/*
 * @description : 获取舵机的工作模式和速度
 * @param {uint8_t} servo_id : 要获取信息的舵机 ID
 * @param {int&} mode : 用于返回舵机的工作模式（位置控制模式或电机控制模式）
 * @param {int&} speed : 用于返回舵机的转动速度
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the servo's mode and speed
 * @param {uint8_t} servo_id : The ID of the servo to get information for
 * @param {int&} mode : To return the servo's mode (position or motor control mode)
 * @param {int&} speed : To return the servo's speed
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_mode_and_speed(uint8_t servo_id, int &mode, int &speed) {
    // 发送 SERVO_OR_MOTOR_MODE_READ 命令请求舵机工作模式和转动速度
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_OR_MOTOR_MODE_READ[0], nullptr, 0);
    if (result != Operation_Success) {
        return Operation_Fail;  // 如果命令发送失败，返回失败
    }

    // 延迟 5ms 给舵机一些时间响应
    delay(5);

    // 接收并解析返回的数据
    uint8_t params_received[4];
    size_t params_received_len = 0;
    uint8_t expected_params_len = SerialServo::SERVO_OR_MOTOR_MODE_READ[2] - 3;
    
    // 调用 receive_command 接收数据
    result = receive_command(SerialServo::SERVO_OR_MOTOR_MODE_READ[0], expected_params_len, params_received, &params_received_len);
    if (result != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;  // 接收失败或者数据长度不匹配，返回失败
    }

    // 解析舵机模式，0表示位置控制模式，1表示电机控制模式
    mode = params_received[0];
    if (mode != SerialServo::MODE_POSITION && mode != SerialServo::MODE_MOTOR) {
        return Operation_Fail;  // 如果模式无效，返回失败
    }

    // 如果是电机控制模式，返回速度值；如果是位置控制模式，返回速度值为0
    if (mode == SerialServo::MODE_MOTOR) {
        // 解析转动速度，低8位和高8位合并为一个16位整数
        speed = (params_received[2] + (params_received[3] << 8));
    } else {
        speed = 0;  // 位置控制模式下速度为0
    }

    return Operation_Success;  // 返回成功
}
/*
 * @description : 控制舵机电机的加载和卸载
 * @param {uint8_t} servo_id : 要操作的舵机 ID
 * @param {bool} unload : 如果为 `true` 则卸载电机，如果为 `false` 则装载电机
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Control the loading and unloading of the servo motor
 * @param {uint8_t} servo_id : The ID of the servo to operate on
 * @param {bool} unload : If `true`, unload the motor, if `false`, load the motor
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_motor_load(uint8_t servo_id, bool unload) {
    // 校验舵机ID的有效性
    if (servo_id < 1 || servo_id > 253) {
        return Operation_Fail;  // 舵机ID无效
    }

    // 卸载掉电 (0) 或装载电机 (1)
    uint8_t unload_value = unload ? 1 : 0;

    // 生成指令参数数组
    uint8_t params[1] = {unload_value};  // 包含卸载或装载的值

    size_t params_len = sizeof(params) / sizeof(params[0]);  // 计算参数数组的长度

    // 调用 send_command 方法发送指令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_LOAD_OR_UNLOAD_WRITE[0], params, params_len);

    if (result != Operation_Success) {
        return Operation_Fail;  // 发送命令失败
    }

    return Operation_Success;  // 返回成功
}
/*
 * @description : 获取舵机电机加载状态
 * @param {uint8_t} servo_id : 要查询的舵机 ID
 * @param {bool} motor_loaded : 返回舵机电机是否已加载的状态，`true` 表示已加载，`false` 表示未加载
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the loading status of the servo motor
 * @param {uint8_t} servo_id : The ID of the servo to query
 * @param {bool} motor_loaded : The result indicating whether the servo motor is loaded, `true` if loaded, `false` if not loaded
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_motor_load_status(uint8_t servo_id, bool &motor_loaded) {
    // 发送 SERVO_LOAD_OR_UNLOAD_READ 命令请求舵机电机状态
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_LOAD_OR_UNLOAD_READ[0], nullptr, 0);
    if (result != Operation_Success) {
        return Operation_Fail;  // 如果命令发送失败，返回失败
    }

    // 延迟 5ms 给舵机一些时间响应
    delay(5);

    // 接收并解析返回的数据
    uint8_t params_received[4];
    size_t params_received_len = 0;
    uint8_t expected_params_len = SerialServo::SERVO_LOAD_OR_UNLOAD_READ[2] - 3;
    
    // 调用 receive_command 接收数据
    result = receive_command(SerialServo::SERVO_LOAD_OR_UNLOAD_READ[0], expected_params_len, params_received, &params_received_len);
    if (result != Operation_Success || params_received_len != expected_params_len) {
        return Operation_Fail;  // 接收失败或者数据长度不匹配，返回失败
    }

    // 解析电机状态，0表示卸载，1表示装载
    uint8_t motor_status = params_received[0];
    if (motor_status != 0 && motor_status != 1) {
        return Operation_Fail;  // 如果电机状态值不正确，返回失败
    }

    // 如果电机状态为1，则表示电机已装载，返回成功并将motor_loaded赋值为true
    motor_loaded = (motor_status == 1);
    return Operation_Success;  // 返回成功
}
/*
 * @description : 设置舵机 LED 灯的亮灭状态
 * @param {uint8_t} servo_id : 要控制的舵机 ID
 * @param {bool} led_on : LED 是否亮起，`true` 表示亮起，`false` 表示熄灭
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set the servo LED light status
 * @param {uint8_t} servo_id : The ID of the servo to control
 * @param {bool} led_on : Whether the LED is on, `true` for on, `false` for off
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_led(uint8_t servo_id, bool led_on) {
    // 校验舵机ID的有效性
    if (servo_id < 1 || servo_id > 253) {
        return Operation_Fail;  // 舵机ID无效
    }
    // 设置LED灯的亮灭状态 (0为常亮，1为常灭)
    uint8_t led_value = led_on ? 1 : 0;
    // 生成指令参数数组
    uint8_t params[1] = {led_value};  // 包含LED状态的值
    size_t params_len = sizeof(params) / sizeof(params[0]);  // 计算参数数组的长度
    // 调用 send_command 方法发送指令
    t_FuncRet result = send_command(servo_id, SerialServo::SERVO_LED_CTRL_WRITE[0], params, params_len);
    if (result != Operation_Success) {
        return Operation_Fail;  // 发送命令失败
    }
    return Operation_Success;  // 成功设置LED灯状态
}
/*
 * @description : 获取舵机 LED 灯的状态
 * @param {uint8_t} servo_id : 要查询的舵机 ID
 * @param {bool} led_on : 读取到的 LED 状态，`true` 表示 LED 灯常灭，`false` 表示 LED 灯常亮
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the servo LED light status
 * @param {uint8_t} servo_id : The ID of the servo to query
 * @param {bool} led_on : The LED status read, `true` if the LED is always off, `false` if the LED is always on
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_led(uint8_t servo_id, bool &led_on) {
    // 校验舵机ID的有效性
    if (servo_id < 0 || servo_id > 253) {
        return Operation_Fail;  // 舵机ID无效
    }
    // 发送读取LED控制状态命令
    t_FuncRet result_s = send_command(servo_id, SerialServo::SERVO_LED_CTRL_READ[0], nullptr,0);
    if (result_s != Operation_Success) {
        return Operation_Fail;  // 发送命令失败
    }
    // 延时等待数据返回
    delay(5);
    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_MOVE_TIME_READ[2] - 3;
    t_FuncRet result_r = receive_command(SerialServo::SERVO_LED_CTRL_READ[0], expected_params_len,params_received,&params_received_len);
    if (result_r != Operation_Success) {
        return Operation_Fail;  // 接收数据失败
    }

    // 解析LED状态，0表示常亮，1表示常灭
    int led_status = params_received[0];  // 这里使用 int 类型来接收数据
    if (led_status != 0 && led_status != 1) {
        return Operation_Fail;  // 非法LED状态
    }
    // 设置LED状态的返回值：1表示LED常灭，0表示LED常亮
    led_on = (led_status == 1);
    return Operation_Success;  // 成功读取LED状态
}
/*
 * @description : 设置舵机 LED 报警状态
 * @param {uint8_t} servo_id : 要设置的舵机 ID
 * @param {uint8_t} alarm_code : 要设置的报警代码
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Set the servo LED alarm state
 * @param {uint8_t} servo_id : The ID of the servo to set
 * @param {uint8_t} alarm_code : The alarm code to set
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::set_servo_led_alarm(uint8_t servo_id, uint8_t alarm_code) {
    // 校验报警代码是否在合法范围内
    if (alarm_code != SerialServo::ERROR_NO_ALARM &&
        alarm_code != SerialServo::ERROR_OVER_TEMP &&
        alarm_code != SerialServo::ERROR_OVER_VOLT &&
        alarm_code != SerialServo::ERROR_OVER_TEMP_AND_VOLT &&
        alarm_code != SerialServo::ERROR_STALL &&
        alarm_code != SerialServo::ERROR_OVER_TEMP_AND_STALL &&
        alarm_code != SerialServo::ERROR_OVER_VOLT_AND_STALL &&
        alarm_code != SerialServo::ERROR_ALL) {
        return Operation_Fail;  // 无效的报警代码
    }

    // 生成指令参数数组
    uint8_t params[1] = {alarm_code};  // 包含报警代码的值

    size_t params_len = sizeof(params) / sizeof(params[0]);  // 计算参数数组的长度

    // 调用 send_command 方法发送指令
    t_FuncRet result = send_command(servo_id, 35, params, params_len);
    if (result != Operation_Success) {
        return Operation_Fail;  // 发送命令失败
    }

    return Operation_Success;  // 成功设置报警代码
}
/*
 * @description : 获取舵机 LED 故障报警状态
 * @param {uint8_t} servo_id : 要查询的舵机 ID
 * @param {uint8_t} alarm_value : 输出的报警值（通过引用传递）
 * @return {t_FuncRet} : 返回操作结果，成功时返回 `Operation_Success`，失败时返回 `Operation_Fail`
 * ===================================================
 * @description : Get the servo LED alarm status
 * @param {uint8_t} servo_id : The ID of the servo to query
 * @param {uint8_t} alarm_value : The alarm value output (passed by reference)
 * @return {t_FuncRet} : Return operation result, `Operation_Success` if successful, `Operation_Fail` if failed
 */
t_FuncRet SerialServo::get_servo_led_alarm(uint8_t servo_id, uint8_t &alarm_value) {
    // 发送 SERVO_LED_ERROR_READ 命令
    t_FuncRet result_s = send_command(servo_id, SerialServo::SERVO_LED_ERROR_READ[0], nullptr,0);
    if (result_s != Operation_Success) {
        return Operation_Fail;  // 发送命令失败
    }
    // 延迟 5ms 等待数据
    delay(5);
    // 接收并解析返回的数据
    uint8_t params_received[4];  
    size_t params_received_len = 0;  // 解析到的参数数量
    uint8_t expected_params_len = SerialServo::SERVO_LED_ERROR_READ[2] - 3;
    t_FuncRet result_r = receive_command(SerialServo::SERVO_LED_ERROR_READ[0], expected_params_len,params_received,&params_received_len);
    // 如果没有接收到数据，则返回失败
    if (result_r != Operation_Success || params_received_len == 0) {
        return Operation_Fail;
    }
    // 解析 LED 故障报警值
    alarm_value = static_cast<uint8_t>(params_received[0]);
    // 判断值是否在合法范围内
    if (alarm_value != SerialServo::ERROR_NO_ALARM &&
        alarm_value != SerialServo::ERROR_OVER_TEMP &&
        alarm_value != SerialServo::ERROR_OVER_VOLT &&
        alarm_value != SerialServo::ERROR_OVER_TEMP_AND_VOLT &&
        alarm_value != SerialServo::ERROR_STALL &&
        alarm_value != SerialServo::ERROR_OVER_TEMP_AND_STALL &&
        alarm_value != SerialServo::ERROR_OVER_VOLT_AND_STALL &&
        alarm_value != SerialServo::ERROR_ALL) {
        return Operation_Fail;  // 报警值不合法
    }
    // 返回成功，报警值已传递到 alarm_value 引用中
    return Operation_Success;
}

