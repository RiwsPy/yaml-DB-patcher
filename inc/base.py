from yaml import safe_load
from json import dump
import os
from pathlib import Path
from .data_dict import Data_dict

BASE_DIR = Path(__file__).resolve().parent.parent


class YamlReader:
    inc_string = "£"
    path_string = "$"

    def __init__(self, path="", is_first=False):
        self.is_first = is_first
        self._dirname = os.path.join(BASE_DIR, os.path.dirname(path))
        self._basename = os.path.basename(path)

        if not os.path.exists(path):
            print(f"{path} not found.")
            raise FileNotFoundError

    @property
    def data(self) -> Data_dict:
        file_content = self.read()
        file_content = self.convert_inc_string(file_content, self.inc_string)
        file_content = self.convert_path_to_absolute(file_content, self.path_string)

        ret = Data_dict(is_first=self.is_first, **safe_load(file_content))
        ret.key_disaggregation()
        ret.extends()
        return ret

    @property
    def abspath(self) -> str:
        """
        Renvoie le chemin absolu du fichier
        """
        return os.path.join(self._dirname, self._basename)

    @property
    def patchpath(self) -> str:
        return os.path.basename(os.path.abspath(self._dirname))

    def read(self) -> str:
        read_file = ""
        if os.path.isdir(self.abspath):  # repository
            for file in os.listdir(self._dirname):
                with open(os.path.join(self._dirname, file), "r") as file_content:
                    read_file += file_content.read()
        else:  # file
            with open(self.abspath, "r") as file_content:
                read_file += file_content.read()

        return read_file

    @staticmethod
    def convert_inc_string(file_content: str, inc_string: str) -> str:
        """
        Permet d'unicifier un attribut en remplacant une chaîne de caractère par un identifiant sans avoir besoin de connaître sa valeur.
        Notamment utilisé par les 'fix'.
        """
        splited_str = file_content.split(inc_string)
        ret = ""
        # ~dynamic join
        for index, txt in enumerate(splited_str[:-1]):
            ret = ret + txt + str(index).zfill(8)
        return ret + splited_str[-1]

    def convert_path_to_absolute(self, file_content: str, path_string: str) -> str:
        return file_content.replace(path_string, f"{self.patchpath}.")

    def dump(self, dirname="", force=False) -> None:
        if dirname == "":
            filename = self._basename.rpartition(".")[0] + ".json"
            dirname = os.path.join(self._dirname, filename)

        if force is False and os.path.exists(dirname):
            print(f"Echec. {dirname} pré-existant.")
            return

        with open(dirname, "w") as file:
            dump(self.data, file, ensure_ascii=False, indent=1)
