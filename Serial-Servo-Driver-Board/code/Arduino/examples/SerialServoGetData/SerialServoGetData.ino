#include <Arduino.h>
#include "serial_servo.h"

SerialServo servo(Serial2);  // 创建 SerialServo 对象，传入串口对象

void setup() {
    // 初始化串口
    Serial.begin(115200);  // 设置主串口波特率（用于串口调试）
    Serial2.begin(115200, SERIAL_8N1, 16, 17); // 参数分别为：波特率，数据位，起始引脚，停止引脚

}

void loop() {
    // 1. 控制舵机立即移动到指定角度并在指定时间内完成
    uint8_t servo_id = 1;  // 假设舵机ID为1
    float target_angle_1 = 90.0f;  // 目标角度为 90 度
    uint16_t move_time_1 = 1000;  // 转动时间为 1000 毫秒

    servo.move_servo_immediate(servo_id, target_angle_1, move_time_1);

    // 2. 获取舵机的当前预设角度和时间
    float current_angle_1 = 0.0f;
    uint16_t current_time_1 = 0;

    t_FuncRet result_get_1 = servo.get_servo_move_immediate(servo_id, &current_angle_1, &current_time_1);
    if (result_get_1 == Operation_Success) {
        Serial.print("Current angle_1: ");
        Serial.println(current_angle_1);
        Serial.print("Current time_1: ");
        Serial.println(current_time_1);
    } else {
        Serial.println("Failed to get servo move details.");
    }

    delay(1000);
    // 3. 控制舵机立即移动到指定角度并在指定时间内完成
    float target_angle_2 = 180.0f;  // 目标角度为 90 度
    uint16_t move_time_2 = 1000;  // 转动时间为 1000 毫秒

    servo.move_servo_immediate(servo_id, target_angle_2, move_time_2);

    // 4. 获取舵机的当前预设角度和时间
    float current_angle_2 = 0.0f;
    uint16_t current_time_2 = 0;

    t_FuncRet result_get_2 = servo.get_servo_move_immediate(servo_id, &current_angle_2, &current_time_2);
    if (result_get_2 == Operation_Success) {
        Serial.print("Current angle_2: ");
        Serial.println(current_angle_2);
        Serial.print("Current time_2: ");
        Serial.println(current_time_2);
    } else {
        Serial.println("Failed to get servo move details.");
    }
    delay(1000);
}