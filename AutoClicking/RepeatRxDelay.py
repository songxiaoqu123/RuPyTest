from pykeyboard import *
from pymouse import *
import time

class UserMouse(PyMouse):

    def delay_click(self,x=0,y=0,button=1, n=1, delay=1):
        self.press(x=x,y=y,button=button)
        time.sleep(delay)
        self.release(x=x,y=y,button=button)

mouse =  UserMouse()
keyboard = PyKeyboard()


for i in range(100):
    time.sleep(5)
    mouse.delay_click(368, 78)      #click "Measure"


    time.sleep(2)
    mouse.delay_click(578,95)       #click "Rx_Delay"


    time.sleep(2)
    mouse.delay_click(578,128)      #click "OK"


    time.sleep(2)
    mouse.delay_click(1249,846)     #click "OK"


    time.sleep(2)
    mouse.delay_click(486,432)      #click "OK"
    time.sleep(100)


    time.sleep(2)
    mouse.delay_click(88,78)      #click "Reset"


    time.sleep(5)
    mouse.delay_click(460, 360)
    time.sleep(2)
    mouse.delay_click(460, 408)
    time.sleep(2)
    mouse.delay_click(460, 446)

    time.sleep(120)