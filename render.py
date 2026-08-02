import re
from rich.console import Group
from rich.table import Table
from rich.text import Text
from rich.box import ASCII2

TABLE_PLACEHOLDER = re.compile(r'\[\[TABLE:(\d+)\]\]')


def build_table_widget(table_rows):
    tbl = Table(show_header=False, box=ASCII2, padding=(0, 1))
    if not table_rows:
        return tbl
    column_count = max(len(r) for r in table_rows)
    for _ in range(column_count):
        tbl.add_column(justify="center")
    for row in table_rows:
        padded_row = list(row) + [''] * (column_count - len(row))
        tbl.add_row(*padded_row)
    return tbl


def render_question(question_text, question_tables):
    rendered_parts = []
    last_position = 0
    for match in TABLE_PLACEHOLDER.finditer(question_text):
        text_before = question_text[last_position:match.start()].strip('\n')
        if text_before:
            rendered_parts.append(Text(text_before))
        table_index = int(match.group(1))
        if question_tables and 0 <= table_index < len(question_tables):
            rendered_parts.append(build_table_widget(question_tables[table_index]))
        last_position = match.end()
    text_after = question_text[last_position:].strip('\n')
    if text_after:
        rendered_parts.append(Text(text_after))
    if not rendered_parts:
        rendered_parts.append(Text(question_text))
    return Group(*rendered_parts)


if __name__ == '__main__':
    from rich.console import Console
    from rich.panel import Panel
    from html_clean import clean_task_html

    html = open('table_sample.html', encoding='utf-8').read()
    text, tables, files = clean_task_html(html)

    console = Console()
    console.print(Panel(render_question(text, tables), title="2/28"))