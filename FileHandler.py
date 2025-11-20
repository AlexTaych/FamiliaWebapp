import json
from pathlib import Path


class FileHandler:
    """Производит все операции с файлами проекта.

    Attributes:
        project (str): Название проекта / название папки проекта.
        records_dict (dict): Словарь с типами записей / названия папок с типами записей.
            Структура: {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
        base_folder (Path): Путь к папке приложения.
        projects_folder (Path): Путь к папке с проектами.
        current_project_folder (Path): Путь к текущему проекту.
        settings_path (Path): Путь к файлу настроек проекта.
    """

    def __init__(self, project: str) -> None:
        """Инициализирует объект обработчика файлов.

        Args:
            project (str): Название проекта / название папки проекта.
        """
        self.project = project
        self.records_dict = {'Births': [], 'Weddings': [], 'Deaths': [], 'Side_events': []}
        self.base_folder = Path(__file__).resolve().parent
        self.projects_folder = self.base_folder.joinpath('Projects')
        self.current_project_folder = self.projects_folder.joinpath(self.project)
        self.settings_path = self.current_project_folder.joinpath('settings.json')

    def project_initiation(self) -> None:
        """Формирует папки и рабочие файлы нового проекта.

        Создает 4 папки по типам записи, названия берет из ключей record_dict,
        также создает файл для отчетов - 'reports.txt'
        и файл для сохранения результатов последнего поиска по БД - 'previous_results.json'.
        """
        if self.project:
            cpf = self.current_project_folder
            for rec_type in self.records_dict:
                cpf.joinpath(rec_type).mkdir(parents=True, exist_ok=True)
            with open(cpf.joinpath('reports.txt'), "w", encoding="utf-8") as f:
                pass
            with open(cpf.joinpath('settings.json'), "w", encoding="utf-8") as f:
                pass
            with open(cpf.joinpath('previous_results.json'), "w", encoding="utf-8") as f:
                json.dump(self.records_dict, f, ensure_ascii=False, indent=2)

    def get_base_folder(self) -> Path:
        """Возвращает папку приложения."""
        if self.base_folder:
            return self.base_folder

    def get_projects_folder(self) -> Path:
        """Возвращает папку с проектами."""
        if self.projects_folder:
            return self.projects_folder

    def get_settings(self) -> dict:
        """Возвращает настройки текущего проекта.

        Returns:
            dict
        """
        if self.settings_path.exists():
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"familia_m": "", "familia_f": "", "locality": ""}

    def save_settings(self, familia_m: str, familia_f: str, locality: str) -> None:
        """Сохраняет настройки текущего проекта.

        Args:
            familia_m (str): Мужская фамилия по умолчанию.
            familia_f (str): Женская фамилия по умолчанию.
            locality (str): Населенный пункт по умолчанию.
        """
        if self.settings_path.exists():
            settings = {"familia_m": familia_m, "familia_f": familia_f, "locality": locality}
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

    def get_projects(self) -> list:
        """Возвращает список с названиями существующих проектов.

        Returns:
            list
        """
        if self.projects_folder.exists():
            return [project.name for project in self.projects_folder.iterdir() if project.is_dir()]
        return []

    @staticmethod
    def get_rec_text(rec_path: Path) -> dict:
        """Функция для чтения json файла - стандартной записи БД.

        Args:
            rec_path (Path): Путь к файлу.

        Returns:
            dict: Словарь с записью из БД.
        """
        with open(rec_path, "r", encoding="UTF-8") as rec:
            record = json.load(rec)
        return record

    def get_id(self, rec_type: str) -> int:
        """Присваивает актуальный номер ID для записи.

        Args:
            rec_type (str): Тип записи: 'Births'/'Weddings'/'Deaths'/'Side_events'.

        Returns:
            int: Актуальный ID записи в виде числа.
        """
        if self.project:
            rec_type_folder = self.current_project_folder.joinpath(rec_type)
            rec_list = [self.get_rec_text(f) for f in rec_type_folder.iterdir()]
            ids = [text['id'] for text in rec_list if 'id' in text.keys()]
            if len(ids) >= 1:
                return max(ids) + 1
            else:
                return 1

    def rec_dump(self, rec_type: str, file_name: str, record: dict, report: str) -> None:
        """Записывает новую запись в json файл, а также оставляет сообщение о новой записи в файле 'reports.txt'.

        Args:
            rec_type (str): Тип записи: 'Births'/'Weddings'/'Deaths'/'Side_events'.
            file_name (str): Название файла.
            record (dict): Новая запись БД в формате словаря.
            report (str): Сообщение о новой записи.
        """
        if self.project:
            cpf = self.current_project_folder
            rec_type_folder = cpf.joinpath(rec_type)
            with open(rec_type_folder.joinpath(f"{file_name}.json"), "w", encoding="UTF-8") as new_record:
                json.dump(record, new_record, ensure_ascii=False, indent=2)
            with open(cpf.joinpath("reports.txt"), "a", encoding="UTF-8") as mod_reports:
                mod_reports.write(f'{report}\n')

    def save_previous_results(self, results: dict) -> None:
        """Сохраняет последний результат поиска по БД в файл 'previous_results.json'.

        Args:
            results (dict): Результат поиска по БД в формате словаря.
        """
        if self.project:
            with open(self.current_project_folder.joinpath("previous_results.json"), "w", encoding="UTF-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    def get_previous_results(self) -> dict:
        """Возвращает последний результат поиска по БД из файла 'previous_results.json'.

        Returns:
            dict: Результат поиска по БД.
        """
        if self.project:
            with open(self.current_project_folder.joinpath("previous_results.json"), "r", encoding="UTF-8") as f:
                results = json.load(f)
            return results

    def record_request(self, rec_types: list) -> dict:
        """Формирует словарь из записей БД.

        Функция возвращает словарь с четырьмя ключами, соответствующими типам записей в БД,
        значениями выступают списки со словарями из отдельных записей БД.
        Args:
            rec_types (list): Список из типов записей: 'Births'/'Weddings'/'Deaths'/'Side_events'.

        Returns:
            dict: Словарь из записей БД.
        """
        rec_dict = self.records_dict
        for rec_type in rec_types:
            rec_type_folder = self.current_project_folder.joinpath(rec_type)
            rec_list = [self.get_rec_text(f) for f in rec_type_folder.iterdir()]
            rec_dict[rec_type] = rec_list
        return rec_dict
