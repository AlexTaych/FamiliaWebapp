from itertools import chain
from Patterns import name_pattern, non_name_pattern, name_search_pattern
import re


class DataBaseSearch:
    """Производит поиск среди записей проекта.

        Attributes:
            records (dict): Словарь с записями базы данных проекта.
            query (str): Поисковый запрос.
            settings (dict): Словарь с настройками проекта.
            response_dict (dict): Словарь с типами записей, нужен для корректного возврата результатов поиска.
                Структура: {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
        """

    def __init__(self, records, query, settings):
        """Инициализирует объект поиска по записям БД.

        Args:
            records (dict): Словарь с записями базы данных проекта.
            query (str): Поисковый запрос.
            settings (dict): Словарь с настройками проекта.
        """
        self.records = records
        self.query = query
        self.settings = settings
        self.response_dict = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}

    def name_search(self):
        """Поиск среди записей БД по элементам имени.

        Returns:
            dict: Словарь с результатами поиска структурированный по типам записей БД.
        """
        records = self.records
        query = self.query
        settings = self.settings
        response_dict = self.response_dict
        for record_type, record_list in records.items():
            if record_type == 'Births' and len(records[record_type]) > 0:
                newborn_list = [name_pattern(rec, 'newborn', settings) for rec in record_list if
                                re.search(query, name_search_pattern(rec, 'newborn'))]
                father_list = [name_pattern(rec, 'father', settings) for rec in record_list if
                               re.search(query, name_search_pattern(rec, 'father'))]
                mother_list = [name_pattern(rec, 'mother', settings) for rec in record_list if
                               re.search(query, name_search_pattern(rec, 'mother'))]
                response_list = list(chain(newborn_list, father_list, mother_list))
                response_dict[record_type] = response_list
            if record_type == 'Weddings' and len(records[record_type]) > 0:
                husband_list = [name_pattern(rec, 'husband', settings) for rec in record_list if
                                re.search(query, name_search_pattern(rec, 'husband'))]
                wife_list = [name_pattern(rec, 'wife', settings) for rec in record_list if
                             re.search(query, name_search_pattern(rec, 'wife'))]
                response_list = list(chain(husband_list, wife_list))
                response_dict[record_type] = response_list
            if record_type == 'Deaths' and len(records[record_type]) > 0:
                deceased_list = [name_pattern(rec, 'deceased', settings) for rec in record_list if
                                 re.search(query, name_search_pattern(rec, 'deceased'))]
                relative_list = [name_pattern(rec, 'relative', settings) for rec in record_list if
                                 re.search(query, name_search_pattern(rec, 'relative'))]
                response_list = list(chain(deceased_list, relative_list))
                response_dict[record_type] = response_list
            if record_type == 'Side_events' and len(records[record_type]) > 0:
                participant_list = [name_pattern(rec, 'participant', settings) for rec in record_list if
                                    re.search(query, name_search_pattern(rec, 'participant'))]
                susceptor1_list = [name_pattern(rec, 'susceptor1', settings) for rec in records['Births']
                                   if re.search(query, name_search_pattern(rec, 'susceptor1'))]
                susceptor2_list = [name_pattern(rec, 'susceptor2', settings) for rec in records['Births']
                                   if re.search(query, name_search_pattern(rec, 'susceptor2'))]
                husband_guarantor1_list = [name_pattern(rec, 'husband_guarantor1', settings)
                                           for rec in records['Weddings']
                                           if re.search(query, name_search_pattern(rec, 'husband_guarantor1'))]
                husband_guarantor2_list = [name_pattern(rec, 'husband_guarantor2', settings)
                                           for rec in records['Weddings']
                                           if re.search(query, name_search_pattern(rec, 'husband_guarantor2'))]
                wife_guarantor1_list = [name_pattern(rec, 'wife_guarantor1', settings)
                                        for rec in records['Weddings']
                                        if re.search(query, name_search_pattern(rec, 'wife_guarantor1'))]
                wife_guarantor2_list = [name_pattern(rec, 'wife_guarantor2', settings)
                                        for rec in records['Weddings']
                                        if re.search(query, name_search_pattern(rec, 'wife_guarantor2'))]
                response_list = list(chain(participant_list, susceptor1_list, susceptor2_list,
                                           husband_guarantor1_list, husband_guarantor2_list,
                                           wife_guarantor1_list, wife_guarantor2_list))
                response_dict[record_type] = response_list
        return response_dict

    def id_search(self):
        """Поиск среди записей БД по ID записи.

        Returns:
            dict: Словарь с результатами поиска структурированный по типам записей БД.
        """
        records = self.records
        query = self.query
        settings = self.settings
        response_dict = self.response_dict
        for record_type, record_list in records.items():
            if record_type == 'Births' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query == str(rec['id'])]
                response_dict[record_type] = response_list
            if record_type == 'Weddings' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query == str(rec['id'])]
                response_dict[record_type] = response_list
            if record_type == 'Deaths' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query == str(rec['id'])]
                response_dict[record_type] = response_list
            if record_type == 'Side_events' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query == str(rec['id'])]
                response_dict[record_type] = response_list
        return response_dict

    def date_search(self):
        """Поиск среди записей БД по дате записи.

        Returns:
            dict: Словарь с результатами поиска структурированный по типам записей БД.
        """
        records = self.records
        query = self.query
        settings = self.settings
        response_dict = self.response_dict
        for record_type, record_list in records.items():
            if record_type == 'Births' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query in rec["date"]]
                response_dict[record_type] = response_list
            if record_type == 'Weddings' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query in rec["date"]]
                response_dict[record_type] = response_list
            if record_type == 'Deaths' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query in rec["date"]]
                response_dict[record_type] = response_list
            if record_type == 'Side_events' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if query in rec["date"]]
                response_dict[record_type] = response_list
        return response_dict

    def locality_search(self):
        """Поиск среди записей БД по населенному пункту.

        Returns:
            dict: Словарь с результатами поиска структурированный по типам записей БД.
        """
        records = self.records
        query = self.query
        settings = self.settings
        response_dict = self.response_dict
        for record_type, record_list in records.items():
            if record_type == 'Births' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if re.fullmatch(query, rec["locality"])]
                response_dict[record_type] = response_list
            if record_type == 'Weddings' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if re.fullmatch(query, rec["husband"]["locality"])
                                 or re.fullmatch(query, rec["wife"]["locality"])]
                response_dict[record_type] = response_list
            if record_type == 'Deaths' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if re.fullmatch(query, rec["locality"])]
                response_dict[record_type] = response_list
            if record_type == 'Side_events' and len(records[record_type]) > 0:
                response_list = [non_name_pattern(rec, record_type, settings) for rec in record_list
                                 if re.fullmatch(query, rec["locality"])]
                response_dict[record_type] = response_list
        return response_dict

    def text_search(self):
        """Поиск среди записей БД по текстовому формату записи.

        Returns:
            dict: Словарь с результатами поиска структурированный по типам записей БД.
        """
        records = self.records
        query = self.query
        settings = self.settings
        response_dict = self.response_dict
        for record_type, record_list in records.items():
            if record_type == 'Births' and len(records[record_type]) > 0:
                temp_list = [non_name_pattern(rec, record_type, settings) for rec in record_list]
                response_list = [rec for rec in temp_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
            if record_type == 'Weddings' and len(records[record_type]) > 0:
                temp_list = [non_name_pattern(rec, record_type, settings) for rec in record_list]
                response_list = [rec for rec in temp_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
            if record_type == 'Deaths' and len(records[record_type]) > 0:
                temp_list = [non_name_pattern(rec, record_type, settings) for rec in record_list]
                response_list = [rec for rec in temp_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
            if record_type == 'Side_events' and len(records[record_type]) > 0:
                temp_list = [non_name_pattern(rec, record_type, settings) for rec in record_list]
                response_list = [rec for rec in temp_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
        return response_dict

    def result_search(self, previous_results):
        """Поиск среди результатов предыдущего поискового запроса.

        Args:
            previous_results (dict): Словарь с результатами предыдущего поискового запроса.

        Returns:
            dict: Словарь с результатами поиска структурированный по типам записей БД.
        """
        query = self.query
        response_dict = self.response_dict
        for record_type, record_list in previous_results.items():
            if record_type == 'Births' and len(previous_results[record_type]) > 0:
                response_list = [rec for rec in record_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
            if record_type == 'Weddings' and len(previous_results[record_type]) > 0:
                response_list = [rec for rec in record_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
            if record_type == 'Deaths' and len(previous_results[record_type]) > 0:
                response_list = [rec for rec in record_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
            if record_type == 'Side_events' and len(previous_results[record_type]) > 0:
                response_list = [rec for rec in record_list if re.search(query, str(rec))]
                response_dict[record_type] = response_list
        return response_dict
