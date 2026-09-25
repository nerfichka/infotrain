from rich.live import Live
import parser
import os
import sys
import random
import time
from rich.live import Live
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ASCII, DOUBLE, ASCII_DOUBLE_HEAD
from render import render_question 

console = Console()
platform_flag = True
if sys.platform == 'win32':
    import msvcrt
else:
    import tty
    import termios
    import select
    platform_flag = False
def keyread():
    if platform_flag:
        key = msvcrt.getch()
        if key in (b'\xe0', b'\x00'):
            key = msvcrt.getch()
            if key == b'M': 
                return 'right'
            elif key == b'K':
                return 'left'
            elif key == b'H':
                return 'up'
            elif key == b'P':
                return 'down'
            elif key == ' ':
                return 'space'
        elif key == b'\r':
            return 'enter'
        elif key == b'\x1b':
            return 'escape'
    else: 
        fd = sys.stdin.fileno()
        start_terminal = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = os.read(fd, 1).decode('UTF-8', errors='ignore')
            if key in ('\n', '\r'):
                return 'enter'
            elif key == '\x1b':
                newobj, dump1, dump2 = select.select([fd], [], [], 0.1)
                if newobj:
                    key2 = os.read(fd, 2).decode('UTF-8', errors='ignore')
                    if key2 == '[C':
                        return 'right'
                    elif key2 == '[D':
                        return 'left'
                    elif key2 == '[A':
                        return 'up'
                    elif key2 == '[B':
                        return 'down'
                    elif key2 == ' ':
                        return 'space'
                else:
                    return 'escape'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, start_terminal)
def start_information():
    cursor = 0
    choose_mode = ['Случайный вариант', 'Свой вариант']
    with Live('', refresh_per_second=10) as menu:
        while True:
            list = []
            for i, opt in enumerate(choose_mode):
                pretend = '> ' if i == cursor else ' '
                list.append(f'{pretend}{opt}')
            menu.update('\n'.join(list))
            key = keyread()
            if key == 'up':     cursor = max(0, cursor - 1)
            elif key == 'down': cursor = min(len(choose_mode) - 1, cursor + 1)
            elif key == 'enter': return cursor
            elif key == 'escape': sys.exit()
res = start_information()
print(res)
