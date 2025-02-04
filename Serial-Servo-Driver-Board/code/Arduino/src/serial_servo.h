/**
  ******************************************************************************
* @Time    : 2025/1/24 下午1:59   
* @Author  : lilis           
* @File    : serial_servo.h    
* @version 1.0.0 
* @Description : TTL串口舵机驱动类
  ******************************************************************************
*/
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef serial_servo_h
#define serial_servo_h
/* Includes ------------------------------------------------------------------*/
#include <Arduino.h>
#include <HardwareSerial.h>
#include <assert.h> 
/* Data structure declaration-------------------------------------------------*/
/**
 * @brief 操作结果返回值类型
 * @description 该枚举类型定义了操作的返回值，用于指示操作的执行结果。
 * ===================================================
 * @brief Operation result return type
 * @description This enum defines the return values for operations, indicating the execution result.
 */
typedef enum
{
    Operation_Success = 1,
    Operation_Fail    = 0,
    Operation_Wait    = 2
} t_FuncRet;


/**
 * @class SerialServo
 * @brief TTL串口舵机驱动类
 * @description 该类用于控制TTL串口舵机，通过硬件串口进行通信，发送指令并控制舵机的运动。
 * 包含了对舵机的多种控制指令，如位置控制、电机控制、LED控制等。
 * ===================================================
 * @class SerialServo
 * @brief TTL serial servo driver class
 * @description This class is used to control TTL serial servos, communicate via hardware serial ports, send commands, and control servo movement.
 * It includes various control commands for the servo, such as position control, motor control, LED control, etc.
 */
class SerialServo {
public:
    // 常量：舵机指令
    static const uint8_t SERVO_MOVE_TIME_WRITE[2]; 
    static const uint8_t SERVO_MOVE_TIME_READ[3]; 
    static const uint8_t SERVO_MOVE_TIME_WAIT_WRITE[2]; 
    static const uint8_t SERVO_MOVE_TIME_WAIT_READ[3]; 
    static const uint8_t SERVO_MOVE_START[2]; 
    static const uint8_t SERVO_MOVE_STOP[2]; 
    static const uint8_t SERVO_ID_WRITE[2]; 
    static const uint8_t SERVO_ID_READ[3]; 
    static const uint8_t SERVO_ANGLE_OFFSET_ADJUST[2]; 
    static const uint8_t SERVO_ANGLE_OFFSET_WRITE[2]; 
    static const uint8_t SERVO_ANGLE_OFFSET_READ[3]; 
    static const uint8_t SERVO_ANGLE_LIMIT_WRITE[2]; 
    static const uint8_t SERVO_ANGLE_LIMIT_READ[3]; 
    static const uint8_t SERVO_VIN_LIMIT_WRITE[2]; 
    static const uint8_t SERVO_VIN_LIMIT_READ[3]; 
    static const uint8_t SERVO_TEMP_MAX_LIMIT_WRITE[2]; 
    static const uint8_t SERVO_TEMP_MAX_LIMIT_READ[3]; 
    static const uint8_t SERVO_TEMP_READ[3]; 
    static const uint8_t SERVO_VIN_READ[3]; 
    static const uint8_t SERVO_POS_READ[3]; 
    static const uint8_t SERVO_OR_MOTOR_MODE_WRITE[2]; 
    static const uint8_t SERVO_OR_MOTOR_MODE_READ[3]; 
    static const uint8_t SERVO_LOAD_OR_UNLOAD_WRITE[2]; 
    static const uint8_t SERVO_LOAD_OR_UNLOAD_READ[3]; 
    static const uint8_t SERVO_LED_CTRL_WRITE[2]; 
    static const uint8_t SERVO_LED_CTRL_READ[3]; 
    static const uint8_t SERVO_LED_ERROR_WRITE[2]; 
    static const uint8_t SERVO_LED_ERROR_READ[3]; 
    // 舵机工作模式
    static const uint8_t MODE_POSITION; // 位置控制模式
    static const uint8_t MODE_MOTOR;    // 电机控制模式
    // LED报警故障类型
    static const uint8_t ERROR_NO_ALARM;                // 无报警
    static const uint8_t ERROR_OVER_TEMP;               // 过温报警
    static const uint8_t ERROR_OVER_VOLT;               // 过压报警
    static const uint8_t ERROR_OVER_TEMP_AND_VOLT;      // 过温和过压报警
    static const uint8_t ERROR_STALL;                   // 堵转报警
    static const uint8_t ERROR_OVER_TEMP_AND_STALL;     // 过温和堵转报警
    static const uint8_t ERROR_OVER_VOLT_AND_STALL;     // 过压和堵转报警
    static const uint8_t ERROR_ALL;                     // 过温、过压和堵转报警
    // 读取命令集合
    static const uint8_t READ_COMMANDS[];
    // 构造函数：初始化串口
    SerialServo(HardwareSerial& uart);
    // 初始化串口，设置波特率
    t_FuncRet begin(unsigned long baudRate);
    // 计算校验和，确保数据的完整性和正确性
    t_FuncRet calculate_checksum(uint8_t* data, uint8_t length, uint8_t& checksum);
    // 构建舵机指令包
    t_FuncRet buildPacket(uint8_t servo_id, uint8_t cmd, uint8_t* params, size_t params_length,byte* packet);
    // 发送控制指令到舵机
    t_FuncRet send_command(uint8_t servo_id, uint8_t cmd, uint8_t* params, size_t params_length);
    // 接收并处理舵机返回的指令数据包
    t_FuncRet receive_command(uint8_t expected_cmd, uint8_t expected_params_len, uint8_t* params, size_t* params_len);
    // 立即控制舵机转动到指定角度
    t_FuncRet move_servo_immediate(uint8_t servo_id, float angle, uint16_t time_ms);
    // 获取舵机的预设角度和时间
    t_FuncRet get_servo_move_immediate(uint8_t servo_id, float* angle_value, uint16_t* time_value);
    // 控制舵机延迟转动到指定角度
    t_FuncRet move_servo_with_time_delay(uint8_t servo_id, float angle, uint16_t time_ms);
    // 获取舵机的预设角度和时间（延迟转动）
    t_FuncRet get_servo_move_with_time_delay(uint8_t servo_id, float &angle, uint16_t &time_ms);
    // 启动舵机的转动
    t_FuncRet start_servo(uint8_t servo_id);
    // 立即停止舵机转动并停在当前角度位置
    t_FuncRet stop_servo(uint8_t servo_id);
    // 设置舵机的新ID值
    t_FuncRet set_servo_id(uint8_t servo_id, uint8_t new_id);
    // 获取舵机的ID
    t_FuncRet get_servo_id(uint8_t servo_id, uint8_t* servo_id_value);
    // 根据角度值调整舵机的偏差
    t_FuncRet set_servo_angle_offset(uint8_t servo_id, float angle, bool save_to_memory);
    // 获取舵机的偏差角度
    t_FuncRet get_servo_angle_offset(uint8_t servo_id, float& angle_offset);
    // 设置舵机的最小和最大角度限制
    t_FuncRet set_servo_angle_range(uint8_t servo_id, float min_angle, float max_angle);
    // 获取舵机的角度限位
    t_FuncRet get_servo_angle_range(uint8_t servo_id, float* min_angle, float* max_angle);
    // 设置舵机的最小和最大输入电压限制
    t_FuncRet set_servo_vin_range(uint8_t servo_id, float min_vin, float max_vin);
    // 获取舵机的电压限制值
    t_FuncRet get_servo_vin_range(uint8_t servo_id, float& min_vin, float& max_vin);
    // 设置舵机的最高温度限制
    t_FuncRet set_servo_temp_range(uint8_t servo_id, int max_temp);
    // 获取舵机的内部最高温度限制值
    t_FuncRet get_servo_temp_range(uint8_t servo_id, int& max_temp_limit);
    // 获取舵机的实时温度
    t_FuncRet read_servo_temp(uint8_t servo_id, int& temperature);
    // 获取舵机的实时输入电压
    t_FuncRet read_servo_voltage(uint8_t servo_id, float& voltage);
    // 获取舵机的实时角度位置
    t_FuncRet read_servo_position(uint8_t servo_id, float& position_angle);
    // 设置舵机的工作模式和电机转速
    t_FuncRet set_servo_mode_and_speed(uint8_t servo_id, int mode, int speed);
    // 获取舵机的工作模式和转动速度
    t_FuncRet get_servo_mode_and_speed(uint8_t servo_id, int& mode, int& speed);
    // 设置舵机的电机是否卸载掉电
    t_FuncRet set_servo_motor_load(uint8_t servo_id, bool unload);
    // 获取舵机电机是否装载或卸载
    t_FuncRet get_servo_motor_load_status(uint8_t servo_id, bool &motor_loaded);
    // 设置舵机的LED灯的亮灭状态
    t_FuncRet set_servo_led(uint8_t servo_id, bool led_on);
    // 获取舵机LED的亮灭状态
    t_FuncRet get_servo_led(uint8_t servo_id, bool &led_on);
    // 设置舵机LED闪烁报警对应的故障值
    t_FuncRet set_servo_led_alarm(uint8_t servo_id, uint8_t alarm_code);
    // 获取舵机LED故障报警状态
    t_FuncRet get_servo_led_alarm(uint8_t servo_id, uint8_t &alarm_value);

private:      
    // 用于与舵机通信的Serial实例
    HardwareSerial* uart; 

};

#endif