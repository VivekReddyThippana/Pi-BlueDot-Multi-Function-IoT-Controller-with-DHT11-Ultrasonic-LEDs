from bluedot import BlueDot
from signal import pause
import Adafruit_DHT
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import time

# GPIO Warnings off
GPIO.setwarnings(False)

# Initialize BlueDot
bd = BlueDot()

# DHT11 Sensor setup
sensor = Adafruit_DHT.DHT11
dht_pin = 4

# Buzzer and Ultrasonic Sensor pins
buzzer = 15
TRIG = 19
ECHO = 13

# LCD Setup
lcd = CharLCD('PCF8574', address=0x27, port=1, cols=16, rows=2, charmap='A00')

# LED pins setup
led_pins = [21, 16, 20, 12]

# GPIO mode and pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, GPIO.LOW)
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Distance measurement function with timeout
def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    timeout = start_time + 0.04  # 40ms timeout

    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start_time = time.time()

    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        end_time = time.time()

    if 'start_time' in locals() and 'end_time' in locals():
        duration = end_time - start_time
        distance = (duration * 34300) / 2
        return distance
    else:
        return -1  # Error or timeout

# BlueDot button logic
def dpad(pos):
    if pos.top:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, dht_pin)
        lcd.clear()
        if humidity is not None and temperature is not None:
            print(f"Humidity = {humidity}%, Temperature = {temperature}°C")
            lcd.write_string(f'Temp: {temperature:.1f}C')
            lcd.crlf()
            lcd.write_string(f'Hum: {humidity:.1f}%')
        else:
            lcd.write_string("Sensor Error")
            print("Failed to read from DHT sensor.")

    elif pos.bottom:
        lcd.clear()
        lcd.write_string("Turning LEDs on")
        print("Turning LEDs on")
        for _ in range(4):
            for pin in led_pins:
                GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.25)
            for pin in led_pins:
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.25)
        lcd.clear()
        lcd.write_string("LEDs blinked!")
        print("LEDs blinked!")

    elif pos.left:
        print("Buzzer ON")
        GPIO.output(buzzer, GPIO.HIGH)
        lcd.clear()
        lcd.write_string("Buzzer ON")
        time.sleep(2)
        GPIO.output(buzzer, GPIO.LOW)
        lcd.clear()
        lcd.write_string("Buzzer OFF")
        print("Buzzer OFF")

    elif pos.right:
        dist = measure_distance()
        lcd.clear()
        if dist != -1:
            lcd.write_string(f'Dist: {dist:.2f} cm')
            print(f"Distance: {dist:.2f} cm")
        else:
            lcd.write_string("No Echo!")
            print("Ultrasonic timeout")
        time.sleep(1)

    elif pos.middle:
        print("VEGA")

# Bind BlueDot event and run
bd.when_pressed = dpad

try:
    pause()
finally:
    GPIO.cleanup()
