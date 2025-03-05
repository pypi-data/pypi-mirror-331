import os
import tempfile

import pyautogui


def get_screen_dpi():
    mouse_screen_w, mouse_screen_h = pyautogui.size()  # pyautogui.size()是鼠标可以点击的点的分辨率
    with tempfile.TemporaryDirectory() as tmpdir:
        screenshot_img = pyautogui.screenshot(os.path.join(tmpdir, 'all_screen.png'))  # screenshot 是显示器的分辨率
        screen_dpi_w = int(screenshot_img.size[0] / mouse_screen_w)
        screen_dpi_h = int(screenshot_img.size[1] / mouse_screen_h)
        assert screen_dpi_w == screen_dpi_h
        screen_dpi = screen_dpi_w  # 一般mac上这个值是2
    return screen_dpi


screen_dpi = get_screen_dpi()
