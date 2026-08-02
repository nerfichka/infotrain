import json
def loader(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        task = json.load(file)
    filter_nums = {}
    for i in range(len(task)):
        numbers_ege = task[i]['number']
        tasks_years = int(task[i]['createdAt'][:4])
        if numbers_ege not in filter_nums:
            filter_nums[numbers_ege] = []
        if tasks_years >= 2024:
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
