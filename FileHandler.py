import json
from pathlib import Path



class FileHandler:

    def __init__(self, project):
        self.project = project
        self.base_folder = Path(__file__).resolve().parent
        self.projects_folder = self.base_folder.joinpath('Projects')
        self.current_project_folder = self.projects_folder.joinpath(self.project)
        self.settings_path = self.current_project_folder.joinpath('settings.json')

    def get_base_folder(self):
        """Возвращает папку приложения."""
        return self.base_folder

    def get_projects_folder(self):
        """Возвращает папку с проектами."""
        return self.projects_folder

    def get_settings(self):
        """Возвращает настройки текущего проекта; возвращает словарь."""
        if self.settings_path.exists():
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"familia_m": "", "familia_f": "", "locality": ""}

    def save_settings(self, familia_m, familia_f, locality):
        """Сохраняет настройки текущего проекта.

        Args:
            familia_m (str): мужская фамилия по умолчанию,
            familia_f (str): женская фамилия по умолчанию,
            locality (str): населенный пункт по умолчанию
        """
        if self.settings_path.exists():
            settings = {"familia_m": familia_m, "familia_f": familia_f, "locality": locality}
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)

    def get_projects(self):
        """Возвращает список с названиями существующих проектов.

        Returns:
            list
        """
        if self.projects_folder.exists():
            return [project.name for project in self.projects_folder.iterdir() if project.is_dir()]
        return []

    @staticmethod
    def get_rec_text(rec):
        """Функция для чтения json файла - стандартной записи БД.

        Args:
            rec (str): путь к файлу

        Returns:
            dict: словарь с записью из БД
        """
        with open(rec, 'r', encoding="UTF-8") as record:
            text = json.load(record)
        return text

    def get_id(self, rec_type):
        """Присваивает актуальный номер ID для записи.

        Args:
            rec_type (str): тип записи: 'Births'/'Weddings'/'Deaths'/'Side_events'

        Returns:
            int: актуальный ID записи в виде числа
        """
        if self.project:
            rec_type_folder = self.current_project_folder.joinpath(rec_type)
            rec_list = [self.get_rec_text(f) for f in rec_type_folder.iterdir()]
            ids = [text['id'] for text in rec_list if 'id' in text.keys()]
            if len(ids) >= 1:
                return max(ids) + 1
            else:
                return 1

    def rec_dump(self, rec_type, file_name, record, report):
        """Записывает новую запись в json файл, а также оставляет сообщение о новой записи в файле 'reports.txt'.

        Args:
            rec_type (str): тип записи: 'Births'/'Weddings'/'Deaths'/'Side_events',
            file_name (str): название файла: f'{file_name}.json',
            record (dict): новая запись БД в формате словаря,
            report (str): сообщение о новой записи
        """
        if self.project:
            rec_type_folder = self.current_project_folder.joinpath(rec_type)
            with open(rec_type_folder.joinpath(f"{file_name}.json"), 'w', encoding="UTF-8") as new_record:
                json.dump(record, new_record, ensure_ascii=False, indent=2)
            with open(self.current_project_folder.joinpath("reports.txt"), "r", encoding="UTF-8") as orig_reports:
                temp_text = orig_reports.read()
            with open(self.current_project_folder.joinpath("reports.txt"), "w", encoding="UTF-8") as mod_reports:
                mod_reports.write(f'{temp_text}{report}\n')

    def save_previous_results(self, results):
        """Сохраняет последний результат поиска по БД в файл 'previous_results.json'.

        Args:
            results (dict): результат поиска по БД в формате словаря
        """
        if self.project:
            with open(self.current_project_folder.joinpath("previous_results.json"), 'w', encoding="UTF-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    def get_previous_results(self):
        """Возвращает последний результат поиска по БД из файла 'previous_results.json'.

        Returns:
            dict: результат поиска по БД
        """
        if self.project:
            with open(self.current_project_folder.joinpath("previous_results.json"), 'r', encoding="UTF-8") as f:
                results = json.load(f)
            return results

    def record_request(self, rec_types):
        """Формирует словарь из записей БД.

        Функция возвращает словарь с четырьмя ключами, соответствующими типам записей в БД,
        значениями выступают списки со словарями из отдельных записей БД.
        Args:
            rec_types (list): список из типов записей: 'Births'/'Weddings'/'Deaths'/'Side_events'

        Returns:
            dict: словарь из записей БД
        """
        rec_dict = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
        for rec_type in rec_types:
            rec_type_folder = self.current_project_folder.joinpath(rec_type)
            rec_list = [self.get_rec_text(f) for f in rec_type_folder.iterdir()]
            rec_dict[rec_type] = rec_list
        return rec_dict
