import operator
import re
from typing import Any
import json
from .utils import Breaker

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


class Dyct(dict):
    _first_instance = None
    regex_links_in_str = re.compile(r"(<<([\w\. ]+)>>)")
    heritage_string = "<"
    attr_split_string = "."
    fix_string = "__fixs"

    def __new__(cls, *args, **kwargs):
        obj_id = super().__new__(cls, *args, **kwargs)
        if kwargs.pop("is_first", False) or cls._first_instance is None:
            cls._first_instance = obj_id
        return obj_id

    # captation de l'attribut is_first
    def __init__(self, *args, is_first=False, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Any:
        # self["a.b"] <==> self["a"]["b"]
        if self.attr_split_string not in key:
            return super().__getitem__(key)

        sub_dict = self
        for attr in key.split(self.attr_split_string):
            sub_dict = sub_dict[attr]
        return sub_dict

    def __setitem__(self, key: str, value) -> None:
        """
        self["a.b"] = 2 <==> {"a": {"b": 2}}
        """
        # TODO: pas de type immutable accepté comme clé ?
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

            if self.heritage_string in v:
                try:
                    value_expended = self.__class__()
                    for key, value in v.items():
                        if key != self.heritage_string:
                            value_expended[key] = value
                            continue

                        # héritage multiple <: cls1 cls2 cls3
                        for entity in value.split(" "):
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

        for k, v in self.items():
            if isinstance(v, dict):
                dict_convert = self.__class__(v)
                dict_convert.extends()
                self[k] = dict_convert

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
        self["fixs"]["fix_id"]["fix_keys|method?"] = fix_value
        """
        fixs = self.get(self.fix_string)
        if not isinstance(fixs, dict):
            return

        for fix_id, fix_contents in sorted(fixs.items(), key=operator.itemgetter(0)):
            if isinstance(fix_contents, dict):
                self.update_values_with_operator(fix_contents)

    def resolve_links(self) -> None:
        def resolve_links_in_str(text: str) -> str:
            dialogs = re.split(self.regex_links_in_str, text)
            for index, content_id in enumerate(dialogs[2::3]):
                content_id = content_id.strip()
                content_value = self[content_id]
                if isinstance(content_value, str):
                    content_value = resolve_links_in_str(content_value) or ""
                    self[content_id] = content_value
                else:
                    # TODO: problème si type !str, mais dans ce cas, plus possible de faire un join
                    pass
                dialogs[index * 3 + 1] = ""
                dialogs[index * 3 + 2] = content_value
            return "".join(dialogs)

        txt = resolve_links_in_str(json.dumps(self))
        self.clear()
        self.update(json.loads(txt))

    @staticmethod
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
        return value

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
                    v = self.apply_operator(value_origin, v, ope)
                self[k] = v
