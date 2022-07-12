from yaml import safe_load
from json import dump
import os
from pathlib import Path
from .data_dict import Data_dict

BASE_DIR = Path(__file__).resolve().parent.parent


class StrModel(str):
    inc_string = "£"
    path_string = "$"

    def convert_inc_string(self) -> "StrModel":
        """
        Permet d'unicifier un attribut en remplacant une chaîne de caractère par un identifiant sans avoir besoin de connaître sa valeur.
        Notamment utilisé par les 'fix'.
        """
        splited_str = self.split(self.inc_string)
        ret = ""
        # ~dynamic join
        for index, txt in enumerate(splited_str[:-1]):
            ret = ret + txt + str(index).zfill(8)

        return self.__class__(ret + splited_str[-1])

    def convert_path_string(self, patchpath: str) -> "StrModel":
        return self.__class__(self.replace(self.path_string, f"{patchpath}."))


class YamlReader:
    is_first = False
    str_model = StrModel
    db_directory = "db"

    def __init__(self, path: str):
        if not os.path.exists(path):
            print(f"{path} not found.")
            raise FileNotFoundError

        self._dirname = os.path.join(BASE_DIR, os.path.dirname(path))
        self._basename = os.path.basename(path)

    @property
    def data(self) -> Data_dict:
        file_content = (
            self.read().convert_inc_string().convert_path_string(self.patchpath)
        )

        ret = Data_dict(is_first=self.is_first, **safe_load(file_content))
        ret.key_disaggregation()
        ret.extends()
        ret.fix_me()
        ret.resolve_links()
        return ret

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

    def read(self) -> StrModel:
        read_file = ""
        if os.path.isdir(self.abspath):  # repository
            for file in os.listdir(self._dirname):
                with open(os.path.join(self._dirname, file), "r") as file_content:
                    read_file += file_content.read()
        else:  # file
            with open(self.abspath, "r") as file_content:
                read_file += file_content.read()

        return self.str_model(read_file)

    def dump(self, filename: str = "", force: bool = False) -> None:
        if filename == "":
            if self._basename:
                filename = self._basename.replace(".yaml", ".json").replace(".yml", ".json")
            else:
                filename = self.patchpath + ".json"

        if force is False and os.path.exists(filename):
            print(f"Echec. {filename} pré-existant.")
            return

        dirname = os.path.join(BASE_DIR, self.db_directory, filename)
        with open(dirname, "w") as file:
            dump(self.data, file, ensure_ascii=False, indent=1)
