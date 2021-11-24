from flask import Flask
app = Flask(__name__)
import threading
import time
import math
import sys
import RPi.GPIO as GPIO
import busio
import digitalio
import board
import datetime
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

mcp = None          # mcp object
chan2 = None        # LDR channel 2 on MCP
chan1 = None        # mcp channel 1 on MCP
button =  18        #physical pin 12

interval = 1
startTime = 0


#Setup
def setup():
    global mcp
    global chan2
    global chan1
    global button
    global startTime

    GPIO.setmode(GPIO.BCM)

    #create spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)    
    #Chip select
    cs = digitalio.DigitalInOut(board.D5)
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # create mcp object
    mcp = MCP.MCP3008(spi, cs)
    #analog input channels
    chan1 = AnalogIn(mcp, MCP.P1)
    chan2 = AnalogIn(mcp, MCP.P2)
    # Interrupt
    GPIO.add_event_detect(button, GPIO.RISING, callback=btn_Interrupt, bouncetime=300)

    print("{:<13}{:<20}{:<22}{:}".format("Runtime", "Temp Reading", "Temp","Light Reading"))

    startTime = time.time()

# Thread Function
def Thread():
    global mcp
    global chan2
    global chan1
    global interval
    global startTime

    x = threading.Timer(interval,Thread)
    x.daemon = True                             
    x.start()

    runtime = int(time.time()) - int(startTime)
    #  start the current thread 
    print("{:}{:<12}{:<20}{:0.3f} {:<15}{:}".format(runtime,"s",chan1.value, (chan1.voltage - 0.5)*100,"C", chan2.value))

@app.route('/')       
def btn_Interrupt(channel):
    global interval
    print("button clicked")
    start = time.time()
    time.sleep(0.2)

    while GPIO.input(button) == GPIO.HIGH:
        time.sleep(0.01)

    isTime = time.time() - start

    #Button is pressed for more than 8 seconds, time interval: 10s
    if isTime>=8:
        interval = 10

    #Button is pressed for more than 4 seconds, time interval: 5s
    elif isTime>=4:
        interval = 5

    #Default time interval: 1s
    else:
        interval = 1



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
    try:
       setup()
       Thread()

       while True:
             pass
      
    # clean GPIO
    except KeyboardInterrupt:
       print("\nExiting Program")
       GPIO.cleanup()