import os.path
from pathlib import PosixPath, Path
import json

from django.core.exceptions import ImproperlyConfigured


class BrandingProcessor:
    NECESSARY_REQUISITES = ('INN', 'KPP', 'OGRN', 'SHORT_NAME', 'FULL_NAME', 'LEGAL_ADDR', 'FACT_ADDR', 'SHORT_ADDR',
                            'PHONE', 'EMAIL', 'MAPS_LINK', 'FAX_OWNER_FIRST_NAME', 'FAX_OWNER_LAST_NAME')
    NECESSARY_FILES = ('LOGO', 'FAVICON', 'FAX')
    FILE_LISTS = ('CSS', 'JS')

    def __init__(self, branding_root: Path, config_path: str = '', brand_files_dir: str = 'brand_files'):
        self.branding_root = branding_root
        self.config_path = branding_root / config_path
        self.brand_files_dir = branding_root / brand_files_dir
        self.file_paths, self.requisites, self.coloring = self.__read_config()

    def __check_requisites(self, requisites):
        if requisites is None:
            return 'No requisites mentioned in config'

        missing_requisites = [i for i in self.NECESSARY_REQUISITES if i not in requisites]

        if missing_requisites:
            return f'Missing requisites: {", ".join(missing_requisites)}'

    def __get_files(self, config_dict):
        files = config_dict.get('FILES')
        for label in self.FILE_LISTS:
            if label in files and isinstance(files[label], str):
                files[label] = [files[label]]
        return files

    def __non_existing_files(self, files: dict):
        __errors = list()
        path_list = [value for key, value in files.items() if key not in self.FILE_LISTS]

        for label in self.FILE_LISTS:
            path_list += files.get(label, [])

        for path in path_list:
            if not os.path.isfile(self.brand_files_dir / path) and not os.path.isfile(self.branding_root / path):
                __errors.append(path)
        return __errors

    def __check_files(self, files):
        if files is None:
            return 'No files mentioned in config'

        missing_file_paths = [i for i in self.NECESSARY_FILES if i not in files]

        if missing_file_paths:
            return f'Missing file paths: {", ".join(missing_file_paths)}'

        non_existing_files = self.__non_existing_files(files)

        if non_existing_files:
            return f'Non-existing files: {", ".join(non_existing_files)}'

    def __check_branding(self, config_dict):
        __errors = list()
        files = self.__get_files(config_dict)
        requisites = config_dict.get('REQUISITES')
        coloring = config_dict.get('COLORING', {})

        files_error = self.__check_files(files)
        requisites_error = self.__check_requisites(requisites)

        if files_error:
            __errors.append(files_error)

        if requisites_error:
            __errors.append(requisites_error)

        if __errors:
            raise ImproperlyConfigured('; '.join(__errors))

        return files, requisites, coloring

    def __read_config(self):
        with open(self.config_path / 'config.json') as config:
            full_config = json.load(config)

        return self.__check_branding(full_config)

    def __get_static_path(self, path):
        if os.path.isfile(self.brand_files_dir / path):
            return path
        elif os.path.isfile(self.branding_root / path):
            return os.path.relpath(self.branding_root / path, self.brand_files_dir)

    def static_files(self, no_lists: bool = False):
        if no_lists:
            result = dict()
            source_dict = {label: path for label, path in self.file_paths if label not in self.FILE_LISTS}
        else:
            result = {label: list() for label in self.FILE_LISTS}
            source_dict = self.file_paths

        for label, path in source_dict.items():
            if label not in self.FILE_LISTS:
                result[label] = self.__get_static_path(path)
            else:
                for file_path in path:
                    result[label].append(self.__get_static_path(file_path))
        return result

