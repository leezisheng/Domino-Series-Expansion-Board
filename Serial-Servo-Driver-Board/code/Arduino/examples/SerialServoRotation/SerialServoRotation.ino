#include <Arduino.h>
#include "serial_servo.h"

SerialServo servo(Serial2);  // 创建 SerialServo 对象，传入串口对象

void setup() {
    // 初始化串口
    Serial.begin(115200);  // 设置主串口波特率（用于串口调试）
    Serial2.begin(115200, SERIAL_8N1, 16, 17); // 参数分别为：波特率，数据位，起始引脚，停止引脚

}

void loop() {

    uint8_t servo_id = 1;  // 舵机ID为1
    delay(2000);
    servo.start_servo(servo_id);
    // 立即停止舵机转动并停在当前角度位置
    servo.stop_servo(servo_id);
    delay(1000);
}