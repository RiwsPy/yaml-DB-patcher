import re
import operator
from typing import Any
from copy import deepcopy

from .utils import OutputOfMyClass, Breaker
from .decorators import key_is_str


class StrModel(str, metaclass=OutputOfMyClass):
    inc_string = "£"
    fix_string = "F" + inc_string
    path_string = "$"
    regex_links = re.compile(r"(<<([\w\. ]+)>>)")
    regex_extension = re.compile(r".[yY][aA]?[mM][lL]$")

    def replace_links(self, dyct) -> Any:
        ret = self
        case_realized = set()
        for groups in self.regex_links.finditer(self):
            # groups.group(0) contient l'intégralité du lien avec les < >
            # groups.group(2) ne contient que le lien à proprement parlé
            strref_id = groups.group(2).strip(" ")
            if (
                strref_id in case_realized
            ):  # déjà écrasé par le ret.replace(groups.group(0), new_v)
                continue
            case_realized.add(strref_id)
            new_v = dyct.get(strref_id, "")  # "" par défaut

            if new_v and isinstance(new_v, str):
                # application de replace_links sur le résultat trouvé
                new_v = self.__class__(new_v).replace_links(dyct)
                # sauvegarde dans dyct pour éviter de répéter la procédure
                dyct[strref_id] = new_v
            elif self.regex_links.fullmatch(self):
                # renvoie un autre type que str
                ret = new_v
                continue
            else:
                # converti en str pour être intégré au reste du texte
                new_v = str(new_v)

            ret = ret.replace(groups.group(0), new_v)

        # 6: résolution des liens imbriqués
        if ret is not self and isinstance(ret, self.__class__):
            ret = ret.replace_links(dyct)

        return ret

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
        def remove_extension(text: str) -> str:
            return self.regex_extension.sub("", text)

        return self.replace(self.path_string, f"{remove_extension(patchpath)}.")


class Dyct(dict):
    _first_instance = None
    heritage_string = "<"
    attr_split_string = "."
    fix_string = "__fixs"
    regex_inherit_split = re.compile(" +")

    def __new__(cls, *args, **kwargs):
        obj_id = super().__new__(cls, *args, **kwargs)
        if kwargs.pop("is_first", False) or cls._first_instance is None:
            cls._first_instance = obj_id
        return obj_id

    # captation de l'attribut is_first
    def __init__(self, *args, is_first=False, **kwargs):
        super().__init__(*args, **kwargs)

    @key_is_str
    def __getitem__(self, key: str) -> Any:
        # self["a.b"] <==> self["a"]["b"]
        if self.attr_split_string not in key:
            return super().__getitem__(key)

        sub_dict = self
        for attr in key.split(self.attr_split_string):
            sub_dict = sub_dict[attr]
        return sub_dict

    @key_is_str
    def __setitem__(self, key: str, value: Any) -> None:
        """
        self["a.b"] = 2 <==> {"a": {"b": 2}}
        """
        sub_dict = self
        attrs = key.split(self.attr_split_string)

        for attr in attrs[:-1]:
            sub_dict = sub_dict.setdefault(attr, self.__class__())
        else:
            if sub_dict is self:  # ~ len(attrs) == 1
                # update_values ??
                super().__setitem__(key, value)
            else:
                sub_dict[attrs[-1]] = value

    def get(self, key: str, default=None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def convert(self) -> None:
        self.key_disaggregation()
        self.extends()
        if self is self._first_instance:
            self.fix_me()
            try:
                del self[self.fix_string]
            except KeyError:
                pass
        self.resolve_links()

    def extends(self) -> None:
        # applique les différents héritages
        for k, v in self.items():
            if not isinstance(v, dict):
                continue

            value_expended = None
            if self.heritage_string in v:
                try:
                    value_expended = self.__class__()
                    for key, value in v.items():
                        # ajout des clés présentes n'étant pas le caractère d'héritage
                        if key != self.heritage_string:
                            value_expended[key] = value
                            continue

                        # héritage multiple <: cls1 cls2 cls3
                        inherited_entities = self.regex_inherit_split.split(value)
                        for index, entity in enumerate(inherited_entities):
                            # on passe les héritages vides (espaces)
                            # seule la dernière instance des héritages identiques est prise en compte
                            if not entity or entity in inherited_entities[index+1:]:
                                continue

                            value_expansion = self._first_instance.get(entity, dict())
                            if isinstance(value_expansion, dict):
                                value_expended.update(value_expansion)
                            else:
                                value_expended = value_expansion
                                raise Breaker
                except Breaker:
                    pass
            else:
                value_expended = self.__class__(v)
                value_expended.extends()

            self[k] = value_expended

        """
        for k, v in self.items():
            if isinstance(v, dict):
                dict_convert = self.__class__(v)
                dict_convert.extends()
                self[k] = dict_convert
        """

    def key_disaggregation(self) -> None:
        """
        >self._data = {'cre.PLAYER': {'name': 'player_name'}}
        >self.key_disaggregation()
        >self.data
        {'cre': {'PLAYER': {'name': 'player_name'}}}
        """
        structured_dict = self.__class__()
        for k, v in self.items():
            if isinstance(v, dict):
                v = self.__class__(v)
                v.key_disaggregation()
            structured_dict[k] = v

        self.clear()
        self.update(structured_dict)

    def fix_me(self) -> None:
        """
        self["__fixs"]["fix_id"]["fix_keys|method?"] = fix_value
        """
        fixs = self.get(self.fix_string)
        if not isinstance(fixs, dict):
            return

        # tri sur pk croissant
        for fix_id, fix_contents in sorted(fixs.items(), key=operator.itemgetter(0)):
            if isinstance(fix_contents, dict):
                self.update_values_with_operator(fix_contents)

    def resolve_links(self) -> None:
        """
        Remplace les << X >> par la valeur correspondante dans l'instance principale
        """
        for k, v in self.items():
            """
            # #8 incomplet
            # remplacement des keys dans un premier temps
            # for k, v in self.copy().items():
            new_k = StrModel(k).replace_links(self._first_instance)
            if k != new_k:
                new_d = Dyct({k: v})
                new_d.key_disaggregation()
                self[new_k] = v
                del self[k]
                k = new_k
            """

            # remplacement des values dans un second temps
            if isinstance(v, str):
                self[k] = StrModel(v).replace_links(self._first_instance)
            elif isinstance(v, dict):
                # Provisoire pour issue #5
                if isinstance(v, Dyct):
                    v.resolve_links()
                else:
                    v = Dyct(v)
                    v.resolve_links()
                    self[k] = v

    def update_values_with_operator(self, other: dict) -> None:
        """
        Similaire à dict.update(other_dict)
        Excepté : seules les values sont affectées
        Applique une méthode supplémentaire sur la clé finale pour déterminer si une méthode doit être appliquée sur value
        """
        if not isinstance(other, dict):
            return

        for k, v in other.items():
            if isinstance(v, dict) and isinstance(self.get(k), dict):
                self[k].update_values_with_operator(other[k])
            else:
                key_without_ope, _, ope = k.rpartition("|")
                if key_without_ope and ope:
                    k = key_without_ope
                    # valeur par défaut = valeur par défaut du type(v)
                    value_origin = self.get(k, type(v)())
                    v = apply_operator(value_origin, v, ope)
                self[k] = v


operator_to_method = {
    "+": "__add__",
    "-": "__sub__",
    "/": "__truediv__",
    "*": "__mul__",
    "&": "__and__",
    ">=": "__ge__",
    ">": "__gt__",
    "<=": "__le__",
    "<": "__lt__",
    "%": "__mod__",
    "|": "__or__",
    "^": "__xor__",
    "!=": "__ne__",
    "==": "__eq__",
    "//": "__floordiv__",
    "~": "__invert__",
    "<<": "__lshift__",
    ">>": "__rshift__",
    "**": "__pow__",
}


def apply_operator(source: Any, value: Any, ope: str) -> Any:
    try:
        value = value.copy()
    except AttributeError:
        pass

    method = operator_to_method.get(ope)
    if method:
        try:
            return getattr(source, method)(value)
        except AttributeError:
            print(
                f"fix non appliqué: {type(source)} pas de méthode pour l'opérateur {ope}"
            )
        except TypeError:
            print(f"fix non appliqué: type incorrect {type(source)}, {type(value)}")
        except:
            print(f"Erreur inconnue: {source} {ope} {value}")
    return source if source else value
