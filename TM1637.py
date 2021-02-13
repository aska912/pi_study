#encoding:utf-8

import RPi.GPIO as GPIO

Hight = 1
Low   = 0

PULSE_WIDTH = {
    '1/16':   0x0, #最暗
    '2/16':   0x1,
    '4/16':   0x2,
    '10/16':  0x3,
    '11/16':  0x4,
    '12/16':  0x5,
    '13/16':  0x6,
    '14/16':  0x7, #最暗
}

class TM1637:
    def __init__(self, clk_pin, dio_pin):
        self.__clk = clk_pin
        self.__dio = dio_pin

    @property
    def CLK(self):
        return self.__clk

    @property
    def DIO(self):
        return self.__dio

    @property
    def GRID1(self):
        return 0xc0

    @property
    def GRID2(self):
        return 0xc1

    @property
    def GRID3(self):
        return 0xc2

    @property
    def GRID4(self):
        return 0xc3

    @property
    def GRID5(self):
        return 0xc4

    @property
    def GRID6(self):
        return 0xc6

    def init(self):
        GPIO.setup(self.__clk, GPIO.OUT)
        GPIO.setup(self.__dio, GPIO.OUT)

    def set_mode_as_display(self):
        self.__send_cfg_cmd(0x40)

    def set_mode_as_keyscan(self):
        self.__send_cfg_cmd(0x42)

    def set_addr_as_fixed(self):
        self.__send_cfg_cmd(0x44)

    def set_addr_as_auto(self):
        pass
        #self.__send_cfg_cmd(0x40)

    def turn_off_led(self):
        self.__send_cfg_cmd(0x80)

    def turn_on_led(self, pulse_width=0x0):
        self.__send_cfg_cmd( (0x88 | pulse_width) )

    def write_data_to_addr(self, addr, data):
        self.__start()
        self.__write_byte(addr)
        self.__write_byte(data)
        self.__stop()

    def __write_byte(self, data):
        # DIO写8个bit
        for i in range(0, 8):
            GPIO.output(self.__clk, Low)
            if (data >> i) & 0x01:
                GPIO.output(self.__dio, Hight)
            else:
                GPIO.output(self.__dio, Low)
            GPIO.output(self.__clk, Hight)

        # DIO写完一个byte，等待ACK
        GPIO.output(self.__clk, Low)
        GPIO.output(self.__dio, Hight)
        GPIO.output(self.__clk, Hight)
        GPIO.setup(self.__dio, GPIO.IN)
        for i in range(10):
            if GPIO.input(self.__dio) == Hight:
                break
        #while( GPIO.input(self.__dio) ):
        #    pass
        GPIO.setup(self.__dio, GPIO.OUT)

    def __send_cfg_cmd(self, cmd):
        self.__start()
        self.__write_byte(cmd)
        self.__stop()

    def __start(self):
        GPIO.output(self.__clk, Hight) #时钟打高电平
        GPIO.output(self.__dio, Hight)
        GPIO.output(self.__dio, Low)
        GPIO.output(self.__clk, Low) #时钟打低电平

    def __stop(self):
        GPIO.output(self.__dio, Low) 
        GPIO.output(self.__clk, Low)
        GPIO.output(self.__clk, Hight)
        GPIO.output(self.__dio, Hight) 
        
    