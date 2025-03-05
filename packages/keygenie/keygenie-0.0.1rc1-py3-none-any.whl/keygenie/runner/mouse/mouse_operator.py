import time

import pyautogui

from keygenie.constant import screen_dpi

class MouseOperator:
    def drag(self, from_x, from_y, to_x=None, to_y=None, duration=0.5, down_sleep=0):
        if to_x is None:
            to_x = from_x
        if to_y is None:
            to_y = from_y
        pyautogui.mouseDown(from_x, from_y)
        pyautogui.sleep(down_sleep)
        pyautogui.moveTo(to_x, to_y, duration=duration)
        pyautogui.mouseUp(to_x, to_y)


    def safe_click(self, x, y, pixel: tuple = None, tolerance=10, before_sleep=0.5, after_sleep=0.5, max_waiting_time=10,
                   **kwargs):
        start_time = time.time()
        now_time = time.time()
        pyautogui.moveTo(x, y)
        while now_time - start_time < max_waiting_time:
            if pixel and not pyautogui.pixelMatchesColor(x * screen_dpi, y * screen_dpi, pixel, tolerance=tolerance):
                now_time = time.time()
                pyautogui.sleep(0.2)
                continue
            else:
                self.click(x, y, before_sleep=before_sleep, after_sleep=after_sleep, **kwargs)
                return

        raise RuntimeError(
            f'waiting time > {max_waiting_time}s, pixel in ({x}, {y}) = {pyautogui.pixel(x * screen_dpi, y * screen_dpi)} does not match target pixel {pixel}.')



    def click(self, x, y, before_sleep=0.0, after_sleep=0.0, **kwargs):
        if before_sleep > 0:
            pyautogui.sleep(before_sleep)
        pyautogui.click(x, y, **kwargs)
        if after_sleep > 0:
            pyautogui.sleep(after_sleep)


    def safe_scroll(self, value, after_sleep=1):
        pyautogui.scroll(value)
        pyautogui.sleep(after_sleep)
