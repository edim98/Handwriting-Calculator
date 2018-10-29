from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(9, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.IN)
GPIO.setup(15, GPIO.IN)
GPIO.setup(16, GPIO.IN)
GPIO.setup(14, GPIO.IN)
GPIO.setup(25, GPIO.IN)
GPIO.setup(26, GPIO.IN)
GPIO.setup(27, GPIO.IN)
state1 = GPIO.input(13)
state2 = GPIO.input(14)
state3 = GPIO.input(15)
sol1 = GPIO.input(25)
sol2 = GPIO.input(26)
sol3 = GPIO.input(27)


def waitACKBegin():
    while not (not state1 and state2 and not state3):
        i=0
    print("States")
    print(state1)
    print(state2)
    print(state3)

def waitACKOperation():
    while not (not state1 and state2 and state3):
        i=0
    print("States")
    print(state1)
    print(state2)
    print(state3)

def waitACKNumber1():
    while not (state1 and not state2 and not state3):
        i=0
    print("States")
    print(state1)
    print(state2)
    print(state3)

def waitACKNumber2():
    while not (state1 and not state2 and state3):
        i=0
    print("States")
    print(state1)
    print(state2)
    print(state3)

def waitACKSolution():
    while not (not state1 and not state2 and state3):
        i=0
    print("States")
    print(state1)
    print(state2)
    print(state3)

try:
    # BEGIN
    GPIO.output(2, GPIO.LOW)
    GPIO.output(3, GPIO.LOW)
    GPIO.output(4, GPIO.LOW)
    GPIO.output(5, GPIO.HIGH)
    print("ACK Begin")
    print(state1)
    print(state2)
    print(state3)
    if (not state1 and state2 and not state3):

    # ADD2
        GPIO.output(2, GPIO.LOW)
        GPIO.output(3, GPIO.HIGH)
        GPIO.output(4, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        GPIO.output(11, GPIO.HIGH)
    print("ACK Operation")
    waitACKOperation()

    # 3
    GPIO.output(2, GPIO.LOW)
    GPIO.output(3, GPIO.LOW)
    GPIO.output(4, GPIO.LOW)
    GPIO.output(5, GPIO.LOW)
    GPIO.output(11, GPIO.HIGH)
    GPIO.output(12, GPIO.HIGH)
    print("ACK number1")
    waitACKNumber1()

    # 2
    GPIO.output(11, GPIO.HIGH)
    GPIO.output(12, GPIO.LOW)
    print("ACK number2")
    waitACKNumber2()
    GPIO.output(2, GPIO.LOW)
    GPIO.output(3, GPIO.LOW)
    GPIO.output(4, GPIO.LOW)
    GPIO.output(5, GPIO.LOW)
    GPIO.output(6, GPIO.LOW)
    GPIO.output(7, GPIO.LOW)
    GPIO.output(8, GPIO.LOW)
    GPIO.output(9, GPIO.LOW)
    GPIO.output(10, GPIO.LOW)
    GPIO.output(11, GPIO.LOW)
    GPIO.output(12, GPIO.LOW)
    waitACKSolution()
    print("ACK Solution")
    print("Solution")
    print(sol1)
    print(sol2)
    print(sol3)
finally:
    print("ending")
