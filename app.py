from flask import  Flask, render_template, request, redirect, url_for, session
import json
from pathlib import Path
import re
import datetime


# Регулярные выражения
name_pat_reg = (r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.])) '
                r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.]))')
full_name_reg = (r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.])) '
                 r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.])) '
                 r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                 r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.]))')

# Путь к основной папке программы и к базе данных проектов
folder_location = Path(__file__).resolve().parent
projects_dir = folder_location / "Projects"

# Путь к файлу настроек проекта
def get_settings_path():
    current_project = session.get('current_project')
    if current_project:
        return projects_dir / current_project / "settings.json"
    return None

# Функция для чтения настроек из settings.json
def get_settings():
    settings_path = get_settings_path()
    if settings_path and settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"familia_m": "", "familia_f": "", "locality": ""}

# Функция для сохранения настроек в settings.json
def save_settings(familia_m, familia_f, locality):
    settings_path = get_settings_path()
    if settings_path:
        settings = {"familia_m": familia_m, "familia_f": familia_f, "locality": locality}
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

# Функция для получения списка проектов
def get_projects():
    if projects_dir.exists():
        return [p.name for p in projects_dir.iterdir() if p.is_dir()]
    return []

# Функция для получения актуального ID записи
def get_id(rec_type):
    current_project = session.get('current_project')
    if current_project:
        rec_type_path = projects_dir / current_project / rec_type
        ids = []
        for file in  rec_type_path.iterdir():
            with open(rec_type_path / file, 'r', encoding="UTF-8") as f:
                text = json.load(f)
                if 'id' in text.keys():
                    ids.append(text['id'])
        if len(ids) >= 1:
            return max(ids) + 1
        else:
            return 1


def rec_dump(rec_type, file_name, record, report):
    current_project = session.get('current_project')
    if current_project:
        rec_type_path = projects_dir / current_project / rec_type
        with open(rec_type_path.joinpath(f"{file_name}.json"), 'w', encoding="UTF-8") as file_out:
            json.dump(record, file_out, ensure_ascii=False, indent=2)
        with open(projects_dir.joinpath(current_project, "reports.txt"), "r", encoding="UTF-8") as orig_file:
            temp_text = orig_file.read()
        with open(projects_dir.joinpath(current_project, "reports.txt"), "w", encoding="UTF-8") as mod_file:
            mod_file.write(f'{temp_text}{report}\n')


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Начальная страница
@app.route('/', methods=['GET', 'POST'])
def initial():
    if request.method == 'POST':
        selected_project = request.form.get('project_select')
        if selected_project:
            session['current_project'] = selected_project
            return redirect(url_for('rec_select'))
    projects = get_projects()
    return render_template('initial.html', projects=projects)

# Страница "Задать настройки нового проекта"
@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        pr_name = request.form.get('pr_name')
        familia_m = request.form.get('familia_m')
        familia_f = request.form.get('familia_f')
        locality = request.form.get('locality')

        # Создаем папку проекта
        project_name = pr_name
        project_path = projects_dir / project_name
        dir_list = ['Births', 'Weddings', 'Deaths', 'Side_events']
        for d in dir_list:
            project_path.joinpath(d).mkdir(parents=True, exist_ok=True)
        with open(project_path.joinpath('reports.txt'), "w", encoding="utf-8") as f:
            pass

        # Сохраняем настройки в settings.json внутри папки проекта
        settings_path = project_path / 'settings.json'
        settings = {
            'familia_m': familia_m,
            "familia_f": familia_f,
            'locality': locality
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

        # Сохраняем текущий проект в сессии
        session['current_project'] = project_name

        return redirect(url_for('rec_select'))
    return render_template('new_project.html')

# Страница выбора типа записи
@app.route('/rec_select')
def rec_select():
    current_project = session.get('current_project', 'Проект не выбран')
    return render_template('rec_select.html', current_project=current_project)

# Запись о рождении
@app.route('/birth', methods=['GET', 'POST'])
def birth():
    current_project = session.get('current_project', 'Проект не выбран')
    settings = get_settings()
    rec_type = 'Births'
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get('date').split('-')
        gender = request.form.get('gender')
        newborn = request.form.get('newborn')
        father = request.form.get('father')
        mother = request.form.get('mother')
        locality = request.form.get('locality')
        susceptor1 = request.form.get('susceptor1')
        susceptor2 = request.form.get('susceptor2')
        notes = request.form.get('notes')

        # Проверка на заполнение полей "father", "susceptor1/2"
        check_list1 = [newborn, mother]
        check_list2 = []
        if not father.strip():
            father = '- -'
        else:
            check_list1.append(father)
        if not susceptor1.strip():
            susceptor1 = '- - -'
        else:
            check_list2.append(susceptor1)
        if not susceptor2.strip():
            susceptor2 = '- - -'
        else:
            check_list2.append(susceptor2)

        # Проверка на наличие ошибок
        errors = {}
        for name in check_list1:
            if not re.fullmatch(name_pat_reg, name):
                errors[name] = (f'Неправильно заполненные данные: "{name}".\n'
                                f'Имя и отчество должны соответствовать шаблону: "Иван Иванович"')
        for susceptor in check_list2:
            if not re.fullmatch(full_name_reg, susceptor):
                errors[susceptor] = (
                    f'Неправильно заполненные данные: "{susceptor}".\n'
                    f'Фамилия, имя и отчество восприемника должны соответствовать шаблону: "Иванов Иван Иванович"'
                )
        if errors:
            return render_template('birth.html', errors=errors, form_data=request.form)

        # Формирование дополнительных переменных для json файла
        rec_id = get_id(rec_type)
        date = f'{date_list[2]}.{date_list[1]}.{date_list[0]}'
        familia_m = settings['familia_m']
        familia_f = settings['familia_f']
        newborn_name = newborn.split()[0]
        newborn_patronym = newborn.split()[1]
        if gender == 'м':
            newborn_familia = familia_m
        else:
            newborn_familia = familia_f
        if '-' in father:
            father_familia = '-'
        else:
            father_familia = familia_m
        father_name = father.split()[0]
        father_patronym = father.split()[1]
        mother_name = mother.split()[0]
        mother_patronym = mother.split()[1]
        susceptor_prim_familia = susceptor1.split()[0]
        susceptor_prim_name = susceptor1.split()[1]
        susceptor_prim_patronym = susceptor1.split()[2]
        susceptor_sec_familia = susceptor2.split()[0]
        susceptor_sec_name = susceptor2.split()[1]
        susceptor_sec_patronym = susceptor2.split()[2]
        file_name = f'{rec_id}_{newborn_name}_{newborn_patronym}'
        report = (f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о рождении '
                  f'{newborn_familia} {newborn_name} {newborn_patronym} от {date}; ID - {rec_id}')

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            'date': date,
            'newborn': {'familia': newborn_familia, 'name': newborn_name, 'patronym': newborn_patronym},
            'father': {'familia': father_familia, 'name': father_name, 'patronym': father_patronym},
            'mother': {'familia': familia_f, 'name': mother_name, 'patronym': mother_patronym},
            'locality': locality,
            'susceptors': {
                '1st': {
                    'familia': susceptor_prim_familia,
                    'name': susceptor_prim_name,
                    'patronym': susceptor_prim_patronym
                },
                '2nd': {
                    'familia': susceptor_sec_familia,
                    'name': susceptor_sec_name,
                    'patronym': susceptor_sec_patronym
                }
            },
            'notes': notes
        }

        # Запись в файл
        rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'birth.html',
        current_project=current_project,
        locality=settings['locality']
    )

# Запись о бракосочетании
@app.route('/wedding', methods=['GET', 'POST'])
def wedding():
    current_project = session.get('current_project', 'Проект не выбран')
    settings = get_settings()
    rec_type = "Weddings"
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get('date').split('-')
        husband = request.form.get('husband')
        wife = request.form.get('wife')
        hus_locality = request.form.get('hus_locality')
        wif_locality = request.form.get('wif_locality')
        hus_guarantor1 = request.form.get('hus_guarantor1')
        hus_guarantor2 = request.form.get('hus_guarantor2')
        wif_guarantor1 = request.form.get('wif_guarantor1')
        wif_guarantor2 = request.form.get('wif_guarantor2')
        notes = request.form.get('notes')

        # Проверка на заполнение полей
        check_list = [husband, wife]
        if not hus_guarantor1.strip():
            hus_guarantor1 = '- - -'
        else:
            check_list.append(hus_guarantor1)
        if not hus_guarantor2.strip():
            hus_guarantor2 = '- - -'
        else:
            check_list.append(hus_guarantor2)
        if not wif_guarantor1.strip():
            wif_guarantor1 = '- - -'
        else:
            check_list.append(wif_guarantor1)
        if not wif_guarantor2.strip():
            wif_guarantor2 = '- - -'
        else:
            check_list.append(wif_guarantor2)

        # Проверка на наличие ошибок
        errors = {}
        for name in check_list:
            if not re.fullmatch(full_name_reg, name):
                errors[name] = (
                    f'Неправильно заполненные данные: "{name}".\n'
                    f'Фамилия, имя и отчество должны соответствовать шаблону: "Иванов Иван Иванович"'
                )
        if errors:
            return render_template('wedding.html', errors=errors, form_data=request.form)

        # Формирование дополнительных переменных для json файла
        rec_id = get_id(rec_type)
        date = f'{date_list[2]}.{date_list[1]}.{date_list[0]}'
        husband_familia = husband.split()[0]
        husband_name = husband.split()[1]
        husband_patronym = husband.split()[2]
        wife_familia = wife.split()[0]
        wife_name = wife.split()[1]
        wife_patronym = wife.split()[2]
        hus_guarantor_prim_familia = hus_guarantor1.split()[0]
        hus_guarantor_prim_name = hus_guarantor1.split()[1]
        hus_guarantor_prim_patronym = hus_guarantor1.split()[2]
        hus_guarantor_sec_familia = hus_guarantor2.split()[0]
        hus_guarantor_sec_name = hus_guarantor2.split()[1]
        hus_guarantor_sec_patronym = hus_guarantor2.split()[2]
        wif_guarantor_prim_familia = wif_guarantor1.split()[0]
        wif_guarantor_prim_name = wif_guarantor1.split()[1]
        wif_guarantor_prim_patronym = wif_guarantor1.split()[2]
        wif_guarantor_sec_familia = wif_guarantor2.split()[0]
        wif_guarantor_sec_name = wif_guarantor2.split()[1]
        wif_guarantor_sec_patronym = wif_guarantor2.split()[2]
        file_name = f'{rec_id}_{husband_familia}_{wife_familia}'
        report = (
            f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о бракосочетании '
            f'{husband_familia} {husband_name} {husband_patronym} и {wife_familia} {wife_name} '
            f'{wife_patronym} от {date}; ID - {rec_id}'
        )

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            'date': date,
            'husband': {
                'familia': husband_familia,
                'name': husband_name,
                'patronym': husband_patronym,
                'locality': hus_locality
            },
            'wife': {
                'familia': wife_familia,
                'name': wife_name,
                'patronym': wife_patronym,
                'locality': wif_locality
            },
            'husband_guarantors': {
                '1st': {
                    'familia': hus_guarantor_prim_familia,
                    'name': hus_guarantor_prim_name,
                    'patronym': hus_guarantor_prim_patronym
                },
                '2nd': {
                    'familia': hus_guarantor_sec_familia,
                    'name': hus_guarantor_sec_name,
                    'patronym': hus_guarantor_sec_patronym
                }
            },
            'wife_guarantors': {
                '1st': {
                    'familia': wif_guarantor_prim_familia,
                    'name': wif_guarantor_prim_name,
                    'patronym': wif_guarantor_prim_patronym
                },
                '2nd': {
                    'familia': wif_guarantor_sec_familia,
                    'name': wif_guarantor_sec_name,
                    'patronym': wif_guarantor_sec_patronym
                }
            },
            'notes': notes
        }

        # Запись в файл
        rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'wedding.html',
        current_project=current_project,
        locality=settings['locality'],
        familia_m=settings['familia_m']
    )

# Страница 3
@app.route('/death', methods=['GET', 'POST'])
def death():
    current_project = session.get('current_project', 'Проект не выбран')
    settings = get_settings()
    rec_type = "Deaths"
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get('date').split('-')
        gender = request.form.get('gender')
        deceased = request.form.get('deceased')
        death_cause = request.form.get('death_cause')
        relative = request.form.get('relative')
        relation_degree = request.form.get('relation_degree')
        locality = request.form.get('locality')
        notes = request.form.get('notes')

        # Проверка на заполнение полей
        check_list = [deceased]
        if not relative.strip():
            relative = '- - -'
            relation_degree = '-'
        else:
            check_list.append(relative)

        # Проверка на наличие ошибок
        errors = {}
        for name in check_list:
            if not re.fullmatch(name_pat_reg, name):
                errors[name] = (f'Неправильно заполненные данные: "{name}".\n'
                                f'Имя и отчество должны соответствовать шаблону: "Иван Иванович"')
        if errors:
            return render_template('death.html', errors=errors, form_data=request.form)

        # Формирование дополнительных переменных для json файла
        rec_id = get_id(rec_type)
        date = f'{date_list[2]}.{date_list[1]}.{date_list[0]}'
        familia_m = settings['familia_m']
        familia_f = settings['familia_f']
        if gender == 'м':
            deceased_familia = familia_m
        else:
            deceased_familia = familia_f
        deceased_name = deceased.split()[0]
        deceased_patronym = deceased.split()[1]
        if '-' in relative:
            relative_familia = '-'
        else:
            relative_familia = familia_m
        relative_name = relative.split()[0]
        relative_patronym = relative.split()[1]
        if '-' not in relative and not relation_degree:
            relation_degree = 'отец'
        file_name = f'{rec_id}_{deceased_name}_{deceased_patronym}'
        report = (
            f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о смерти '
            f'{deceased_familia} {deceased_name} {deceased_patronym} от {date}; ID - {rec_id}'
        )

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            'date': date,
            'deceased': {'familia': deceased_familia, 'name': deceased_name, 'patronym': deceased_patronym},
            'death_cause': death_cause,
            'relative': {
                'familia': relative_familia,
                'name': relative_name,
                'patronym': relative_patronym,
                'relation_degree': relation_degree
            },
            'locality': locality,
            'notes': notes
        }

        # Запись в файл
        rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'death.html',
        current_project=current_project,
        locality=settings['locality']
    )

# Страница 3
@app.route('/side_event', methods=['GET', 'POST'])
def side_event():
    current_project = session.get('current_project', 'Проект не выбран')
    settings = get_settings()
    rec_type = "Side_events"
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get('date').split('-')
        gender = request.form.get('gender')
        participant = request.form.get('participant')
        role = request.form.get('role')
        locality = request.form.get('locality')
        notes = request.form.get('notes')

        # Проверка на наличие ошибок
        errors = {}
        if not re.fullmatch(name_pat_reg, participant):
            errors[participant] = (f'Неправильно заполненные данные: "{participant}".\n'
                            f'Имя и отчество должны соответствовать шаблону: "Иван Иванович"')
        if errors:
            return render_template('side_event.html', errors=errors, form_data=request.form)

        # Формирование дополнительных переменных для json файла
        rec_id = get_id(rec_type)
        date = f'{date_list[2]}.{date_list[1]}.{date_list[0]}'
        if gender == 'м':
            participant_familia = settings['familia_m']
        else:
            participant_familia = settings['familia_f']
        participant_name = participant.split()[0]
        participant_patronym = participant.split()[1]
        file_name = f'{rec_id}_{participant_name}_{participant_patronym}'
        report = (
            f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о событии: '
            f'{participant_familia} {participant_name} {participant_patronym} '
            f'записан как {role} от {date}; ID - {rec_id}'
        )

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            'date': date,
            'participant': {
                'familia': participant_familia,
                'name': participant_name,
                'patronym': participant_patronym
            },
            'role': role,
            'locality': locality,
            'notes': notes
        }

        # Запись в файл
        rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'side_event.html',
        current_project=current_project,
        locality=settings['locality']
    )

# Страница "Настройки"
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        familia_m = request.form.get('familia_m')
        familia_f = request.form.get('familia_f')
        locality = request.form.get('locality')
        save_settings(familia_m, familia_f, locality)
        return redirect(url_for('rec_select'))

    # Получаем текущие настройки
    settings = get_settings()
    return render_template(
        'settings.html',
        familia_m=settings['familia_m'],
        familia_f=settings['familia_f'],
        locality=settings['locality']
    )

if __name__ == '__main__':
    app.run(debug=True)