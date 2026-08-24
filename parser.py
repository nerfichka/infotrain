import requests
import json
import time
from html_clean import clean_task_html

def pars_install():
    URL = "https://kompege.ru/api/v1/variant/random"
    all_tasks = []
    seen = set()
    symw = ['|', '/', '-', '\\']
    for i in range(100):
        try:
            print(f'Загрузка данных: {symw[len(all_tasks)%4]} {i}%', end='\r')
            resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=7)
            data = resp.json()

            for task in data.get("tasks", []):
                task_year = task.get('createdAt') or ''
                if len(task_year) < 4 or int(task_year[:4]) < 2023:
                    continue
                else:
                    task_id = task.get("taskId") or task.get("id", "")
                    if task_id not in seen:
                        seen.add(task_id)

                        file_urls = []
                        for f in task.get("files", []):
                            file_url = f.get("url", "") if isinstance(f, dict) else f
                            if file_url:
                                if not file_url.startswith('http'):
                                    file_url = "https://kompege.ru" + file_url
                                file_urls.append(file_url)

                        html_text = task.get("text", "")
                        clean_text, tables, img_urls = clean_task_html(html_text)
                        task_files = file_urls + img_urls

                        all_tasks.append({
                            "number": task.get("number"),
                            'taskID': task.get('taskId'),
                            'comment': task.get('comment', ""),
                            "question": clean_text,
                            "tables": tables,
                            "answer": task.get("key", ""),
                            "source": "kompege",
                            "createdAt": task.get("createdAt"),
                            "files": task_files
                        })
            time.sleep(0.05)

        except Exception as e:
            print(f"\n  Вариант {i}: ошибка - {e}")
            time.sleep(1)

    with open("ege_tasks.json", "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)
    print('\nУстановка завершена!')
def use_pars():
    with open("ege_tasks.json", 'r', encoding='utf-8') as file:
        task = json.load(file)
    filter_nums = {}
    for i in range(len(task)):
        numbers_ege = task[i]['number']
        if numbers_ege not in filter_nums:
            filter_nums[numbers_ege] = []
        filter_nums[numbers_ege].append({
                'number':task[i]['number'],
                'question':task[i]['question'],
                'tables':task[i].get('tables', []),
                'answer':task[i]['answer'],
                 'files':task[i]['files'],
                'taskID':task[i]['taskID'],
                'comment':task[i]['comment'],
                'createdAt':task[i]['createdAt']
                })
        
    return filter_nums
