import filter
import parser
import os
import random
import time
import rich
import msvcrt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ASCII, DOUBLE, ASCII_DOUBLE_HEAD
from render import render_question 

console = Console()
def number_quest(task_dict,numbers, count):
    result = []
    counter = 0
    for i in numbers:
        i = int(i)
        if i in task_dict:
            random.shuffle(task_dict[i])
            result.extend(task_dict[i][:count])
    return result
def check_base():
    if not os.path.exists('ege_tasks.json'):
        print('необноруженно базы данных, хотите загрузить задачи? (Y/N)')
        installation = input().lower()
        if installation == 'y':
            parser.pars_install()
            task_parser = filter.loader('ege_tasks.json')
        else:
            exit()
    else:
        task_parser = filter.loader('ege_tasks.json')
    os.system('cls')
    return task_parser
def start_information():
    N_error_flag = False
    os.system('cls')
    console.print(Panel.fit("Выберите задания для тренировки.\nenter — все задания.",box=DOUBLE,title="infotrain", border_style="deep_sky_blue4"))
    console.print("[dim][#03a59d]Пример:[/#03a59d] 1,2,3,6,18 [/dim]\n [#03a59d]Управление: [/#03a59d]\n [#03a59d]enter:[/#03a59d] сохранить/изменить ответ \n [#03a59d]⭠/⭢ :[/#03a59d] переключение между заданиями \n [#03a59d]ESC: [/#03a59d]завершение заданий и переход к результатам")
    console.print("[deep_sky_blue4]Номера: [/deep_sky_blue4]", end='')
    select_ege_quest = input().split(',')
    if select_ege_quest == ['']:
        N_error_flag = True
        select_ege_quest = [int(i) for i in range(1,28)]

    console.print("[deep_sky_blue4]Количество на номер: [/deep_sky_blue4]")
    select_ege_nums = int(input())
    out_filter = check_base()
    start_processing = number_quest(out_filter,select_ege_quest,select_ege_nums)
    if N_error_flag:
        return start_processing, len(start_processing)
    else:
        return start_processing, len(select_ege_quest) * select_ege_nums
bk_information, count = start_information()
current_index = 0
answers = {}
True_answers = {}
end_information = {}
try:
    for i in range(count):
        True_answers[i] = bk_information[i]['answer']
except IndexError:
    os.system('cls')
    console.print('[red]Скорее всего, вы указали неверные номера. Попробуйте еще раз[/red]')
    console.print(time.sleep(3))
    bk_information.clear()
    count = 0
    bk_information, count = start_information()
    current_index = 0
start_time = time.time()
while True:
    os.system('cls')
    current_task = bk_information[current_index]
    console.print(f"[bold yellow] ID({current_task['taskID']}) | Номер {current_task['number']}№ | ({current_task['comment']})[/bold yellow]")
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
    key = msvcrt.getch()  
    if key in (b'\xe0', b'\x00'):
        key = msvcrt.getch()
        if key == b'M': 
            if current_index < count - 1:
                current_index += 1
        elif key == b'K':
            if current_index > 0:
                current_index -= 1
    
    elif key == b'\r':
        if current_index in answers:
            answer = input('\n Новый ответ: ')
        else:
            answer = input("\n  Ответ: ")
        answers[current_index] = answer
    elif key == b'\x1b':  
        stop_times = time.time() - start_time
        stop_time = f'{round(stop_times, 2)}c'
        if stop_times > 60:
            stop_time = f'{round(stop_times/60, 2)}м'
        elif stop_times > 3600:
            stop_time = f'{round(stop_times/3600, 2)}ч'
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

os.system('cls')

end_table = Table(title='[#0AEBC5]| Результат тренировки |[/#0AEBC5]',box=ASCII_DOUBLE_HEAD, show_footer=True)
end_table.add_column('номер задачи; ID задачи', f' время: {stop_time}', footer_style='dim')
end_table.add_column('Ваши ответы', f' выполнено: {round((count_true / len(end_information) * 100), 2)}%', footer_style='dim')
end_table.add_column('Правильные ответы')
end_table.add_column('Идентификатор')

for i in range(count):
     if end_information[i] == True:
        end_table.add_row(f'[#0AEBC5]{bk_information[i]['number']}№; {bk_information[i]['taskID']}[/#0AEBC5]', f'[#0AEBC5]{answers[i]}[/#0AEBC5]', f'[#0AEBC5]{True_answers[i]}[#0AEBC5]', f'[green]{end_information[i]}[/green]')
     else:
         end_table.add_row(f'[#0AEBC5]{bk_information[i]['number']}№; {bk_information[i]['taskID']}[/#0AEBC5]', f'[#0AEBC5]{answers[i]}[/#0AEBC5]', f'[#0AEBC5]{True_answers[i]}[#0AEBC5]', f'[red]{end_information[i]}[/red]')
    
console.print(end_table)