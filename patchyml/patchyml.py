import yaml
import json
import os
from pathlib import Path
from .db import Dyct
from .utils import OutputOfMyClass

BASE_DIR = Path(__file__).resolve().parent.parent


def dump_file(func):
    def _(self, filename, *args, force=True, **kwargs):
        if force is False and os.path.exists(self.output_basename(filename)):
            raise FileExistsError(f"Échec. '{self.output_filename}' pré-existant.")

        func(self, filename, *args, **kwargs)
        print(f"Écriture dans {self.output_basename(filename)} terminée.")

    return _


class StrModel(str, metaclass=OutputOfMyClass):
    inc_string = "£"
    fix_string = "F" + inc_string
    path_string = "$"

    def replace_fix_string(self) -> "StrModel":
        splited_str = self.split(self.fix_string)
        ret = splited_str[0]
        for index, txt in enumerate(splited_str[1:]):
            ret = (
                ret
                + Dyct.fix_string
                + Dyct.attr_split_string
                + str(index).zfill(8)
                + txt
            )

        return ret

    def replace_inc_string(self) -> "StrModel":
        """
        Permet d'unicifier un attribut en remplacant une chaîne de caractère par un identifiant sans avoir besoin de connaître sa valeur.
        Notamment utilisé par les 'fix'.
        """
        splited_str = self.split(self.inc_string)
        ret = splited_str[0]
        # ~dynamic join
        for index, txt in enumerate(splited_str[1:]):
            ret = ret + str(index).zfill(8) + txt

        return ret

    def replace_path_string(self, patchpath: str) -> "StrModel":
        return self.replace(self.path_string, f"{patchpath}.")


class YamlReader:
    str_model = StrModel
    file_order = "_order.ini"
    ignore_files = set()
    _data = None

    def __init__(self, **kwargs):
        self._dirname = ""
        self._basename = ""
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def data(self) -> str:
        return self._data

    def convert(self) -> None:
        self._data = (
            self.str_model(self._data).replace_fix_string()
            # .replace_inc_string()
            .replace_path_string(self.patchpath)
        )

    @property
    def abspath(self) -> str:
        """
        Renvoie le chemin absolu du fichier ou du dossier
        """
        return os.path.join(self._dirname, self._basename)

    @property
    def patchpath(self) -> str:
        """
        Renvoie le nom du fichier ou du dossier
        """
        return os.path.basename(os.path.abspath(self._dirname))

    def load(self, path: str) -> None:
        """
        Lit le fichier de l'instance ou tous les fichiers présents dans le dossier, les concatènent et les renvoient
        A ce stade, le contenu n'est pas encore interprété

        Attention: actuellement, le Yaml n'a pas (encore ?) de mimetype officiel
        """
        self._dirname = os.path.join(BASE_DIR, os.path.dirname(path))
        self._basename = os.path.basename(path)

        read_file = ""
        if os.path.isdir(self.abspath):  # repository
            order_files = os.listdir(self._dirname)
            if self.file_order in order_files:
                with open(
                    os.path.join(self._dirname, self.file_order), "r"
                ) as file_order:
                    order_files = [line.rstrip("\n") for line in file_order.readlines()]

            for file in order_files:
                if file not in self.get_ignore_files():
                    with open(os.path.join(self._dirname, file), "r") as file_content:
                        read_file += file_content.read()
        else:  # file
            with open(self.abspath, "r") as file_content:
                read_file += file_content.read()

        self._data = read_file

    def get_ignore_files(self) -> set:
        ret = self.ignore_files
        if self.file_order:
            ret.add(self.file_order)
        return ret


class YamlManager:
    is_first = False
    reader_cls = YamlReader
    db_directory = "db"
    _data = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def load(self, *paths) -> None:
        file_content = ""
        reader = self.reader_cls()
        for path in paths:
            if not os.path.exists(path):
                print(f"{path} not found.")
            else:
                reader.load(path)
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
            yaml.dump(json.loads(json.dumps(self.data)), file, **kwargs)

    def output_basename(self, filename: str):
        return os.path.join(BASE_DIR, self.db_directory, filename)
