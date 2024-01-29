import threading
import pyautogui
import keyboard
import time

# 指定目标位置的坐标
target_position = [0, 0]
countdown_time = 10
target_time = 5
count_click = 1

def on_keyboard_press(event):
    if event.name == 'x':
        current_position = pyautogui.position()
        target_position[0] = current_position.x
        target_position[1] = current_position.y
        print(' ' * 20, end='')  # 清空该行
        print("\r当前鼠标位置坐标：", current_position, end='')


def countdown_thread():
    global countdown_time
    global count_click
    while countdown_time > 0:
        print(' ' * 20, end='')  # 清空该行
        print(f"\r剩余时间：{int(countdown_time/60)}:{countdown_time%60:02d},已经成功点击{count_click}次！(按下ctrl+c暂停)", end='')
        countdown_time -= 1
        time.sleep(1)


if __name__ == '__main__':
    print("鼠标放至需要点击的位置，按下X就会记录该位置(可重复多次选择)，然后按下esc确认位置，并且会马上点击一次，然后进行循环至时间结束再次点击，周而复始")
    print("坐标确定后，鼠标会自动移动至该位置进行点击，时间默认设置为31分钟")
    # 监听键盘事件
    keyboard.on_press(on_keyboard_press)

    # 保持脚本运行
    print("按下’x‘，确认鼠标位置")
    print("按下’esc‘，开始执行循环")
    keyboard.wait('esc')

    print('开始循环')
    while True:
        try:
            countdown_time = target_time
            # 移动鼠标到目标位置
            pyautogui.moveTo(target_position[0], target_position[1])

            # 点击一次鼠标
            pyautogui.click()
            pyautogui.click()

            # 开启倒计时
            thread = threading.Thread(target=countdown_thread())
            thread.start()
            # 等待30分钟
            time.sleep(countdown_time)
            count_click += 1
        except KeyboardInterrupt:
            # 如果在执行过程中按下Ctrl+C，则终止循环
            break
