from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import re



app = Flask(__name__)

#temp variables
folder_location = Path(__file__).resolve().parent
projects_dir = folder_location / "Projects"

def get_settings():
    settings_path = projects_dir.joinpath('Taichenachev', "settings.json")
    if settings_path and settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"familia_m": "", "familia_f": "", "locality": ""}


def record_request(rec_types, project_path):
    rec_dict = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
    for rec_type in rec_types:
        rec_list = []
        file_list = [r for r in project_path.joinpath(rec_type).iterdir()]
        for file_name in file_list:
            with open(project_path.joinpath(rec_type, file_name), 'r', encoding="UTF-8") as file:
                text = json.load(file)
                rec_list.append(text)
        rec_dict[rec_type] = rec_list
    print(f'при входном списке словарей: {rec_types}')
    for k, v in rec_dict.items():
        print(f'для словаря {k} выбрано {len(v)} значений')
    return rec_dict

# Функция поиска по элементам имени, принимает на ввод: словарь базы данных и поисковый запрос
def name_search(rec_dict, query, response_dict):
    for k, v in rec_dict.items():
        if k == 'Births' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(
                        query,
                        f'{rec['newborn']['familia']} {rec['newborn']['name']} {rec['newborn']['patronym']}'
                ):
                    if rec['newborn']['familia'] == get_settings()['familia_f']:
                        gender_text = 'родилась'
                    else:
                        gender_text = 'родился'
                    temp_dict = {
                        'main_char': f'{rec['newborn']['familia']} {rec['newborn']['name']} '
                                     f'{rec['newborn']['patronym']}',
                        'date': f'<u>{gender_text}</u> {rec['date']}',
                        'secondary_char': f'<u>Отец</u>: <b>{rec['father']['name']} {rec['father']['patronym']}</b><br>'
                                          f'<u>Мать</u>: <b>{rec['mother']['name']} {rec['mother']['patronym']}</b><br>'
                                          f'<u>Восприемники</u>: {' '.join(rec['susceptors']['1st'].values())} и '
                                          f'{' '.join(rec['susceptors']['2nd'].values())}',
                        'locality': f'<u>Место рождения</u>: {rec['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
                if re.search(
                        query,
                        f'{rec['father']['familia']} {rec['father']['name']} {rec['father']['patronym']}'
                ):
                    temp_dict = {
                        'main_char': f'{rec['father']['familia']} {rec['father']['name']} {rec['father']['patronym']}',
                        'date': f'{rec['date']} записан как <u>отец</u>',
                        'secondary_char': f'<u>Ребенок</u>: <b>{rec['newborn']['name']} '
                                          f'{rec['newborn']['patronym']}</b><br>'
                                          f'<u>Жена</u>: <b>{rec['mother']['name']} {rec['mother']['patronym']}</b><br>'
                                          f'<u>Восприемники</u>: {' '.join(rec['susceptors']['1st'].values())} и '
                                          f'{' '.join(rec['susceptors']['2nd'].values())}',
                        'locality': f'<u>Место проживания</u>: {rec['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
                if re.search(
                        query,
                        f'{rec['mother']['familia']} {rec['mother']['name']} {rec['mother']['patronym']}'
                ):
                    temp_dict = {
                        'main_char': f'{rec['mother']['familia']} {rec['mother']['name']} {rec['mother']['patronym']}',
                        'date': f'{rec['date']} записана как <u>мать</u>',
                        'secondary_char': f'<u>Ребенок</u>: <b>{rec['newborn']['name']} '
                                          f'{rec['newborn']['patronym']}</b><br>'
                                          f'<u>Муж</u>: <b>{rec['father']['name']} {rec['father']['patronym']}</b><br>'
                                          f'<u>Восприемники</u>: {' '.join(rec['susceptors']['1st'].values())} и '
                                          f'{' '.join(rec['susceptors']['2nd'].values())}',
                        'locality': f'<u>Место проживания</u>: {rec['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
            response_dict[k] = response_list
        if k == 'Weddings' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(
                        query,
                        f'{rec['husband']['familia']} {rec['husband']['name']} {rec['husband']['patronym']}'
                ):
                    temp_dict = {
                        'main_char': f'{rec['husband']['familia']} {rec['husband']['name']} '
                                     f'{rec['husband']['patronym']}',
                        'date': f'{rec['date']} записан как <u>жених</u>',
                        'secondary_char': f'<u>Невеста</u>: <b>{rec['wife']['familia']} {rec['wife']['name']} '
                                          f'{rec['wife']['patronym']}</b>; '
                                          f'родом из {rec['wife']['locality']}<br>'
                                          f'<u>Поручители жениха</u>: {' '.join(rec['husband_guarantors']['1st'].values())} и '
                                          f'{' '.join(rec['husband_guarantors']['2nd'].values())}<br>'
                                          f'<u>Поручители невесты</u>: {' '.join(rec['wife_guarantors']['1st'].values())} и '
                                          f'{' '.join(rec['wife_guarantors']['2nd'].values())}',
                        'locality': f'<u>Место проживания</u>: {rec['husband']['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
                if re.search(
                        query,
                        f'{rec['wife']['familia']} {rec['wife']['name']} {rec['wife']['patronym']}'
                ):
                    temp_dict = {
                        'main_char': f'{rec['wife']['familia']} {rec['wife']['name']} '
                                     f'{rec['wife']['patronym']}',
                        'date': f'{rec['date']} записана как <u>невеста</u>',
                        'secondary_char': f'<u>Муж</u>: <b>{rec['husband']['familia']} {rec['husband']['name']} '
                                          f'{rec['husband']['patronym']}</b>; '
                                          f'родом из {rec['husband']['locality']}<br>'
                                          f'<u>Поручители жениха</u>: {' '.join(rec['husband_guarantors']['1st'].values())} и '
                                          f'{' '.join(rec['husband_guarantors']['2nd'].values())}<br>'
                                          f'<u>Поручители невесты</u>: {' '.join(rec['wife_guarantors']['1st'].values())} и '
                                          f'{' '.join(rec['wife_guarantors']['2nd'].values())}',
                        'locality': f'<u>Место проживания</u>: {rec['wife']['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
            response_dict[k] = response_list
        if k == 'Deaths' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(
                        query,
                        f'{rec['deceased']['familia']} {rec['deceased']['name']} {rec['deceased']['patronym']}'
                ):
                    if rec['deceased']['familia'] == get_settings()['familia_f']:
                        gender_text = f'{rec['date']} <u>умерла</u> от: {rec['death_cause']}'
                    else:
                        gender_text = f'{rec['date']} <u>умер</u> от: {rec['death_cause']}'
                    if rec['relative']['patronym'] == '-':
                        relative_text = ''
                    else:
                        relative_text = (f'<u>{rec['relative']['relation_degree']}</u>: <b>{rec['relative']['name']} '
                                         f'{rec['relative']['patronym']}</b>')
                    temp_dict = {
                        'main_char': f'{rec['deceased']['familia']} {rec['deceased']['name']} '
                                     f'{rec['deceased']['patronym']}',
                        'date': gender_text,
                        'secondary_char': relative_text,
                        'locality': f'<u>Место смерти</u>: {rec['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
                if re.search(
                        query,
                        f'{rec['relative']['familia']} {rec['relative']['name']} {rec['relative']['patronym']}'
                ):
                    if rec['relative']['relation_degree'] == 'отец':
                        rel_text = (f'<u>отец</u> умершего ребенка; причина смерти: {rec['death_cause']};<br>'
                                    f'<u>дата смерти</u>: {rec['date']}')
                        deceased = '<u>Ребенок</u>'
                    elif rec['relative']['relation_degree'] == 'муж':
                        rel_text = (f'<u>муж</u> умершей; причина смерти: {rec['death_cause']};<br>'
                                    f'<u>дата смерти</u>: {rec['date']}')
                        deceased = '<u>Жена</u>'
                    else:
                        rel_text = (f'<u>родственник</u> умершего; причина смерти: {rec['death_cause']};<br>'
                                    f'<u>дата смерти</u>: {rec['date']}')
                        deceased = '<u>Родственник</u>'
                    temp_dict = {
                        'main_char': f'{rec['relative']['familia']} {rec['relative']['name']} '
                                     f'{rec['relative']['patronym']}',
                        'date': rel_text,
                        'secondary_char': f'{deceased}: <b>{rec['deceased']['name']} '
                                          f'{rec['deceased']['patronym']}</b>',
                        'locality': f'<u>Место смерти</u>: {rec['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
            response_dict[k] = response_list
        if k == 'Side_events' and len(rec_dict[k]) > 0:
            response_list = response_dict['Side_events']
            for rec in v:
                if re.search(
                        query,
                        f'{rec['participant']['familia']} {rec['participant']['name']} '
                        f'{rec['participant']['patronym']}'
                ):
                    if rec['participant']['patronym'][-1] == 'а':
                        gender_text = 'Записана как'
                    else:
                        gender_text = 'Записан как'
                    temp_dict = {
                        'main_char': f'{rec['participant']['familia']} {rec['participant']['name']} '
                                     f'{rec['participant']['patronym']}',
                        'date': f'Дата события: {rec['date']}',
                        'secondary_char': f'<u>{gender_text}</u>: {rec['role']}',
                        'locality': f'<u>Место события</u>: {rec['locality']}',
                        'ID': rec['id'],
                        'notes': rec['notes']
                    }
                    response_list.append(temp_dict)
            for rec in rec_dict['Births']:
                for n in ['1st', '2nd']:
                    if re.search(
                            query,
                            f'{rec['susceptors'][n]['familia']} {rec['susceptors'][n]['name']} '
                            f'{rec['susceptors'][n]['patronym']}'
                    ):
                        if rec['susceptors'][n]['patronym'][-1] == 'а':
                            gender_text = 'Записана как <u>восприемница</u>'
                        else:
                            gender_text = 'Записан как <u>восприемник</u>'
                        temp_dict = {
                            'main_char': f'{rec['susceptors'][n]['familia']} {rec['susceptors'][n]['name']} '
                                         f'{rec['susceptors'][n]['patronym']}',
                            'date': f'Дата события: {rec['date']}',
                            'secondary_char': f'{gender_text} при рождении: <b>{rec['newborn']['familia']} '
                                              f'{rec['newborn']['name']} {rec['newborn']['patronym']}</b><br>'
                                              f'<u>Отец</u>: <b>{rec['father']['name']} '
                                              f'{rec['father']['patronym']}</b><br>'
                                              f'<u>Мать</u>: <b>{rec['mother']['name']} '
                                              f'{rec['mother']['patronym']}</b><br>',
                            'locality': f'<u>Место события</u>: {rec['locality']}',
                            'ID': rec['id'],
                            'notes': rec['notes']
                        }
                        response_list.append(temp_dict)
            for rec in rec_dict['Weddings']:
                for n in ['1st', '2nd']:
                    if re.search(
                            query,
                            f'{rec['husband_guarantors'][n]['familia']} {rec['husband_guarantors'][n]['name']} '
                            f'{rec['husband_guarantors'][n]['patronym']}'
                    ):
                        temp_dict = {
                            'main_char': f'{rec['husband_guarantors'][n]['familia']} '
                                         f'{rec['husband_guarantors'][n]['name']} '
                                         f'{rec['husband_guarantors'][n]['patronym']}',
                            'date': f'Дата события: {rec['date']}',
                            'secondary_char': f'Записан как <u>поручитель жениха</u> на свадьбе:<br>'
                                              f'<u>Жених</u>: <b>{rec['husband']['familia']} {rec['husband']['name']} '
                                              f'{rec['husband']['patronym']}</b><br>'
                                              f'<u>Невеста</u>: <b>{rec['wife']['familia']} {rec['wife']['name']} '
                                              f'{rec['wife']['patronym']}</b><br>',
                            'locality': f'<u>Место события</u>: {rec['husband']['locality']}',
                            'ID': rec['id'],
                            'notes': rec['notes']
                        }
                        response_list.append(temp_dict)
                    if re.search(
                            query,
                            f'{rec['wife_guarantors'][n]['familia']} {rec['wife_guarantors'][n]['name']} '
                            f'{rec['wife_guarantors'][n]['patronym']}'
                    ):
                        temp_dict = {
                            'main_char': f'{rec['wife_guarantors'][n]['familia']} '
                                         f'{rec['wife_guarantors'][n]['name']} '
                                         f'{rec['wife_guarantors'][n]['patronym']}',
                            'date': f'Дата события: {rec['date']}',
                            'secondary_char': f'Записан как <u>поручитель невесты</u> на свадьбе:<br>'
                                              f'<u>Жених</u>: <b>{rec['husband']['familia']} {rec['husband']['name']} '
                                              f'{rec['husband']['patronym']}</b><br>'
                                              f'<u>Невеста</u>: <b>{rec['wife']['familia']} {rec['wife']['name']} '
                                              f'{rec['wife']['patronym']}</b><br>',
                            'locality': f'<u>Место события</u>: {rec['husband']['locality']}',
                            'ID': rec['id'],
                            'notes': rec['notes']
                        }
                        response_list.append(temp_dict)
            response_dict[k] = response_list
    print(f'По запросу {query} было отобрано:')
    for k, v in response_dict.items():
        print(f'в словаре {k} - {len(v)} записей')
    return  response_dict

# Функция формирования записей для поисковых запросов к неименным элементам записей
def get_rec_pattern(rec_type, rec):
    if rec_type == 'Births':
        if rec['newborn']['familia'] == get_settings()['familia_f']:
            gender_text = 'родилась'
        else:
            gender_text = 'родился'
        temp_dict = {
            'main_char': f'{rec['newborn']['familia']} {rec['newborn']['name']} '
                         f'{rec['newborn']['patronym']}',
            'date': f'<u>{gender_text}</u> {rec['date']}',
            'secondary_char': f'<u>Отец</u>: <b>{rec['father']['name']} {rec['father']['patronym']}</b><br>'
                              f'<u>Мать</u>: <b>{rec['mother']['name']} {rec['mother']['patronym']}</b><br>'
                              f'<u>Восприемники</u>: {' '.join(rec['susceptors']['1st'].values())} и '
                              f'{' '.join(rec['susceptors']['2nd'].values())}',
            'locality': f'<u>Место рождения</u>: {rec['locality']}',
            'ID': rec['id'],
            'notes': rec['notes']
        }
        return temp_dict
    if rec_type == 'Weddings':
        temp_dict = {
            'main_char': f'<u>Жених</u>: <b>{rec['husband']['familia']} {rec['husband']['name']} '
                         f'{rec['husband']['patronym']}</b><br>'
                         f'<u>Невеста</u>: <b>{rec['wife']['familia']} {rec['wife']['name']} '
                         f'{rec['wife']['patronym']}</b>',
            'date': f'<u>Дата свадьбы</u>: {rec['date']}',
            'secondary_char': f'<u>Поручители жениха</u>: {' '.join(rec['husband_guarantors']['1st'].values())} и '
                              f'{' '.join(rec['husband_guarantors']['2nd'].values())}<br>'
                              f'<u>Поручители невесты</u>: {' '.join(rec['wife_guarantors']['1st'].values())} и '
                              f'{' '.join(rec['wife_guarantors']['2nd'].values())}',
            'locality': f'<u>Место жительства жениха</u>: {rec['husband']['locality']}<br>'
                        f'<u>Место жительства невесты</u>: {rec['wife']['locality']}',
            'ID': rec['id'],
            'notes': rec['notes']
        }
        return temp_dict
    if rec_type == 'Deaths':
        if rec['deceased']['familia'] == get_settings()['familia_f']:
            gender_text = f'{rec['date']} <u>умерла</u> от: {rec['death_cause']}'
        else:
            gender_text = f'{rec['date']} <u>умер</u> от: {rec['death_cause']}'
        if rec['relative']['patronym'] == '-':
            relative_text = ''
        else:
            relative_text = (f'<u>{rec['relative']['relation_degree']}</u>: <b>{rec['relative']['name']} '
                             f'{rec['relative']['patronym']}</b>')
        temp_dict = {
            'main_char': f'{rec['deceased']['familia']} {rec['deceased']['name']} '
                         f'{rec['deceased']['patronym']}',
            'date': gender_text,
            'secondary_char': relative_text,
            'locality': f'<u>Место смерти</u>: {rec['locality']}',
            'ID': rec['id'],
            'notes': rec['notes']
        }
        return temp_dict
    if rec_type == 'Side_events':
        if rec['participant']['patronym'][-1] == 'а':
            gender_text = 'Записана как'
        else:
            gender_text = 'Записан как'
        temp_dict = {
            'main_char': f'{rec['participant']['familia']} {rec['participant']['name']} '
                         f'{rec['participant']['patronym']}',
            'date': f'<u>Дата события</u>: {rec['date']}',
            'secondary_char': f'<u>{gender_text}</u>: {rec['role']}',
            'locality': f'<u>Место события</u>: {rec['locality']}',
            'ID': rec['id'],
            'notes': rec['notes']
        }
        return temp_dict

# Поиск по ID
def id_search(rec_dict, query, response_dict):
    for k, v in rec_dict.items():
        if k == 'Births' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) == str(rec['id']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Weddings' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) == str(rec['id']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Deaths' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) == str(rec['id']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Side_events' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) == str(rec['id']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
    print(f'По запросу {query} было отобрано:')
    for k, v in response_dict.items():
        print(f'в словаре {k} - {len(v)} записей')
    return  response_dict

# Поиск по дате
def date_search(rec_dict, query, response_dict):
    for k, v in rec_dict.items():
        if k == 'Births' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) in rec['date']:
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Weddings' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) in rec['date']:
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Deaths' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) in rec['date']:
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Side_events' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if str(query) in rec['date']:
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
    print(f'По запросу {query} было отобрано:')
    for k, v in response_dict.items():
        print(f'в словаре {k} - {len(v)} записей')
    return  response_dict

# Поиск по дате
def locality_search(rec_dict, query, response_dict):
    for k, v in rec_dict.items():
        if k == 'Births' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.fullmatch(query, rec['locality']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Weddings' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.fullmatch(query, rec['husband']['locality']) or re.fullmatch(query, rec['wife']['locality']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Deaths' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.fullmatch(query, rec['locality']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Side_events' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.fullmatch(query, rec['locality']):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
    print(f'По запросу {query} было отобрано:')
    for k, v in response_dict.items():
        print(f'в словаре {k} - {len(v)} записей')
    return  response_dict

# Поиск по тексту записи
def text_search(rec_dict, query, response_dict):
    for k, v in rec_dict.items():
        if k == 'Births' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(query, str(rec)):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Weddings' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(query, str(rec)):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Deaths' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(query, str(rec)):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
        if k == 'Side_events' and len(rec_dict[k]) > 0:
            response_list = []
            for rec in v:
                if re.search(query, str(rec)):
                    response_list.append(get_rec_pattern(k, rec))
            response_dict[k] = response_list
    print(f'По запросу {query} было отобрано:')
    for k, v in response_dict.items():
        print(f'в словаре {k} - {len(v)} записей')
    return  response_dict



@app.route('/')
def index():
    # При первой загрузке отправляем пустые списки
    return render_template(
        'users.html',
        lists={'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
    )


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '')
    rec_types = request.form.get('rectype', 'all')
    rec_field = request.form.get('field', 'name')
    if rec_field == 'name':
        query = f'(?<![а-яА-ЯёЁ]){query}(?![а-яА-ЯёЁ])'
    if '...' in query:
        query = f'{query.replace('...', '[а-яА-ЯёЁ.]+')}'
    project = projects_dir.joinpath('Taichenachev')


    if rec_types == 'all':
        rec_types = ['Births', 'Weddings', 'Deaths', 'Side_events']
    elif rec_types == 'Side_events':
        rec_types = ['Births', 'Weddings', 'Side_events']
    else:
        rec_types = [rec_types]

    response_dict = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}

    # Формирование словаря из базы данных
    rec_dict = record_request(rec_types, project)

    # Осуществление поиска по заданному полю
    if rec_field == 'name':
        results = name_search(rec_dict, query, response_dict)
    elif rec_field == 'id':
        results = id_search(rec_dict, query, response_dict)
    elif rec_field == 'date':
        results = date_search(rec_dict, query, response_dict)
    elif rec_field == 'locality':
        results = locality_search(rec_dict, query, response_dict)
    elif rec_field == 'text':
        results = text_search(rec_dict, query, response_dict)
    else:
        results = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}

    # Корявая очистка результатов поиска по побочным записям от рождений и свадеб
    if 'Side_events' not in rec_types:
        results['Side_events'] = []
    if rec_types == ['Births', 'Weddings', 'Side_events']:
        results['Births'] = []
        results['Weddings'] = []

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)