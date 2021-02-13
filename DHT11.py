#encoding:utf-8

import RPi.GPIO as GPIO
from time import sleep

Hight = 1
Low   = 0

class DHT11:
    def __init__(self, data_pin):
        self.__IO_DATA  = data_pin
        self.humi_offset = 0x80   # 湿度补偿值128
        self.clk_offset  = 239    # 补偿并对齐读取bit时的时钟

    def get(self):
        try_cnt = 10
        raw_data_queue = []
        temperature = 0
        humidity    = 0
        temp     = 0  #温度整数
        temp_p   = 0  #温度小数
        hum      = 0  #湿度整数
        hum_p    = 0  #湿度小数
        checksum = 0  #校验和

        while try_cnt:
            raw_data_queue = self.__read_raw_data()
            if len(raw_data_queue) == 40:
                i = 0
                while i < 40:
                    tmp_byte = 0x0
                    bits = 7
                    while bits >= 0:
                        tmp_byte = (tmp_byte | (raw_data_queue[i] << bits))
                        bits -= 1
                        i += 1
                    if i == 8:
                        hum = tmp_byte ^ self.humi_offset
                    elif i == 16:
                        hum_p = tmp_byte
                    elif i == 24:
                        temp = tmp_byte
                    elif i == 32:
                        temp_p = tmp_byte
                    else:
                        checksum = tmp_byte

                #print("hum: ", hum, "hum_p: ", hum_p, "temp: ", temp, "temp_p: ", temp_p)
                #print("checksum: ", checksum, " | ", (hum + hum_p + temp + temp_p))
                if checksum == (hum + hum_p + temp + temp_p) and not(checksum == 0 and checksum==255) :
                    temperature = temp + self.convert_decimal(temp_p)
                    humidity    = hum  + self.convert_decimal(hum_p)
                    return (True, temperature, humidity)
            try_cnt -= 1
        return (False, -1, -1)

    def __read_raw_data(self):
        data_queue = []
        resp_low_timeout   = 1
        resp_hight_timeout = 1
        read_low_timeout   = 1

        GPIO.setup(self.__IO_DATA, GPIO.OUT)
        GPIO.output(self.__IO_DATA, Hight)
        sleep(1)

        # 唤醒DHT
        GPIO.output(self.__IO_DATA, Low)
        sleep(0.02)   # 等待20ms， 唤醒DHT
        GPIO.output(self.__IO_DATA, Hight)

        # 等待DHT响应
        GPIO.setup(self.__IO_DATA, GPIO.IN)
        i = 80
        while i:
            if GPIO.input(self.__IO_DATA) == Low:
                resp_low_timeout = 0
                break
            i -= 1

        i = 80
        while i:
            if GPIO.input(self.__IO_DATA) == Hight:
                resp_hight_timeout = 0
                break
            i -= 1

        #读取DHT数据： 40个bit
        j = 40
        while j:
            k = 0
            i = 80   
            read_low_timeout = 0
            while GPIO.input(self.__IO_DATA) == Low:
                if i <= 0:
                    read_low_timeout = 1 
                    break
                else:
                    i -= 1
            
            while GPIO.input(self.__IO_DATA) == Hight: 
                if k > 100: 
                    break
                else:
                    k += 1

            for i in range(self.clk_offset):
                continue
            
            #print('GPIO Read bit: ', k)
            if k <= 10:
                # 小于10次的，记为0
                data_queue.append(0)
            else:
                data_queue.append(1)
            j -= 1

        #print("Data Queue: ", data_queue)
        #print("resp_low_timeout: ", resp_low_timeout, "resp_hight_timeout: ", resp_hight_timeout, "read_low_timeout: ", read_low_timeout)
        GPIO.setup(self.__IO_DATA, GPIO.OUT)
        GPIO.output(self.__IO_DATA, Hight)
        return(data_queue)

    def convert_decimal(self, num):
        if num <= 30:
            return ( float(num) / 10)
        elif num > 10 and num <= 999:
            return ( float(num) / 100)


if __name__ == '__main__':
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    dht = DHT11(36)
    print(dht.get())


            


    
        
    
