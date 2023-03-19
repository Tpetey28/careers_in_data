import pyautogui
import time

while True:
    for i in range(0,100):
        pyautogui.moveTo(1000,i*10)
        pyautogui.press('shift')
        time.sleep(5)

        
