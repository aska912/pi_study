#!/usr/bin/env python3
#encoding:utf-8

import TM1637

#------------------------------------------------------------------------
#               
#          a      Hight                              Low
#       __/       dp   g    f    e    d    c    b    a
#   g_f|__|b |    SG8  SG7  SG6  SG5  SG4  SG3  SG2  SG1
#     e|__|c |    1    0    1    1    1    1    1    1   0xBF ==> '0:'
#        |    \
#        d     dp
#
#------------------------------------------------------------------------
LED_FONTS = {
    '0':   0x3f,
    '1':   0x06,
    '2':   0x5b,
    '3':   0x4f,
    '4':   0x66,
    '5':   0x6d,
    '6':   0x7d,
    '7':   0x07,
    '8':   0x7f,
    '9':   0x6f,
    '0:':  0xbf,
    '1:':  0x86,
    '2:':  0xdb,
    '3:':  0xcf,
    '4:':  0xe6,
    '5:':  0xed,
    '6:':  0xfd,
    '7:':  0x87,
    '8:':  0xff,
    '9:':  0xef,
    'a':   0x77,
    'c':   0x39,
    'e':   0x79,
    'i':   0x06,
    'f':   0x71,
    'l':   0x38,
    'p':   0x73,
    'q':   0x6f,
    's':   0xed,
    'u':   0x3e,
    '-':   0x40,     #负号
    'o':   0x63,     #摄氏度的小圆圈
    'blank': 0x00,
}

BRIGHTNESS_ADJUST_RANGE = (TM1637.PULSE_WIDTH['1/16'],   \
                           TM1637.PULSE_WIDTH['2/16'],   \
                           TM1637.PULSE_WIDTH['4/16'],   \
                           TM1637.PULSE_WIDTH['10/16'],   \
                           TM1637.PULSE_WIDTH['11/16'],   \
                           TM1637.PULSE_WIDTH['12/16'],   \
                           TM1637.PULSE_WIDTH['13/16'],   \
                           TM1637.PULSE_WIDTH['14/16'])

MAX_BRIGHTNRSS = 5
MID_BRIGHTNRSS = 2
MIN_BRIGHTNRSS = 0


class four_digital_led:
    def __init__(self, clk_pin, dio_pin):
        self.tm1637 = TM1637.TM1637(clk_pin, dio_pin)
        self.tm1637.init()
        self.brightness = BRIGHTNESS_ADJUST_RANGE[MID_BRIGHTNRSS]
        self.__data_buff = None
        self.__grid_list = (self.tm1637.GRID1, \
                            self.tm1637.GRID2, \
                            self.tm1637.GRID3, \
                            self.tm1637.GRID4)

    def adjust_brightness(self, brightness):
        if brightness <= 0:
            self.brightness = MIN_BRIGHTNRSS
        elif brightness >= len(BRIGHTNESS_ADJUST_RANGE):
            self.brightness = MAX_BRIGHTNRSS
        else:
            self.brightness = brightness

    def write_data(self, data_1, data_2, data_3, data_4):
        self.__data_buff = ( (self.__grid_list[0], data_1),   \
                             (self.__grid_list[1], data_2),   \
                             (self.__grid_list[2], data_3),   \
                             (self.__grid_list[3], data_4) )

    def display(self):
        if self.__data_buff is not None:
            self.tm1637.set_mode_as_display()
            self.tm1637.set_addr_as_fixed()
            for addr_and_data in self.__data_buff:
                if len(addr_and_data):
                    addr = addr_and_data[0]
                    data = addr_and_data[1]
                    self.tm1637.write_data_to_addr(addr, data)
                else:
                    continue
            self.tm1637.turn_on_led(self.brightness)
        del self.__data_buff
        self.__data_buff = None
    


if __name__ == "__main__":
    import RPi.GPIO as GPIO
    import time
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    clk = 16
    dio = 18
    delay = 6

    led = four_digital_led(clk, dio)
    led.adjust_brightness(MIN_BRIGHTNRSS)
    while True:

        dp = 0
        for cnt in range(15):
            now_time=time.localtime(time.time())
            time_mon  = now_time[1]
            time_mday = now_time[2]
            time_hour = now_time[3]
            time_min  = now_time[4]
            #time_sec  = now_time[5]
            hour_ge  = time_hour % 10      #小时树的个位数
            hour_shi = int(time_hour / 10) #小时数的十位数
            min_ge   = time_min % 10
            min_shi  = int(time_min / 10)
            if hour_shi:
                hour_shi_led_font = LED_FONTS['%d'%hour_shi]
            else:
                hour_shi_led_font = LED_FONTS['blank']
            dp = dp ^ 1  # 冒号显示，每秒亮暗交替。异或：相同为0,不同为1
            if dp:
                led.write_data(hour_shi_led_font, LED_FONTS['%d:'%hour_ge], LED_FONTS['%d'%min_shi], LED_FONTS['%d'%min_ge])
            else:
                led.write_data(hour_shi_led_font, LED_FONTS['%d'%hour_ge], LED_FONTS['%d'%min_shi], LED_FONTS['%d'%min_ge])
            led.display()
            time.sleep(1)

        mon_shi  = int(time_mon / 10)
        mon_ge   = time_mon % 10
        mday_shi = int(time_mday / 10)
        mday_ge  = time_mday % 10
        if mon_shi:
            mon_shi_led_font = LED_FONTS['%d'%mon_shi]
        else:
            mon_shi_led_font = LED_FONTS['blank']
    
        if mday_shi:
            mday_shi_led_font = LED_FONTS['%d'%mday_shi]
        else:
            mday_shi_led_font = LED_FONTS['blank']
        led.write_data(mon_shi_led_font, LED_FONTS['%d'%mon_ge], mday_shi_led_font, LED_FONTS['%d'%mday_ge])
        led.display()
        time.sleep(delay)

        cpu_temp = -1
        try:
            fn = open('/sys/class/thermal/thermal_zone0/temp', 'r') 
            cpu_temp = int(float(fn.read()) /1000)
            fn.close()
        except:
            pass
        #print("CPU Tempture: ", cpu_temp, '\'C')
        if not cpu_temp == -1:
            cpu_temp_shi  = cpu_temp / 10
            cpu_temp_ge   = cpu_temp % 10
            data_queue    = [ LED_FONTS['blank'], LED_FONTS['c'], LED_FONTS['p'], LED_FONTS['u'], LED_FONTS['blank'], \
                              LED_FONTS['%d'%cpu_temp_shi], LED_FONTS['%d'%cpu_temp_ge], LED_FONTS['o'], LED_FONTS['c'] ]
            display_queue = [LED_FONTS['blank'], LED_FONTS['blank'], LED_FONTS['blank'], LED_FONTS['blank']]

            # 流水灯模式， 向左移动
            for i in range( len(data_queue) ):
                display_queue.pop(0)
                display_queue.append(data_queue[i])
                led.write_data(display_queue[0], display_queue[1], display_queue[2], display_queue[3])
                led.display()
                time.sleep(0.6)
        else:
            led.write_data(LED_FONTS['blank'], LED_FONTS['e'], LED_FONTS['-'], LED_FONTS['3'])
            led.display()
        time.sleep(delay)

        



