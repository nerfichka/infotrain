import re
from bs4 import BeautifulSoup, NavigableString

SUP_MAP = {
    '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹',
    '+':'⁺','-':'⁻','–':'⁻','=':'⁼','(':'⁽',')':'⁾','n':'ⁿ','i':'ⁱ',
    'a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ','g':'ᵍ','h':'ʰ','j':'ʲ',
    'k':'ᵏ','l':'ˡ','m':'ᵐ','o':'ᵒ','p':'ᵖ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ',
    'v':'ᵛ','w':'ʷ','x':'ˣ','y':'ʸ','z':'ᶻ',
}
SUB_MAP = {
    '0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉',
    '+':'₊','-':'₋','–':'₋','=':'₌','(':'₍',')':'₎',
    'a':'ₐ','e':'ₑ','h':'ₕ','i':'ᵢ','j':'ⱼ','k':'ₖ','l':'ₗ','m':'ₘ','n':'ₙ',
    'o':'ₒ','p':'ₚ','r':'ᵣ','s':'ₛ','t':'ₜ','u':'ᵤ','v':'ᵥ','x':'ₓ',
}

def to_unicode_script(raw_text, char_map):
    converted = []
    for symbol in raw_text:
        if symbol in char_map:
            converted.append(char_map[symbol])
        elif symbol.isspace() or symbol in ',.':
            converted.append(symbol)
        else:
            return f"({raw_text})"
    return ''.join(converted)

def convert_sup_sub(soup):
    for script_tag in soup.find_all(['sup', 'sub']):
        tag_content = script_tag.get_text()
        char_map = SUP_MAP if script_tag.name == 'sup' else SUB_MAP
        script_tag.replace_with(NavigableString(to_unicode_script(tag_content, char_map)))

LATEX_MACROS = {
    r'\wedge': '∧', r'\vee': '∨', r'\neg': '¬', r'\lnot': '¬',
    r'\rightarrow': '→', r'\leftarrow': '←', r'\Rightarrow': '⇒', r'\Leftrightarrow': '⇔',
    r'\equiv': '≡', r'\neq': '≠', r'\leq': '≤', r'\geq': '≥',
    r'\times': '×', r'\cdot': '·', r'\pm': '±', r'\infty': '∞',
    r'\forall': '∀', r'\exists': '∃', r'\in': '∈', r'\notin': '∉',
    r'\subset': '⊂', r'\cup': '∪', r'\cap': '∩', r'\emptyset': '∅',
    r'\left': '', r'\right': '', r'\,': ' ', r'\;': ' ', r'\!': '',
    r'\{': '{', r'\}': '}', r'\%': '%', r'\lor':'∨', r'\to':'→', r'\land':'∧'
}

SCRIPT_GROUP_PATTERN = re.compile(r'([\^_])\{([^{}]*)\}|([\^_])(\S)')

def replace_script_group(match):
    script_marker = match.group(1) or match.group(3)
    script_content = match.group(2) if match.group(1) else match.group(4)
    char_map = SUP_MAP if script_marker == '^' else SUB_MAP
    return to_unicode_script(script_content, char_map)

def clean_latex(raw_text):
    cleaned = raw_text.replace('\\(', '').replace('\\)', '')
    for macro, replacement in sorted(LATEX_MACROS.items(), key=lambda kv: -len(kv[0])):
        cleaned = cleaned.replace(macro, replacement)
    cleaned = SCRIPT_GROUP_PATTERN.sub(replace_script_group, cleaned)
    return cleaned

def extract_and_remove_tables(soup):
    all_tables = []
    for table_index, table_tag in enumerate(soup.find_all('table')):
        table_rows = []
        for row_tag in table_tag.find_all('tr'):
            row_cells = []
            for cell_tag in row_tag.find_all(['td', 'th']):
                convert_sup_sub(cell_tag)
                cell_text = re.sub(r' {2,}', ' ', cell_tag.get_text(separator='', strip=True))
                row_cells.append(cell_text)
            if row_cells:
                table_rows.append(row_cells)
        if table_rows:
            all_tables.append(table_rows)
            table_tag.replace_with(NavigableString(f"\n[[TABLE:{len(all_tables)-1}]]\n"))
        else:
            table_tag.decompose()
    return all_tables

BLOCK_TAGS = ['p', 'div', 'li', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']

def clean_task_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    found_files = []
    for img_tag in soup.find_all('img'):
        img_src = img_tag.get('src', '')
        if img_src and not img_src.startswith('data:image'):
            if not img_src.startswith('http'):
                img_src = "https://kompege.ru" + img_src
            found_files.append(img_src)
        img_tag.decompose()

    convert_sup_sub(soup)
    extracted_tables = extract_and_remove_tables(soup)

    for block_tag in soup.find_all(BLOCK_TAGS):
        block_tag.insert_after(NavigableString('\n'))

    raw_text = soup.get_text(separator='', strip=False)
    raw_text = clean_latex(raw_text)

    text_lines = []
    for line in raw_text.split('\n'):
        line = re.sub(r' {2,}', ' ', line.strip())
        if line:
            text_lines.append(line)
    final_text = '\n'.join(text_lines)

    return final_text, extracted_tables, found_files