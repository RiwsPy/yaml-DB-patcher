from yaml import safe_load
from json import dump
import os
from pathlib import Path
from .data_dict import Data_dict
from utils import ForceReturnOfMyClass

BASE_DIR = Path(__file__).resolve().parent.parent


class StrModel(str, metaclass=ForceReturnOfMyClass):
    inc_string = "£"
    path_string = "$"

    def convert_inc_string(self) -> "StrModel":
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

    def __init__(self, path: str):
        self._dirname = os.path.join(BASE_DIR, os.path.dirname(path))
        self._basename = os.path.basename(path)

    @property
    def data(self) -> str:
        return self.read().convert_inc_string().replace_path_string(self.patchpath)

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
        """
        Lit le fichier de l'instance ou tous les fichiers présents dans le dossier, les concatènent et les renvoient
        A ce stade, le contenu n'est pas encore interprété

        Attention: actuellement, le Yaml n'a pas (encore ?) de mimetype officiel
        """
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

        return self.str_model(read_file)

    def get_ignore_files(self) -> set:
        ret = self.ignore_files
        if self.file_order:
            ret.add(self.file_order)
        return ret


class YamlManager:
    is_first = False
    reader_cls = YamlReader
    db_directory = "db"
    filename = "default.json"

    def __init__(self, *paths):
        self.paths = paths

    # TODO: gestion de l'ordre dans les dossiers
    def read(self) -> str:
        ret = ""
        for path in self.paths:
            if not os.path.exists(path):
                print(f"{path} not found.")
            else:
                ret += self.reader_cls(path).data
        return ret

    @property
    def data(self) -> Data_dict:
        file_content = self.read()
        ret = Data_dict(is_first=self.is_first, **safe_load(file_content))
        ret.key_disaggregation()
        ret.extends()
        ret.fix_me()
        ret.resolve_links()

        return ret

    def dump(self, force: bool = True, **kwargs) -> None:
        """
        :param force: si False, renvoie FileExistsError si le ficher est pré-existant
        """
        dirname = os.path.join(BASE_DIR, self.db_directory, self.filename)
        if force is False and os.path.exists(dirname):
            print(f"Échec. '{self.filename}' pré-existant.")
            raise FileExistsError

        with open(dirname, "w") as file:
            dump(self.data, file, **kwargs)

        print(f"Écriture dans {dirname} terminée.")
