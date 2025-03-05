import time
import sys
import os

from keygenie.constant import screen_dpi
from keygenie.utils.decorator import singleton

project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_path)

from pynput.mouse import Listener as Mouse_Listener

import tempfile

import pyautogui
from pynput.keyboard import Controller, Key, Listener as Keyboard_Listener


# todo 已知bug1：启动时偶发会有个KeyError: 'CFMachPortCreateRunLoopSource'，会导致键盘记录不了，如遇到，重新试着开几次
# todo bug2: 退出程序的话在项目目录下保存一个临时图片，好像是pyautogui.pixel的问题

@singleton
class MyListener(object):
    def __init__(self, guarantee=True):
        self.guarantee = guarantee # 保证鼠标点击前的位置像素值是正确的
        self.key_map = {
            Key.cmd: 'ctrl',
            Key.cmd_r: 'ctrl',
            Key.alt: 'option',
            Key.alt_r: 'option',
            Key.shift_r: 'shift',
        }
        self.key_stack = []
        self.max_key_stack = []

        self.total_scroll = 0

        self.pressed_xy = (0, 0)

        self.last_click_print = None
        self.last_click_print_time = time.time()
        
        self.print_line_list = []

    def print_hot_key(self):
        key_list = []
        # self.print_line_list.append(self.max_stack)
        for item in self.max_key_stack:
            if isinstance(item, str):
                key_list.append(item)
            else:
                try:
                    key_list.append(self.key_map[item])
                except:
                    key_list.append(str(item)[4:])  # 'Key.backspace' 如果不在self.key_map里，那就用backspace
        print_str = ''.join([f"'{key}', " for key in key_list])
        if 'q' in print_str:
            raise KeyError('Finish.')
        self.print_line_list.append(f"pyautogui.hotkey({print_str[:-2]})")

    def on_key_press(self, key):
        try:
            self.key_stack.append(key.char)
        except AttributeError:
            self.key_stack.append(key)
        self.max_key_stack = self.key_stack.copy()

    def on_key_release(self, key):
        if self.key_stack:
            self.key_stack.pop()
        if not self.key_stack and self.max_key_stack:
            self.print_hot_key()

    def on_scroll(self, x, y, dx, dy):
        if dx != 0:
            print('dx = ', dx)
        if dy != 0:
            print('dy = ', dy)
        if dx != 0:
            self.total_scroll = self.total_scroll + dx
        else:
            if self.total_scroll != 0:
                self.print_line_list.append(f"total_scroll = {self.total_scroll}")
            self.total_scroll = 0
        if dy != 0:
            self.total_scroll = self.total_scroll + dy
        else:
            if self.total_scroll != 0:
                self.print_line_list.append(f"total_scroll = {self.total_scroll}")
            self.total_scroll = 0

    def on_click(self, x, y, button, is_press):
        # self.print_line_list.append(f"鼠标{button}键在({x}, {y})处{'按下' if is_press else '松开'}")
        x = round(x)
        y = round(y)
        if is_press:
            self.pressed_xy = (x, y)
            self.pixel_before_press = pyautogui.pixel(x * screen_dpi, y * screen_dpi)
        if not is_press:
            if x == self.pressed_xy[0] and y == self.pressed_xy[1]:
                if self.guarantee:
                    now_click_print = f'mouse_operator.safe_click({x}, {y}, pixel={self.pixel_before_press[0], self.pixel_before_press[1], self.pixel_before_press[2]}, tolerance=10)'
                else:
                    now_click_print = f'pyautogui.click({x}, {y})'
                now_click_print_time = time.time()
                # self.print_line_list.append('now_click_print = ', now_click_print)
                # self.print_line_list.append('self.last_click_print = ', self.last_click_print)
                # if now_click_print != self.last_click_print:
                #     # self.print_line_list.append(now_click_print)
                #     pass
                # else:
                    # self.print_line_list.append(now_click_print_time - self.last_click_print_time )
                if now_click_print_time - self.last_click_print_time > 0.5:
                    self.print_line_list.append(now_click_print)
                else:
                    if now_click_print == self.last_click_print:
                        self.print_line_list.pop()
                        self.print_line_list.append(f'pyautogui.doubleClick({x}, {y})')
                    else:
                        self.print_line_list.append(now_click_print)
                self.last_click_print_time = time.time()
                self.last_click_print = now_click_print
            else:
                self.print_line_list.append(f'mouse_operator.drag({self.pressed_xy[0]}, {self.pressed_xy[1]}, to_x={x}, to_y={y})')

    def start_listen(self):
        try:
            print('###start###')
            self.print_line_list.append('''import pyautogui\n
from keygenie.runner.mouse.mouse_operator import MouseOperator\n
mouse_operator = MouseOperator()\n
''')
            mouse_listen_thread = Mouse_Listener(on_click=self.on_click, on_scroll=self.on_scroll)
            mouse_listen_thread.start()

            keyboard_listen_thread = Keyboard_Listener(on_press=self.on_key_press, on_release=self.on_key_release)
            keyboard_listen_thread.start()
            keyboard_listen_thread.join()
        except:
            _ = [print(line) for line in self.print_line_list]
            return self.print_line_list


if __name__ == '__main__':
    result = MyListener().start_listen()
    # print(result)
