from flask import  Flask, render_template, request, redirect, url_for, session, jsonify
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
projects_dir = Path(__file__).resolve().parent / "Projects"

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

# Функция для сохранения данных в json файл
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

# Функции поиска
# Обращение к базе данных и формирование словарей для последующего поиска
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
                        'main_char': f'<b>{rec['newborn']['familia']} {rec['newborn']['name']} '
                                     f'{rec['newborn']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['father']['familia']} {rec['father']['name']} '
                                     f'{rec['father']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['mother']['familia']} {rec['mother']['name']} '
                                     f'{rec['mother']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['husband']['familia']} {rec['husband']['name']} '
                                     f'{rec['husband']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['wife']['familia']} {rec['wife']['name']} '
                                     f'{rec['wife']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['deceased']['familia']} {rec['deceased']['name']} '
                                     f'{rec['deceased']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['relative']['familia']} {rec['relative']['name']} '
                                     f'{rec['relative']['patronym']}</b>',
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
                        'main_char': f'<b>{rec['participant']['familia']} {rec['participant']['name']} '
                                     f'{rec['participant']['patronym']}</b>',
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
                            'main_char': f'<b>{rec['susceptors'][n]['familia']} {rec['susceptors'][n]['name']} '
                                         f'{rec['susceptors'][n]['patronym']}</b>',
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
                            'main_char': f'<b>{rec['husband_guarantors'][n]['familia']} '
                                         f'{rec['husband_guarantors'][n]['name']} '
                                         f'{rec['husband_guarantors'][n]['patronym']}</b>',
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
                            'main_char': f'<b>{rec['wife_guarantors'][n]['familia']} '
                                         f'{rec['wife_guarantors'][n]['name']} '
                                         f'{rec['wife_guarantors'][n]['patronym']}</b>',
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
    return  response_dict

# Функция формирования записей для поисковых запросов к неименным элементам записей
def get_rec_pattern(rec_type, rec):
    if rec_type == 'Births':
        if rec['newborn']['familia'] == get_settings()['familia_f']:
            gender_text = 'родилась'
        else:
            gender_text = 'родился'
        temp_dict = {
            'main_char': f'<b>{rec['newborn']['familia']} {rec['newborn']['name']} '
                         f'{rec['newborn']['patronym']}</b>',
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
            'main_char': f'Жених: <b>{rec['husband']['familia']} {rec['husband']['name']} '
                         f'{rec['husband']['patronym']}</b><br>'
                         f'Невеста: <b>{rec['wife']['familia']} {rec['wife']['name']} '
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
            'main_char': f'<b>{rec['deceased']['familia']} {rec['deceased']['name']} '
                         f'{rec['deceased']['patronym']}</b>',
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
            'main_char': f'<b>{rec['participant']['familia']} {rec['participant']['name']} '
                         f'{rec['participant']['patronym']}</b>',
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
    return  response_dict

# Поиск по тексту записи
def text_search(rec_dict, query, response_dict):
    for k, v in rec_dict.items():
        if k == 'Births' and len(rec_dict[k]) > 0:
            response_list = []
            temp_list = []
            for rec in v:
                temp_list.append(get_rec_pattern(k, rec))
            for i in temp_list:
                if re.search(query, str(i)):
                    response_list.append(i)
            response_dict[k] = response_list
        if k == 'Weddings' and len(rec_dict[k]) > 0:
            response_list = []
            temp_list = []
            for rec in v:
                temp_list.append(get_rec_pattern(k, rec))
            for i in temp_list:
                if re.search(query, str(i)):
                    response_list.append(i)
            response_dict[k] = response_list
        if k == 'Deaths' and len(rec_dict[k]) > 0:
            response_list = []
            temp_list = []
            for rec in v:
                temp_list.append(get_rec_pattern(k, rec))
            for i in temp_list:
                if re.search(query, str(i)):
                    response_list.append(i)
            response_dict[k] = response_list
        if k == 'Side_events' and len(rec_dict[k]) > 0:
            response_list = []
            temp_list = []
            for rec in v:
                temp_list.append(get_rec_pattern(k, rec))
            for i in temp_list:
                if re.search(query, str(i)):
                    response_list.append(i)
            response_dict[k] = response_list
    return  response_dict


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

        # Создание папки проекта и внутренней структуры папок
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

# Запись о смерти
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

# Запись о побочном событии
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


# ПОИСК
@app.route('/search_initial')
def search_initial():
    # При первой загрузке отправляем пустые списки
    return render_template(
        'search.html',
        lists={'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
    )


@app.route('/search_query', methods=['POST'])
def search_query():
    query = request.form.get('query', '')
    rec_types = request.form.get('rectype', 'all')
    rec_field = request.form.get('field', 'name')
    if rec_field == 'name':
        query = f'(?<![а-яА-ЯёЁ]){query}(?![а-яА-ЯёЁ])'
    if '...' in query:
        query = f'{query.replace('...', '[а-яА-ЯёЁ.]+')}'
    current_project = session.get('current_project', 'Проект не выбран')
    projects_path = projects_dir.joinpath(current_project)


    if rec_types == 'all':
        rec_types = ['Births', 'Weddings', 'Deaths', 'Side_events']
    elif rec_types == 'Side_events':
        rec_types = ['Births', 'Weddings', 'Side_events']
    else:
        rec_types = [rec_types]

    response_dict = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}

    # Формирование словаря из базы данных
    rec_dict = record_request(rec_types, projects_path)

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