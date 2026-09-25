import parser
import os
import sys
import random
import time
from rich.live import Live
from rich.console import Group
from rich.text import Text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ASCII, DOUBLE, ASCII_DOUBLE_HEAD
from render import render_question 
from rich.align import Align

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
        elif key == b'\r':
            return 'enter'
        elif key == b'\x1b':
            return 'escape'
        elif key == b'\t':
            return 'tab'
    else: 
        fd = sys.stdin.fileno()
        start_terminal = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = os.read(fd, 1).decode('UTF-8', errors='ignore')
            if key in ('\n', '\r'):
                return 'enter'
            elif key == '\t':
                return 'tab'
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
                else:
                    return 'escape'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, start_terminal)
def clear_screen():
        if platform_flag:
            os.system('cls')
        else:
            os.system('clear')
def check_json():
    if not os.path.exists('ege_tasks.json'):
        print('необноруженно базы данных, хотите загрузить задачи? (Y/N)')
        installation = input().lower()
        if installation == 'y':
            parser.pars_install()
            task_parser = parser.use_pars()
        else:
            sys.exit()
    else:
        task_parser = parser.use_pars()
    clear_screen()
    return task_parser
#я хз че он вернет, будем думать
def number_quest(setting: dict[int, dict[str,any]], json_archiv:dict[any], key_mode:int):
    updatable = {}
    if key_mode == 0:    
        for n in setting:
            if setting[n]['diff'] == 4:
                pool = json_archiv[n]
                pool = random.sample(pool, setting[n]['counter'])
                updatable[n] = pool
            else:
                diff_err = setting[n]['diff'] - 1
                pool = [i for i in json_archiv[n] if i['difficulty'] == setting[n]['diff']]
                while diff_err >= 0:
                    if len(pool) < setting[n]['counter']:
                        pool.extend(i for i in json_archiv[n] if i['difficulty'] == diff_err)
                        diff_err -= 1
                    else:
                        break
                pool = random.sample(pool, setting[n]['counter'])
                updatable[n] = pool
    else:
        for n in json_archiv:
            updatable[n] = random.sample(json_archiv[n], 1)
    out_filter = []
    for n in list(updatable.values()):
        out_filter.extend(n)
    return out_filter, len(out_filter)

def start_information(tasks_received):
    def esc_funct():
        clear_screen()
        switch_esc = 0
        while True:
            if switch_esc == 0:
                esc_quest = '[underline green]да[/underline green] | нет'
            else:
                esc_quest = 'да | [underline green]нет[/underline green]'
            menu.update(Align(Group(Panel('Вы хотите выйти?', box=ASCII, title='[red]infotrain[/red]'), Text.from_markup(esc_quest, justify='center')), align='center'))
            key_esc = keyread()
            if key_esc == 'left':
                if switch_esc == 1:
                    switch_esc -= 1
            elif key_esc == 'right':
                if switch_esc == 0:
                    switch_esc += 1
            elif key_esc == 'enter':
                if switch_esc == 0:
                    sys.exit()
                else:
                    return None
    clear_screen()
    with Live('', refresh_per_second=10) as menu:
        select_one_menu = ['Свой вариант', 'Случайный варинат']
        select_num = 0
        while True:
            importer = []
            for index, named in enumerate(select_one_menu):
                if select_num == index:
                    symbl_select = '> '
                    named = f'[reverse bold]{named}[/reverse bold]'
                else:
                    symbl_select = '  '
                importer.append(f'{symbl_select}{named}')
            menu.update(Align(Panel('\n'.join(importer), box=ASCII, title='[red]infotrain[/red]', width=40), align='center'))
            key_menu = keyread()
            if key_menu == 'down':
                select_num = min(len(select_one_menu) - 1, select_num + 1)
            elif key_menu == 'up':
                select_num = max(0, select_num - 1)
            elif key_menu == 'enter':
                key_two_menu = select_num
                break
            elif key_menu == 'escape':
                sys.exit()
        if key_two_menu == 0:
            settings = {}
            switch_settings = 0
            menu.update(clear_screen())
            importer = [dump for i, dump in enumerate(tasks_received)]
            while True:
                visual_importer = []
                for i, task in enumerate(tasks_received):
                    if task in settings:
                        select_opt = f'[[green]X[/green]]'
                    else:
                        select_opt = '[ ]'
                    if select_num == i:
                        symbl_select = '> '
                        named = f'[reverse bold]задание {task}[/reverse bold]   {select_opt}'
                    elif select_num != i:
                        symbl_select = '  '
                        named = f'задание {task}   {select_opt}'
                    visual_importer.append(f'{symbl_select}{named}')
                
                if importer[select_num] in settings:
                    ccs = settings[importer[select_num]]
                    name_harder = ['легкая', 'средняя', 'сложная', 'гроб', 'случайная']
                    if switch_settings == 0:
                        settings_visual = f'[underline]Кол-во задач:[/underline] {ccs['counter']} | Сложность: {name_harder[ccs['diff']]}'
                    else:
                        settings_visual = f'Кол-во задач: {ccs['counter']} | [underline]Сложность[/underline]: {name_harder[ccs['diff']]}'
                else:
                    settings_visual = ' '
                        
                menu.update(Align(Group(Panel('\n'.join(visual_importer), box=ASCII, title='[red]infotrain[/red]', width=40), Text.from_markup(settings_visual, justify='center')), align='center'))
                key_menu = keyread()
                if key_menu == 'down':
                    select_num = min(len(importer) - 1, select_num + 1)
                elif key_menu == 'up':
                    select_num = max(0, select_num - 1)
                elif key_menu == 'enter':
                    if importer[select_num] not in settings:
                        settings.setdefault(importer[select_num], {'counter':1, 'diff':0})
                    else:
                        settings.pop(importer[select_num])
                elif key_menu == 'tab':
                    if switch_settings < 1:
                        switch_settings += 1
                    else:
                        switch_settings = 0
                elif key_menu == 'left':
                    if switch_settings == 0:
                        if importer[select_num] in settings and settings[importer[select_num]]['counter'] > 1:
                            settings[importer[select_num]]['counter'] -= 1
                    else:
                        if importer[select_num] in settings and settings[importer[select_num]]['diff'] > 0:
                            settings[importer[select_num]]['diff'] -= 1
                elif key_menu == 'right':
                    if switch_settings == 0:    
                        if importer[select_num] in settings and settings[importer[select_num]]['counter'] < 30:
                            settings[importer[select_num]]['counter'] += 1
                    else:
                        if importer[select_num] in settings and settings[importer[select_num]]['diff'] < 4:
                            settings[importer[select_num]]['diff'] += 1
                elif key_menu == 'escape':
                    if len(settings) > 0:
                        menu.stop()
                        return number_quest(settings, tasks_received, key_two_menu)
                    else:
                        esc_funct()
        elif key_two_menu == 1:
                      dump = 0
                      return number_quest(dump ,tasks_received,key_two_menu)

current_index = 0
answers = {}
True_answers = {}
end_information = {}
while True:
    bk_information, count = start_information(check_json())
    for i, task in enumerate(bk_information):
        True_answers[i] = task['answer']
    break
start_time = time.time()
while True:
    clear_screen()
    current_task = bk_information[current_index]
    if current_task['difficulty'] == 0:
        name_difficulty = 'Сложность: Легкая'
    elif current_task['difficulty'] == 1:
        name_difficulty = 'Сложность: Cредняя'
    elif current_task['difficulty'] == 2:
        name_difficulty = 'Сложность: Сложная'
    elif current_task['difficulty'] == 3:
        name_difficulty = 'Сложность: ГРОБ'
                        
    console.print(f"[bold yellow] ID({current_task['taskID']}) | Номер {current_task['number']}№ | ({name_difficulty}) | {current_task['comment']}[/bold yellow]")
    question_renderable = render_question(current_task['question'], current_task.get('tables', []))
    console.print(Panel(question_renderable,box=ASCII,title=f'{current_index + 1}/{count}'))
    if bk_information[current_index]['files'] != []:
        console.print(f'[dim] Файлы: [/dim]')
        for url in bk_information[current_index]['files']:
            console.print(f'[bold underline medium_purple2] {url} [/bold underline medium_purple2]') 
    if current_index in answers:
        console.print()
        console.print('-'*50, style="#095F79")
        console.print(f'Сохраненный ответ:[#0AB7CE] {answers[current_index]} [/#0AB7CE]')
        console.print('-'*50, style="#095F79")
    key = keyread() 
    if key == 'right':
            if current_index < count - 1:
                current_index += 1
    elif key == 'left':
            if current_index > 0:
                current_index -= 1
    
    elif key == 'enter':
        if current_index in answers:
            answer = input('\n Новый ответ: ')
        else:
            answer = input("\n  Ответ: ")
        answers[current_index] = answer
    elif key == 'escape':  
        stop_times = time.time() - start_time
        if stop_times > 3600:
            stop_time = f'{round(stop_times/3600, 2)}ч'
        elif stop_times > 60:
            stop_time = f'{round(stop_times/60, 2)}м'
        else:
            stop_time = f'{round(stop_times, 2)}c'
        break
for i in True_answers:
    if i not in answers:
       answers[i] = 0
count_true = 0
for key in answers:
    if answers[key] != True_answers[key]:
        end_information[key] = False
    else:
        end_information[key] = True
        count_true += 1

clear_screen()

end_table = Table(title='[#0AEBC5]| Результат тренировки |[/#0AEBC5]',box=ASCII_DOUBLE_HEAD, show_footer=True)
end_table.add_column('номер задачи; ID задачи', f' время: {stop_time}', footer_style='dim')
end_table.add_column('Ваши ответы', f' выполнено: {round((count_true / len(end_information) * 100), 2)}%', footer_style='dim')
end_table.add_column('Правильные ответы')
end_table.add_column('Идентификатор')

for i in range(count):
     if end_information[i] == True:
        end_table.add_row(f'[#0AEBC5]{bk_information[i]['number']}№; {bk_information[i]['taskID']}[/#0AEBC5]', f'[#0AEBC5]{answers[i]}[/#0AEBC5]', f'[#0AEBC5]{True_answers[i]}[/#0AEBC5]', f'[green]{end_information[i]}[/green]')
     else:
         end_table.add_row(f'[#0AEBC5]{bk_information[i]['number']}№; {bk_information[i]['taskID']}[/#0AEBC5]', f'[#0AEBC5]{answers[i]}[/#0AEBC5]', f'[#0AEBC5]{True_answers[i]}[/#0AEBC5]', f'[red]{end_information[i]}[/red]')
    
console.print(end_table)
input()
clear_screen()