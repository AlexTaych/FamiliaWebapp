# Свалка всех шаблонов

def name_pattern(record: dict, character: str, settings: dict) -> dict:
    """Функция формирует словарь с данными из БД для отображения на странице HTML.

    В отличие от non_name_pattern() формирует персонаж-зависимый словарь, т. е.
    текст записи меняется в зависимости от роли представленной в 'character'.
    Подобный подход облегчает восприятие результатов поиска.
    Args:
        record (dict): Исходная запись БД.
        character (str): Роль персоны, влияет на представление возвращаемого словаря.
        settings (dict): Словарь настроек, нужен для формирования гендерно зависимых формулировок.

    Returns:
        dict: Словарь с данными из БД для отображения на странице HTML.
    """
    if character == 'newborn':
        if record["newborn"]["familia"] == settings["familia_f"]:
            gender_text = 'родилась'
        else:
            gender_text = 'родился'
        pattern = {
            'main_char': f'<b>{record["newborn"]["familia"]} {record["newborn"]["name"]} '
                         f'{record["newborn"]["patronym"]}</b>',
            "date": f'<u>{gender_text}</u> {record["date"]}',
            'secondary_char': f'<u>Отец</u>: <b>{record["father"]["name"]} {record["father"]["patronym"]}</b><br>'
                              f'<u>Мать</u>: <b>{record["mother"]["name"]} {record["mother"]["patronym"]}</b><br>'
                              f'<u>Восприемники</u>: {" ".join(record["susceptors"]["1st"].values())} и '
                              f'{" ".join(record["susceptors"]["2nd"].values())}',
            "locality": f'<u>Место рождения</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character in ['father', 'mother']:
        if character == 'father':
            gender_text = ["записан", "отец"]
            spouse = ["Жена", "mother"]
        else:
            gender_text = ["записана", "мать"]
            spouse = ["Муж", "father"]
        pattern = {
            'main_char': f'<b>{record[character]["familia"]} {record[character]["name"]} '
                         f'{record[character]["patronym"]}</b>',
            "date": f'{record["date"]} {gender_text[0]} как <u>{gender_text[1]}</u>',
            'secondary_char': f'<u>Ребенок</u>: <b>{record["newborn"]["name"]} '
                              f'{record["newborn"]["patronym"]}</b><br>'
                              f'<u>{spouse[0]}</u>: <b>{record[spouse[1]]["name"]} {record[spouse[1]]["patronym"]}</b><br>'
                              f'<u>Восприемники</u>: {" ".join(record["susceptors"]["1st"].values())} и '
                              f'{" ".join(record["susceptors"]["2nd"].values())}',
            "locality": f'<u>Место проживания</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character in ['husband','wife']:
        if character == 'husband':
            gender_text = ["записан", "жених"]
            spouse = ["Невеста", "wife"]
            self_locality = record["husband"]["locality"]
            spouse_locality = record["wife"]["locality"]
        else:
            gender_text = ["записана", "невеста"]
            spouse = ["Жених", "husband"]
            self_locality = record["wife"]["locality"]
            spouse_locality = record["husband"]["locality"]
        pattern = {
            'main_char': f'<b>{record[character]["familia"]} {record[character]["name"]} '
                         f'{record[character]["patronym"]}</b>',
            "date": f'{record["date"]} {gender_text[0]} как <u>{gender_text[1]}</u>',
            'secondary_char': f'<u>{spouse[0]}</u>: <b>{record[spouse[1]]["familia"]} {record[spouse[1]]["name"]} '
                              f'{record[spouse[1]]["patronym"]}</b>; '
                              f'родом из {spouse_locality}<br>'
                              f'<u>Поручители жениха</u>: {" ".join(record["husband_guarantors"]["1st"].values())} и '
                              f'{" ".join(record["husband_guarantors"]["2nd"].values())}<br>'
                              f'<u>Поручители невесты</u>: {" ".join(record["wife_guarantors"]["1st"].values())} и '
                              f'{" ".join(record["wife_guarantors"]["2nd"].values())}',
            "locality": f'<u>Место проживания</u>: {self_locality}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character == 'deceased':
        if record["deceased"]["familia"] == settings['familia_f']:
            gender_text = 'умерла'
        else:
            gender_text = 'умер'
        if record["relative"]["patronym"] == '-':
            relative_text = ''
        else:
            relative_text = (f'<u>{record["relative"]["relation_degree"]}</u>: <b>{record["relative"]["name"]} '
                             f'{record["relative"]["patronym"]}</b>')
        pattern = {
            'main_char': f'<b>{record["deceased"]["familia"]} {record["deceased"]["name"]} '
                         f'{record["deceased"]["patronym"]}</b>',
            "date": f'{record["date"]} <u>{gender_text}</u> от: {record["death_cause"]}',
            'secondary_char': relative_text,
            "locality": f'<u>Место смерти</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character == 'relative':
        if record["relative"]["relation_degree"] == 'отец':
            relative_text = f'<u>отец</u> умершего ребенка;'
            deceased = '<u>Ребенок</u>'
        elif record["relative"]["relation_degree"] == 'муж':
            relative_text = f'<u>муж</u> умершей;'
            deceased = '<u>Жена</u>'
        else:
            relative_text = f'<u>родственник</u> умершего;'
            deceased = '<u>Родственник</u>'
        pattern = {
            'main_char': f'<b>{record["relative"]["familia"]} {record["relative"]["name"]} '
                         f'{record["relative"]["patronym"]}</b>',
            "date": f'{relative_text} причина смерти: {record["death_cause"]};<br><u>дата смерти</u>: {record["date"]}',
            'secondary_char': f'{deceased}: <b>{record["deceased"]["name"]} '
                              f'{record["deceased"]["patronym"]}</b>',
            "locality": f'<u>Место смерти</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character == 'participant':
        if record["participant"]["patronym"][-1] == 'а':
            gender_text = 'Записана'
        else:
            gender_text = 'Записан'
        pattern = {
            'main_char': f'<b>{record["participant"]["familia"]} {record["participant"]["name"]} '
                         f'{record["participant"]["patronym"]}</b>',
            "date": f'Дата события: {record["date"]}',
            'secondary_char': f'<u>{gender_text} как</u>: {record["role"]}',
            "locality": f'<u>Место события</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character in ['susceptor1', 'susceptor2']:
        if character == 'susceptor1':
            n = "1st"
        else:
            n = "2nd"
        if record["susceptors"][n]["patronym"][-1] == 'а':
            gender_text = 'Записана как <u>восприемница</u>'
        else:
            gender_text = 'Записан как <u>восприемник</u>'
        pattern = {
            'main_char': f'<b>{record["susceptors"][n]["familia"]} {record["susceptors"][n]["name"]} '
                         f'{record["susceptors"][n]["patronym"]}</b>',
            "date": f'Дата события: {record["date"]}',
            'secondary_char': f'{gender_text} при рождении: <b>{record["newborn"]["familia"]} '
                              f'{record["newborn"]["name"]} {record["newborn"]["patronym"]}</b><br>'
                              f'<u>Отец</u>: <b>{record["father"]["name"]} '
                              f'{record["father"]["patronym"]}</b><br>'
                              f'<u>Мать</u>: <b>{record["mother"]["name"]} '
                              f'{record["mother"]["patronym"]}</b><br>',
            "locality": f'<u>Место события</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if character in ['husband_guarantor1', 'husband_guarantor2', 'wife_guarantor1', 'wife_guarantor2']:
        if character in ['husband_guarantor1','wife_guarantor1']:
            n = "1st"
        else:
            n = "2nd"
        if 'husband' in character:
            rel_text = ["husband_guarantors", "жениха"]
        else:
            rel_text = ["wife_guarantors", "невесты"]
        pattern = {
            'main_char': f'<b>{record[rel_text[0]][n]["familia"]} '
                         f'{record[rel_text[0]][n]["name"]} '
                         f'{record[rel_text[0]][n]["patronym"]}</b>',
            "date": f'Дата события: {record["date"]}',
            'secondary_char': f'Записан как <u>поручитель {rel_text[1]}</u> на свадьбе:<br>'
                              f'<u>Жених</u>: <b>{record["husband"]["familia"]} {record["husband"]["name"]} '
                              f'{record["husband"]["patronym"]}</b><br>'
                              f'<u>Невеста</u>: <b>{record["wife"]["familia"]} {record["wife"]["name"]} '
                              f'{record["wife"]["patronym"]}</b><br>',
            "locality": f'<u>Место события</u>: {record["husband"]["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern


def non_name_pattern(record: dict, record_type: str, settings: dict) -> dict:
    """Функция формирует словарь с данными из БД для отображения на странице HTML.

    Формирует словарь с данными для неименных поисковых запросов, поэтому результат
    зависит исключительно от типа записи и являет собой стандартное представление записи на странице HTML.
    Args:
        record (dict): Исходная запись БД.
        record_type (str): Тип записи к которому относится record.
        settings (dict): Словарь настроек, нужен для формирования гендерно зависимых формулировок.

    Returns:
        dict: Словарь с данными из БД для отображения на странице HTML.
    """
    if record_type == 'Births':
        if record["newborn"]["familia"] == settings['familia_f']:
            gender_text = 'родилась'
        else:
            gender_text = 'родился'
        pattern = {
            'main_char': f'<b>{record["newborn"]["familia"]} {record["newborn"]["name"]} '
                         f'{record["newborn"]["patronym"]}</b>',
            "date": f'<u>{gender_text}</u> {record["date"]}',
            'secondary_char': f'<u>Отец</u>: <b>{record["father"]["name"]} {record["father"]["patronym"]}</b><br>'
                              f'<u>Мать</u>: <b>{record["mother"]["name"]} {record["mother"]["patronym"]}</b><br>'
                              f'<u>Восприемники</u>: {" ".join(record["susceptors"]["1st"].values())} и '
                              f'{" ".join(record["susceptors"]["2nd"].values())}',
            "locality": f'<u>Место рождения</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if record_type == 'Weddings':
        pattern = {
            'main_char': f'Жених: <b>{record["husband"]["familia"]} {record["husband"]["name"]} '
                         f'{record["husband"]["patronym"]}</b><br>'
                         f'Невеста: <b>{record["wife"]["familia"]} {record["wife"]["name"]} '
                         f'{record["wife"]["patronym"]}</b>',
            "date": f'<u>Дата свадьбы</u>: {record["date"]}',
            'secondary_char': f'<u>Поручители жениха</u>: {" ".join(record["husband_guarantors"]["1st"].values())} и '
                              f'{" ".join(record["husband_guarantors"]["2nd"].values())}<br>'
                              f'<u>Поручители невесты</u>: {" ".join(record["wife_guarantors"]["1st"].values())} и '
                              f'{" ".join(record["wife_guarantors"]["2nd"].values())}',
            "locality": f'<u>Место жительства жениха</u>: {record["husband"]["locality"]}<br>'
                        f'<u>Место жительства невесты</u>: {record["wife"]["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if record_type == 'Deaths':
        if record["deceased"]["familia"] == settings['familia_f']:
            gender_text = f'{record["date"]} <u>умерла</u> от: {record["death_cause"]}'
        else:
            gender_text = f'{record["date"]} <u>умер</u> от: {record["death_cause"]}'
        if record["relative"]["patronym"] == '-':
            relative_text = ''
        else:
            relative_text = (f'<u>{record["relative"]["relation_degree"]}</u>: <b>{record["relative"]["name"]} '
                             f'{record["relative"]["patronym"]}</b>')
        pattern = {
            'main_char': f'<b>{record["deceased"]["familia"]} {record["deceased"]["name"]} '
                         f'{record["deceased"]["patronym"]}</b>',
            "date": gender_text,
            'secondary_char': relative_text,
            "locality": f'<u>Место смерти</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern
    if record_type == 'Side_events':
        if record["participant"]["patronym"][-1] == 'а':
            gender_text = 'Записана как'
        else:
            gender_text = 'Записан как'
        pattern = {
            'main_char': f'<b>{record["participant"]["familia"]} {record["participant"]["name"]} '
                         f'{record["participant"]["patronym"]}</b>',
            "date": f'<u>Дата события</u>: {record["date"]}',
            'secondary_char': f'<u>{gender_text}</u>: {record["role"]}',
            "locality": f'<u>Место события</u>: {record["locality"]}',
            'ID': record['id'],
            'notes': record['notes']
        }
        return pattern


def name_search_pattern(record: dict, character: str) -> str:
    """Функция формирует строку с ФИО персоны для именных поисковых запросов к БД.

    Формирует словарь с данными для неименных поисковых запросов, поэтому результат
    зависит исключительно от типа записи и являет собой стандартное представление записи на странице HTML.
    Args:
        record (dict): Исходная запись БД.
        character (str): Роль персоны в записи БД.

    Returns:
        str: строка с ФИО персоны для именных поисковых запросов к БД.
    """
    if character in ['susceptor1', 'susceptor2']:
        if character == 'susceptor1':
            n = "1st"
        else:
            n = "2nd"
        return (f'{record["susceptors"][n]["familia"]} {record["susceptors"][n]["name"]} '
                f'{record["susceptors"][n]["patronym"]}')
    if character in ['husband_guarantor1', 'husband_guarantor2', 'wife_guarantor1', 'wife_guarantor2']:
        if character in ['husband_guarantor1', 'wife_guarantor1']:
            n = "1st"
        else:
            n = "2nd"
        if 'husband' in character:
            rel_text = ["husband_guarantors", "жениха"]
        else:
            rel_text = ["wife_guarantors", "невесты"]
        return (f'{record[rel_text[0]][n]["familia"]} {record[rel_text[0]][n]["name"]} '
                f'{record[rel_text[0]][n]["patronym"]}')
    else:
        return f'{record[character]["familia"]} {record[character]["name"]} {record[character]["patronym"]}'


def name_pat_reg():
    """Регулярное выражение для имени и отчества.

    Нужно для проверки корректности ввода данных с учетом правил замены отсутствующих элементов имени на "...".
    """
    return (r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.])) '
                r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я][а-я]+\.{3}[а-я]+(?![а-яА-Я+\.])|'
                r'(?<![а-яА-Я+\.])[А-Я]\.{3}[а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}(?![а-яА-Я+\.]))')


def full_name_reg():
    """Регулярное выражение для ФИО.

    Нужно для проверки корректности ввода данных с учетом правил замены отсутствующих элементов имени на "...".
    """
    return (r'((?<![а-яА-Я+\.])[А-Я][а-я]+(?![а-яА-Я+\.])|(?<![а-яА-Я+\.])\.{3}[а-я]+(?![а-яА-Я+\.])|'
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


def record_pattern(rec_type, rec_raw, rec_id, settings):
    """Функция формирует словарь с записью БД.

    Формирует словарь с данными для неименных поисковых запросов, поэтому результат
    зависит исключительно от типа записи и являет собой стандартное представление записи на странице HTML.
    Args:
        rec_type (str): Тип записи.
        rec_raw (dict): Данные для записи, полученные с клиентской стороны.
        rec_id (int): Актуальный номер записи среди записей БД этого типа.
        settings (dict): Словарь с настройками проекта.

    Returns:
        dict: Словарь со стандартной записью БД.
    """
    if rec_type == 'Births':
        # Формирование дополнительных переменных для json файла
        date = f'{rec_raw["date_list"][2]}.{rec_raw["date_list"][1]}.{rec_raw["date_list"][0]}'
        familia_m = settings['familia_m']
        familia_f = settings['familia_f']
        newborn_name, newborn_patronym = rec_raw['newborn'].split()
        if rec_raw['gender'] == 'м':
            newborn_familia = familia_m
        else:
            newborn_familia = familia_f
        if '-' in rec_raw['father']:
            father_familia = '-'
        else:
            father_familia = familia_m
        father_name, father_patronym = rec_raw['father'].split()
        mother_name, mother_patronym = rec_raw['mother'].split()
        susceptor_prim_familia, susceptor_prim_name, susceptor_prim_patronym = rec_raw['susceptor1'].split()
        susceptor_sec_familia, susceptor_sec_name, susceptor_sec_patronym = rec_raw['susceptor2'].split()

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            "date": date,
            "newborn": {"familia": newborn_familia, "name": newborn_name, "patronym": newborn_patronym},
            "father": {"familia": father_familia, "name": father_name, "patronym": father_patronym},
            "mother": {"familia": familia_f, "name": mother_name, "patronym": mother_patronym},
            "locality": rec_raw["locality"],
            "susceptors": {
                "1st": {
                    "familia": susceptor_prim_familia,
                    "name": susceptor_prim_name,
                    "patronym": susceptor_prim_patronym
                },
                "2nd": {
                    "familia": susceptor_sec_familia,
                    "name": susceptor_sec_name,
                    "patronym": susceptor_sec_patronym
                }
            },
            'notes': rec_raw["notes"]
        }
        return record
    if rec_type == 'Weddings':
        # Формирование дополнительных переменных для json файла
        date = f'{rec_raw["date_list"][2]}.{rec_raw["date_list"][1]}.{rec_raw["date_list"][0]}'
        husband_familia, husband_name, husband_patronym = rec_raw["husband"].split()
        wife_familia, wife_name, wife_patronym = rec_raw["wife"].split()
        hus_guarantor_prim_familia, hus_guarantor_prim_name, hus_guarantor_prim_patronym = (
            rec_raw["hus_guarantor1"].split()
        )
        hus_guarantor_sec_familia, hus_guarantor_sec_name, hus_guarantor_sec_patronym = (
            rec_raw["hus_guarantor2"].split()
        )
        wif_guarantor_prim_familia, wif_guarantor_prim_name, wif_guarantor_prim_patronym = (
            rec_raw["wif_guarantor1"].split()
        )
        wif_guarantor_sec_familia, wif_guarantor_sec_name, wif_guarantor_sec_patronym = (
            rec_raw["wif_guarantor2"].split()
        )

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            "date": date,
            "husband": {
                "familia": husband_familia,
                "name": husband_name,
                "patronym": husband_patronym,
                "locality": rec_raw["hus_locality"]
            },
            "wife": {
                "familia": wife_familia,
                "name": wife_name,
                "patronym": wife_patronym,
                "locality": rec_raw["wif_locality"]
            },
            "husband_guarantors": {
                "1st": {
                    "familia": hus_guarantor_prim_familia,
                    "name": hus_guarantor_prim_name,
                    "patronym": hus_guarantor_prim_patronym
                },
                "2nd": {
                    "familia": hus_guarantor_sec_familia,
                    "name": hus_guarantor_sec_name,
                    "patronym": hus_guarantor_sec_patronym
                }
            },
            "wife_guarantors": {
                "1st": {
                    "familia": wif_guarantor_prim_familia,
                    "name": wif_guarantor_prim_name,
                    "patronym": wif_guarantor_prim_patronym
                },
                "2nd": {
                    "familia": wif_guarantor_sec_familia,
                    "name": wif_guarantor_sec_name,
                    "patronym": wif_guarantor_sec_patronym
                }
            },
            'notes': rec_raw["notes"]
        }
        return record
    if rec_type == 'Deaths':
        # Формирование дополнительных переменных для json файла
        date = f'{rec_raw["date_list"][2]}.{rec_raw["date_list"][1]}.{rec_raw["date_list"][0]}'
        relation_degree = rec_raw["relation_degree"]
        familia_m = settings['familia_m']
        familia_f = settings['familia_f']
        if rec_raw['gender'] == 'м':
            deceased_familia = familia_m
        else:
            deceased_familia = familia_f
        deceased_name, deceased_patronym = rec_raw["deceased"].split()
        if '-' in rec_raw["relative"]:
            relative_familia = '-'
        else:
            relative_familia = familia_m
        relative_name, relative_patronym = rec_raw["relative"].split()
        if '-' not in rec_raw["relative"] and not rec_raw["relation_degree"]:
            relation_degree = 'отец'

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            "date": date,
            "deceased": {"familia": deceased_familia, "name": deceased_name, "patronym": deceased_patronym},
            "death_cause": rec_raw["death_cause"],
            "relative": {
                "familia": relative_familia,
                "name": relative_name,
                "patronym": relative_patronym,
                "relation_degree": relation_degree
            },
            "locality": rec_raw["locality"],
            'notes': rec_raw["notes"]
        }
        return record
    if rec_type == 'Side_events':
        # Формирование дополнительных переменных для json файла
        date = f'{rec_raw["date_list"][2]}.{rec_raw["date_list"][1]}.{rec_raw["date_list"][0]}'
        if rec_raw['gender'] == 'м':
            participant_familia = settings['familia_m']
        else:
            participant_familia = settings['familia_f']
        participant_name, participant_patronym = rec_raw["participant"].split()

        # Формирование словаря для последующей передачи в json файл
        record = {
            'id': rec_id,
            "date": date,
            "participant": {
                "familia": participant_familia,
                "name": participant_name,
                "patronym": participant_patronym
            },
            "role": rec_raw["role"],
            "locality": rec_raw["locality"],
            'notes': rec_raw["notes"]
        }
        return record


def name_pat_error(name):
    """Сообщение об ошибке в заполнении имени и отчества

    Args:
        name (str): Текст из поля в котором содержится ошибка.
    """
    return (f'Неправильно заполненные данные: "{name}".\n '
            f'Имя и отчество должны соответствовать шаблону: "Иван Иванович"')


def full_name_error(name):
    """Сообщение об ошибке в заполнении ФИО

    Args:
        name (str): Текст из поля в котором содержится ошибка.
    """
    return (f'Неправильно заполненные данные: "{name}".\n'
            f'Фамилия, имя и отчество должны соответствовать шаблону: "Иванов Иван Иванович"')
