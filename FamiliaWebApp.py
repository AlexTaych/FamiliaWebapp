import re
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from FileHandler import FileHandler
from DataBaseSearch import DataBaseSearch
from Patterns import name_pat_reg, full_name_reg, record_pattern, name_pat_error, full_name_error


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
    projects = FileHandler('None').get_projects()
    return render_template('initial.html', projects=projects)


# Страница "Задать настройки нового проекта"
@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        project_name = request.form.get('pr_name')
        familia_m = request.form.get('familia_m')
        familia_f = request.form.get('familia_f')
        locality = request.form.get("locality")

        # Создание папки проекта и внутренней структуры папок
        handler = FileHandler(project_name)
        handler.project_initiation()

        # Сохранение настроек в settings.json внутри папки проекта
        handler.save_settings(familia_m, familia_f, locality)

        # Сохранение текущего проекта в сессии
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
    rec_type = 'Births'
    current_project = session.get('current_project', 'Проект не выбран')
    handler = FileHandler(current_project)
    settings = handler.get_settings()
    rec_id = handler.get_id(rec_type)
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get("date").split('-')
        gender = request.form.get('gender')
        newborn = request.form.get("newborn")
        father = request.form.get("father")
        mother = request.form.get("mother")
        locality = request.form.get("locality")
        susceptor1 = request.form.get('susceptor1')
        susceptor2 = request.form.get('susceptor2')
        notes = request.form.get('notes')

        # Проверка на заполнение полей "father", "susceptor1/2"
        check_list1 = [newborn, mother]
        check_list2 = []
        if father.strip():
            check_list1.append(father)
        else:
            father = "- -"
        if susceptor1.strip():
            check_list2.append(susceptor1)
        else:
            susceptor1 = "- - -"
        if susceptor2.strip():
            check_list2.append(susceptor2)
        else:
            susceptor2 = "- - -"

        # Проверка на наличие ошибок
        errors = {}
        for name in check_list1:
            if not re.fullmatch(name_pat_reg(), name):
                errors[name] = name_pat_error(name)
        for susceptor in check_list2:
            if not re.fullmatch(full_name_reg(), susceptor):
                errors[susceptor] = full_name_error(susceptor)
        if errors:
            return render_template('birth.html', errors=errors, form_data=request.form)

        # Формирование словаря для последующей передачи в json файл
        rec_raw = {
            'date_list': date_list,
            'gender': gender,
            'newborn': newborn,
            'father': father,
            'mother': mother,
            'locality': locality,
            'susceptor1': susceptor1,
            'susceptor2': susceptor2,
            'notes': notes
        }
        record = record_pattern(rec_type, rec_raw, rec_id, settings)

        # Название файла и сообщение о записи
        file_name = f'{rec_id}_{record["newborn"]["name"]}_{record["newborn"]["patronym"]}'
        report = (f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о рождении '
                  f'{record["newborn"]["familia"]} {record["newborn"]["name"]} {record["newborn"]["patronym"]} '
                  f'от {record["date"]}; ID - {rec_id}')

        # Запись в файл
        handler.rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'birth.html',
        current_project=current_project,
        locality=settings["locality"]
    )


# Запись о бракосочетании
@app.route('/wedding', methods=['GET', 'POST'])
def wedding():
    rec_type = 'Weddings'
    current_project = session.get('current_project', 'Проект не выбран')
    handler = FileHandler(current_project)
    settings = handler.get_settings()
    rec_id = handler.get_id(rec_type)
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get("date").split('-')
        husband = request.form.get("husband")
        wife = request.form.get("wife")
        hus_locality = request.form.get("hus_locality")
        wif_locality = request.form.get("wif_locality")
        hus_guarantor1 = request.form.get("hus_guarantor1")
        hus_guarantor2 = request.form.get("hus_guarantor2")
        wif_guarantor1 = request.form.get("wif_guarantor1")
        wif_guarantor2 = request.form.get("wif_guarantor2")
        notes = request.form.get("notes")

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
            if not re.fullmatch(full_name_reg(), name):
                errors[name] = full_name_error(name)
        if errors:
            return render_template('wedding.html', errors=errors, form_data=request.form)

        # Формирование словаря для последующей передачи в json файл
        rec_raw = {
            'date_list': date_list,
            'husband': husband,
            'wife': wife,
            'hus_locality': hus_locality,
            'wif_locality': wif_locality,
            'hus_guarantor1': hus_guarantor1,
            'hus_guarantor2': hus_guarantor2,
            'wif_guarantor1': wif_guarantor1,
            'wif_guarantor2': wif_guarantor2,
            'notes': notes
        }
        record = record_pattern(rec_type, rec_raw, rec_id, settings)

        # Название файла и сообщение о записи
        file_name = f'{rec_id}_{record["husband"]["familia"]}_{record["wife"]["familia"]}'
        report = (
            f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о бракосочетании '
            f'{record["husband"]["familia"]} {record["husband"]["name"]} {record["husband"]["patronym"]} и '
            f'{record["wife"]["familia"]} {record["wife"]["name"]} {record["wife"]["patronym"]} '
            f'от {record["date"]}; ID - {rec_id}'
        )

        # Запись в файл
        handler.rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'wedding.html',
        current_project=current_project,
        locality=settings["locality"],
        familia_m=settings["familia_m"]
    )


# Запись о смерти
@app.route('/death', methods=['GET', 'POST'])
def death():
    rec_type = 'Deaths'
    current_project = session.get('current_project', 'Проект не выбран')
    handler = FileHandler(current_project)
    settings = handler.get_settings()
    rec_id = handler.get_id(rec_type)
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get("date").split("-")
        gender = request.form.get("gender")
        deceased = request.form.get("deceased")
        death_cause = request.form.get("death_cause")
        relative = request.form.get("relative")
        relation_degree = request.form.get("relation_degree")
        locality = request.form.get("locality")
        notes = request.form.get("notes")

        # Проверка на заполнение полей
        check_list = [deceased]
        if not relative.strip():
            relative = '- -'
            relation_degree = '-'
        else:
            check_list.append(relative)

        # Проверка на наличие ошибок
        errors = {}
        for name in check_list:
            if not re.fullmatch(name_pat_reg(), name):
                errors[name] = name_pat_error(name)
        if errors:
            return render_template('death.html', errors=errors, form_data=request.form)

        # Формирование словаря для последующей передачи в json файл
        rec_raw = {
            'date_list': date_list,
            'gender': gender,
            'deceased': deceased,
            'death_cause': death_cause,
            'relative': relative,
            'relation_degree': relation_degree,
            'locality': locality,
            'notes': notes
        }
        record = record_pattern(rec_type, rec_raw, rec_id, settings)

        # Название файла и сообщение о записи
        file_name = f'{rec_id}_{record["deceased"]["name"]}_{record["deceased"]["patronym"]}'
        report = (
            f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о смерти '
            f'{record["deceased"]["familia"]} {record["deceased"]["name"]} {record["deceased"]["patronym"]} '
            f'от {record["date"]}; ID - {rec_id}'
        )

        # Запись в файл
        handler.rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'death.html',
        current_project=current_project,
        locality=settings["locality"]
    )


# Запись о побочном событии
@app.route('/side_event', methods=['GET', 'POST'])
def side_event():
    rec_type = 'Side_events'
    current_project = session.get('current_project', 'Проект не выбран')
    handler = FileHandler(current_project)
    settings = handler.get_settings()
    rec_id = handler.get_id(rec_type)
    if request.method == 'POST':
        # Получаем данные из формы
        date_list = request.form.get("date").split("-")
        gender = request.form.get("gender")
        participant = request.form.get("participant")
        role = request.form.get("role")
        locality = request.form.get("locality")
        notes = request.form.get("notes")

        # Проверка на наличие ошибок
        errors = {}
        if not re.fullmatch(name_pat_reg(), participant):
            errors[participant] = name_pat_error(participant)
        if errors:
            return render_template('side_event.html', errors=errors, form_data=request.form)

        # Формирование словаря для последующей передачи в json файл
        rec_raw = {
            'date_list': date_list,
            'gender': gender,
            'participant': participant,
            'role': role,
            'locality': locality,
            'notes': notes
        }
        record = record_pattern(rec_type, rec_raw, rec_id, settings)

        # Название файла и сообщение о записи
        file_name = f'{rec_id}_{record["participant"]["name"]}_{record["participant"]["patronym"]}'
        report = (
            f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} была добавлена запись о событии: '
            f'{record["participant"]["familia"]} {record["participant"]["name"]} {record["participant"]["patronym"]} '
            f'записан как {role} от {record["date"]}; ID - {rec_id}'
        )

        # Запись в файл
        handler.rec_dump(rec_type, file_name, record, report)

        return redirect(url_for('rec_select'))
    return render_template(
        'side_event.html',
        current_project=current_project,
        locality=settings["locality"]
    )


# Страница "Настройки"
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    current_project = session.get('current_project')
    handler = FileHandler(current_project)
    if request.method == 'POST':
        familia_m = request.form.get("familia_m")
        familia_f = request.form.get("familia_f")
        locality = request.form.get("locality")
        handler.save_settings(familia_m, familia_f, locality)
        return redirect(url_for("rec_select"))

    # Получаем текущие настройки
    settings = handler.get_settings()
    return render_template(
        'settings.html',
        familia_m=settings["familia_m"],
        familia_f=settings["familia_f"],
        locality=settings["locality"]
    )


# Поиск
@app.route('/search_initial')
def search_initial():
    # При первой загрузке отправляем пустые списки
    return render_template(
        'search.html',
        lists={'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
    )


# Обработка поискового запроса
@app.route('/search_query', methods=['POST'])
def search_query():
    current_project = session.get('current_project', 'Проект не выбран')
    handler = FileHandler(current_project)
    settings = handler.get_settings()
    query = request.form.get('query', '')
    rec_types = request.form.get("rectype", "all")
    rec_field = request.form.get("field", "name")
#    search_in_previous = request.form.get('search_in_previous') == 'on'

    # Обработка пропусков("...") в поисковых запросах
    if rec_field == 'name':
        query = f'(?<![а-яА-ЯёЁ]){query}(?![а-яА-ЯёЁ])'
    if '...' in query and query != '...':
        query = f'{query.replace("...", "[а-яА-ЯёЁ.]+")}'
    if query == '...':
        query = '\\.\\.\\.'

    # При поиске по 'Side_events' необходимо производить поиск по записям других типов
    if rec_types == 'all':
        rec_types = ['Births', 'Weddings', 'Deaths', 'Side_events']
    elif rec_types == 'Side_events':
        rec_types = ['Births', 'Weddings', 'Side_events']
    else:
        rec_types = [rec_types]

    # Формирование словаря из базы данных
    rec_dict = handler.record_request(rec_types)

    # Инициация поиска
    search = DataBaseSearch(rec_dict, query, settings)

    # Осуществление поиска по заданному полю
    if rec_field == 'results':
        previous_results = handler.get_previous_results()
        results = search.result_search(previous_results)
    else:
        if rec_field == 'name':
            results = search.name_search()
        elif rec_field == 'id':
            results = search.id_search()
        elif rec_field == 'date':
            results = search.date_search()
        elif rec_field == 'gender':
            results = search.gender_search()
        elif rec_field == 'locality':
            results = search.locality_search()
        elif rec_field == 'text':
            results = search.text_search()
        else:
            results = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}

    # Корявая очистка результатов поиска по побочным записям от рождений и свадеб
    if 'Side_events' not in rec_types:
        results['Side_events'] = []
    if rec_types == ['Births', 'Weddings', 'Side_events']:
        results['Births'] = []
        results['Weddings'] = []

    # Сохранение результатов для возможного поиска по ним
    handler.save_previous_results(results)

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
