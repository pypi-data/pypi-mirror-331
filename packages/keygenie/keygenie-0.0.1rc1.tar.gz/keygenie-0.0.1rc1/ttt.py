import pyautogui

from keygenie.runner.mouse.mouse_operator import MouseOperator

mouse_operator = MouseOperator()


mouse_operator.safe_click(872, 418, pixel=(50, 50, 50), tolerance=10)
mouse_operator.safe_click(929, 291, pixel=(50, 50, 50), tolerance=10)
mouse_operator.drag(905, 596, to_x=669, to_y=555)
pyautogui.doubleClick(829, 743)