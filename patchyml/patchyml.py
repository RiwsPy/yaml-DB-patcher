import yaml
import json
import os
from pathlib import Path
from typing import Set, List
from mimetypes import guess_type

from .decorators import dump_file
from .db import Dyct, StrModel

BASE_DIR = Path(__file__).resolve().parent.parent


class YamlReader:
    str_model = StrModel
    file_order = "_order.ini"
    ignore_files = {"__init__.py", "__pycache__"}
    _data = ""

    def __init__(self, **kwargs):
        self._dirname = ""
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def data(self) -> str:
        return self._data

    def convert(self) -> None:
        self._data = self.str_model(self._data).replace_fix_string()

    def load(self, path: str) -> None:
        """
        Lit le fichier de l'instance ou tous les fichiers présents dans le dossier, les concatènent et les renvoient
        A ce stade, le contenu n'est pas encore interprété
        """

        def file_content() -> str:
            with open(self._dirname, "rt") as file:
                patchpath = (
                    self._dirname.replace(str(BASE_DIR) + "/", "")
                    .partition("/")[2]
                    .replace("/", ".")
                )
                content = self.str_model(file.read()).replace_path_string(patchpath)
            return content

        self._dirname = os.path.abspath(path)

        content_file = ""
        if os.path.isdir(path):  # directory
            for filename in self.get_order_files():
                if filename not in self.get_ignore_files():
                    self.load(os.path.join(path, filename))
        else:  # file
            if self.file_has_yaml_mimetype(self._dirname):
                content_file += file_content()

        self._data += content_file + "\n"

    def get_ignore_files(self) -> Set[str]:
        ret = set(self.ignore_files)
        if self.file_order:
            ret.add(self.file_order)
        return ret

    def get_order_files(self) -> List[str]:
        if self._dirname == "":
            print("Attribut _dirname non initialisé, méthode .load() activée ?")
            return []

        order_files = os.listdir(self._dirname)
        if self.file_order in order_files:
            with open(os.path.join(self._dirname, self.file_order), "rt") as file_order:
                order_files = file_order.read().splitlines()

        return order_files

    @staticmethod
    def file_has_yaml_mimetype(path: str) -> bool:
        # Attention: le Yaml n'a pas (encore ?) de mimetype officiel
        typ, encoding = guess_type(path)
        return encoding is None and typ in (None, "text/yaml", "application/x-yaml")


class YamlManager:
    is_first = False
    reader_cls = YamlReader
    output_directory = "db"
    input_directory = "patchs"
    _data = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def load(self, *paths) -> None:
        file_content = ""
        reader = self.reader_cls()
        for path in paths:
            patch_path = self.input_directory + "/" + path
            if not os.path.exists(patch_path):
                print(f"{patch_path} not found.")
                continue

            reader.load(patch_path)
            reader.convert()
            file_content += reader.data

        data = Dyct(yaml.safe_load(file_content), is_first=self.is_first)
        data.convert()
        self._data = data

    @property
    def data(self) -> Dyct:
        return self._data

    @dump_file
    def dump_json(self, filename, **kwargs) -> None:
        with open(self.output_basename(filename), "w") as file:
            json.dump(self.data, file, **kwargs)

    @dump_file
    def dump_yaml(self, filename, **kwargs) -> None:
        with open(self.output_basename(filename), "w") as file:
            # hack pour convertir l'objet en dictionnaire
            yaml.dump(
                json.loads(json.dumps(self.data)),
                file,
                **kwargs,
            )

    def output_basename(self, filename: str) -> str:
        return os.path.join(BASE_DIR, self.output_directory, filename)
