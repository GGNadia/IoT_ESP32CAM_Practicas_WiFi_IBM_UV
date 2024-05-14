from machine import Pin, RTC, Timer
import dht
import network
import urequests
import time
import ntptime

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'myWiFi'
password = '1234567890'

thirdparty = 'https://hook.us1.make.com/'
api_key = '27t4dzqqj9jcxwtx4g166nsey2oob0kg'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

sensor = dht.DHT11(Pin(15))

def read_sensor():
    global temp, hum
    temp = hum = 0
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        if isinstance(temp, (float, int)) and isinstance(hum, (float, int)):
            hum = round(hum, 2)
            return temp, hum
        else:
            return 'Invalid sensor readings.'
    except OSError as e:
        return 'Failed to read sensor.'

def timer_interrupt(t):
    try:
        global sensor_readings
        read_sensor()
        ntptime.settime()
      
        rtc = RTC()
        (year, month, day, weekday, hour, minute, second, milisecond) = rtc.datetime()
        hour -= 6
        rtc.init((year, month, day, weekday, hour, minute, second, milisecond))
        date = "{:02d}/{:02d}/{}".format(day, month, year)
        hour = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)

        sensor_readings = {'temperature': temp, 'humidity': hum, 'date': date, 'hour': hour}
        print(sensor_readings)
        delta_interrupt()  # Llama a la función para enviar los datos aquí
    except OSError as e:
        print('Failed to read/publish sensor readings.')

timer = Timer(-1)
timer.init(period=30000, mode=Timer.PERIODIC, callback=timer_interrupt)

def delta_interrupt():
    global sensor_readings
    request_headers = {'Content-Type': 'application/json'}
    request = urequests.post(thirdparty + api_key, json=sensor_readings, headers=request_headers)
    if 'error' in str(request.text):
        print('error')
        print(request.text)
    request.close()


