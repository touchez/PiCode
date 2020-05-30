# coding=UTF-8
import serial
import pynmea2
import socketio
import RPi.GPIO as GPIO
import time

# socket_server_ip = "http://192.168.2.137:9099?userId=树莓派1号"
socket_server_ip = "http://touchez.cn:9099?userId=树莓派1号"

#树莓派GPIO操作相关
GPIO.setmode(GPIO.BCM)

ENA=18
IN1=3
IN2=4

GPIO.setup(ENA,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)

GPIO.output(ENA,True)

####定义电机正转函数
def gogo():
    print('motor gogo')
    #GPIO.output(ENA,True)
    GPIO.output(IN1,True)
    GPIO.output(IN2,False)

###定义电机反转函数
def back():
    print('motor_back')
    #GPIO.output(ENA,True)
    GPIO.output(IN1,False)
    GPIO.output(IN2,True)

###定义电机停止函数
def stop():
    print('motor_stop')
    #GPIO.output(ENA,False)
    GPIO.output(IN1,False)
    GPIO.output(IN2,False)

###树莓派socketio相关
sio = socketio.Client()

@sio.on('openlock')
def on_open(data):
    print("openlock收到消息" + data)
    gogo()
    time.sleep(3.3)
    stop()

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('messageevent')
def on_msg(data):
    print("get msg:" + data)

sio.connect(socket_server_ip)

###树莓派GPS相关

###输出数据小数点位置往后了两位，此处前移两位
def fixPoint(str):
    index = str.find('.')
    str = str.replace('.', '')
    str_list = list(str)
    str_list.insert(index - 2, '.')
    return ''.join(str_list)


def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
        print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))
        lat = fixPoint(msg.lat)
        lon = fixPoint(msg.lon)
        sio.emit('gps', {'lat': lat, 'lon': lon})

serialPort = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)

while True:
    str = serialPort.readline().decode()
    parseGPS(str)
