import time, ustruct
from machine import Pin,UART
from micropython import const


SERVO_MOVE_TIME_WRITE       = const(1)
SERVO_MOVE_TIME_READ        = const(2)
SERVO_POS_READ              = const(28)
SERVO_MOVE_STOP             = const(12)
SERVO_ID_WRITE              = const(13)
SERVO_ID_READ               = const(14)

SERVO_ANGLE_OFFSET_ADJUST   = const(17)
SERVO_ANGLE_OFFSET_WRITE    = const(18)
SERVO_ANGLE_OFFSET_READ     = const(19)

SERVO_ANGLE_LIMIT_READ      = const(21)
SERVO_VIN_LIMIT_READ        = const(23)
SERVO_TEMP_MAX_LIMIT_READ   = const(25)

SERVO_VIN_READ              = const(27)
SERVO_OR_MOTOR_MODE_WRITE   = const(29)
SERVO_LOAD_OR_UNLOAD_WRITE  = const(31)
SERVO_LOAD_OR_UNLOAD_READ   = const(32)

SERVO_TEMP_READ             = const(26)

have_got_servo_pos = {}

def get_low8_byte(data):
  return (data & 0xFF)

def get_high8_byte(data):
  return ((data>>8) & 0xFF)
  
def byte_to_hw(a, b):
  return (a | (b << 8))
  
  
class BusServo:
  def __init__(self, tx=12, rx=35, tx_en=14, rx_en=13):
    self.rx_buf = [0x55]
    self.isAutoEnableRT = False
    if tx_en == None:
      self.isAutoEnableRT = True
      
    if self.isAutoEnableRT == False:
      self.tx_en = Pin(tx_en, Pin.OUT)
      self.rx_en = Pin(rx_en, Pin.OUT)
      self.rx_enable()
    
    self.uart = UART(2, 115200, tx=tx, rx=rx)

  def rx_enable(self):
    if self.isAutoEnableRT == False:
      self.rx_en.value(1)
      self.tx_en.value(0)
  
  def tx_enable(self):
    if self.isAutoEnableRT == False:
      self.rx_en.value(0)
      self.tx_en.value(1)
    
  def check_sum(self, data):
    sum = 0
    for i in range(2,data[3] + 2):
      sum += data[i]
    sum = ~sum
    return (sum & 0xFF)
    
  def send_data(self, data):
    self.tx_enable()
    for d in data:
      self.uart.write(ustruct.pack('B',d))
    if self.isAutoEnableRT == False:
      self.rx_en.value(1)
      self.tx_en.value(0)
  def run(self, id, p, servo_run_time = 1000):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(7)
    tx_buf.append(SERVO_MOVE_TIME_WRITE)
    tx_buf.append(get_low8_byte(p))
    tx_buf.append(get_high8_byte(p))
    tx_buf.append(get_low8_byte(servo_run_time))
    tx_buf.append(get_high8_byte(servo_run_time))
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)
  
  def run_mult(self, pp, servo_run_time):
    for p in enumerate(pp):
      self.run(p[0] + 1, p[1], servo_run_time)
   
  def run_add_or_dec(self, id, speed):
    try:
      pos = have_got_servo_pos[id]
    except:
      pos = self.get_position(id)
      if pos == False:
        return False

    pos += speed
    if pos < 0:pos = 0
    if pos > 1000:pos = 1000
    have_got_servo_pos[id] = pos
    self.run(id, pos, 20)
    return True
    
  def stop(self, id):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_MOVE_STOP)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

  def set_ID(self, old_id,new_id):
    tx_buf = [0x55,0x55]
    tx_buf.append(old_id)
    tx_buf.append(4)
    tx_buf.append(SERVO_ID_WRITE)
    tx_buf.append(new_id)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

  def get_ID(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(254)
    tx_buf.append(3)
    tx_buf.append(SERVO_ID_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return self.rx_buf[5]
    return False

  def set_mode(self, id, mode, speed = 0):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(7)
    tx_buf.append(SERVO_OR_MOTOR_MODE_WRITE)
    tx_buf.append(mode)
    tx_buf.append(0)
    tx_buf.append(get_low8_byte(speed))
    tx_buf.append(get_high8_byte(speed))
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)
    
  def load(self, id):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(4)
    tx_buf.append(SERVO_LOAD_OR_UNLOAD_WRITE)
    tx_buf.append(1)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)
    
  def unload(self, id):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(4)
    tx_buf.append(SERVO_LOAD_OR_UNLOAD_WRITE)
    tx_buf.append(0)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)
    
    
  def servo_receive_handle(self):
    frameStarted = False
    frameCount = 0
    dataCount = 0
    dataLength = 2
    self.rx_buf = [0x55]
    time_now = time.ticks_ms()
    while self.uart.any():
      buf = ustruct.unpack('B', self.uart.read(1))[0]
      time.sleep_us(100)
      if not frameStarted:
        if buf == 0x55:
          frameCount += 1
          if frameCount == 2:
            frameCount = 0
            frameStarted = True
            dataCount = 1
        else:
          frameStarted = False
          dataCount = 0
          frameCount = 0
        
      if frameStarted:
        self.rx_buf.append(buf)
        
        if dataCount == 3:
          dataLength = self.rx_buf[dataCount]
          if dataLength < 3 or dataLength > 7:
            dataLength = 2
            frameStarted = False
        dataCount += 1
        if dataCount == dataLength + 3:
          c = self.check_sum(self.rx_buf)
          if c == self.rx_buf[dataCount - 1]:
            return True
          return False
      if time.ticks_ms() - time_now > 1000:
        return False
    
  def get_position(self, id):
    self.uart.read()
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_POS_READ)
    tx_buf.append(self.check_sum(tx_buf))
    
    self.send_data(tx_buf)
    
    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return ustruct.unpack('h', ustruct.pack('H', byte_to_hw(self.rx_buf[5], self.rx_buf[6])))[0]
    return False

  def get_vin(self, id):
    self.uart.read()
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_VIN_READ)
    tx_buf.append(self.check_sum(tx_buf))
    
    self.send_data(tx_buf)
    
    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return byte_to_hw(self.rx_buf[5], self.rx_buf[6])
    return False

  def adjust_offset(self, id,offset):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(4)
    tx_buf.append(SERVO_ANGLE_OFFSET_ADJUST)
    tx_buf.append(offset)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

  def save_offset(self, id):
    tx_buf = [0x55,0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_ANGLE_OFFSET_WRITE)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

  def get_offset(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_ANGLE_OFFSET_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return ustruct.unpack('b',ustruct.pack('B',self.rx_buf[5]))[0]
    return False
    
  def get_temp(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_TEMP_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return self.rx_buf[5]
    return False
  
#--------------------------------------------------
  def get_AngleRange(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_ANGLE_LIMIT_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return ustruct.unpack('h', ustruct.pack('H', byte_to_hw(self.rx_buf[5], self.rx_buf[6])))[0],\
      ustruct.unpack('h', ustruct.pack('H', byte_to_hw(self.rx_buf[7], self.rx_buf[8])))[0]
    return False
  
  def get_VinLimit(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_VIN_LIMIT_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return ustruct.unpack('h', ustruct.pack('H', byte_to_hw(self.rx_buf[5], self.rx_buf[6])))[0],\
      ustruct.unpack('h', ustruct.pack('H', byte_to_hw(self.rx_buf[7], self.rx_buf[8])))[0]
    return False

  def get_TempLimit(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_TEMP_MAX_LIMIT_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return self.rx_buf[5]
    return False

  def get_LoadOrUnload(self, id):
    self.uart.read()
    tx_buf = [0x55, 0x55]
    tx_buf.append(id)
    tx_buf.append(3)
    tx_buf.append(SERVO_LOAD_OR_UNLOAD_READ)
    tx_buf.append(self.check_sum(tx_buf))
    self.send_data(tx_buf)

    time_now = time.ticks_ms()
    while self.uart.any() == 0:
      if time.ticks_ms() - time_now > 50:
        return False
    if self.servo_receive_handle():
      return self.rx_buf[5]
    return False



















