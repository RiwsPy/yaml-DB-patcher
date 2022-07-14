import operator
import re
from typing import Any
import json

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


class Data_dict(dict):
    _first_instance = None
    regex_links_in_str = re.compile(r"(<<([\w\. ]+)>>)")
    heritage_string = "<"
    attr_split_string = "."
    fix_string = "fix"

    def __new__(cls, *args, is_first: bool = False, **kwargs):
        obj_id = super().__new__(cls, *args, **kwargs)
        if is_first or cls._first_instance is None:
            cls._first_instance = obj_id
        return obj_id

    # captation de l'attribut is_first
    def __init__(self, *args, is_first: bool = None, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Any:
        # suit les chemins x.y comme s'il s'agissait de {"x": {"y": object}}
        if self.attr_split_string not in key:
            return super().__getitem__(key)

        sub_dict = self
        for attr in key.split(self.attr_split_string):
            sub_dict = sub_dict[attr]
        return sub_dict

    def get(self, key: str, default=None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            if default is None:
                return {}
        return default

    def extends(self) -> None:
        # applique les différents héritages
        for k, v in self.items():
            if not isinstance(v, dict):
                continue

            if self.heritage_string in v:
                value_expended = self.__class__()
                for key, value in v.items():
                    if key != self.heritage_string:
                        value_expended[key] = value
                        continue

                    # héritage multiple <: cls1 cls2 cls3
                    force_break = False
                    for entity in value.split(" "):
                        value_expansion = self._first_instance.get(entity) or {}
                        if isinstance(value_expansion, dict):
                            value_expended.update(value_expansion)
                        else:
                            value_expended = value_expansion
                            force_break = True
                            break
                    if force_break:
                        break
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
        >self.data = {'cre.PLAYER': {'name': 'player_name', 'con': 1}}
        >self.key_disaggregation()
        >self.data
        {'cre': {'PLAYER': {'name': 'player_name', 'con': 1}}}
        """
        structured_dict = self.__class__()
        fix_str = self.fix_string + self.attr_split_string
        for k, v in self.items():
            sub_dict = structured_dict
            if isinstance(k, str):
                if k.startswith(fix_str):
                    key_1, _, key_2 = k.partition(self.attr_split_string)
                    if key_1 not in sub_dict:
                        sub_dict[key_1] = dict()
                    sub_dict[key_1][key_2] = v
                    continue
                splited_keys = k.split(self.attr_split_string)
            else:
                splited_keys = [k]
            for splited_key in splited_keys[:-1]:
                if splited_key not in sub_dict:
                    sub_dict[splited_key] = {}
                sub_dict = sub_dict[splited_key]

            if isinstance(v, dict):
                v = self.__class__(v)
                v.key_disaggregation()
            sub_dict[splited_keys[-1]] = v  # dernier élément

        self.clear()
        self.update(structured_dict)

    def fix_me(self) -> None:
        """
        self["OBJECT"]["fix"]["fix_id"]["fix_content"]["fix_key|method"] = fix_value
        """
        for key, value in self.copy().items():
            if not isinstance(value, dict) or self.fix_string not in value:
                continue

            # tri des fixs en fonction du pk
            for fix_id, fix_content in sorted(
                value[self.fix_string].items(), key=operator.itemgetter(0)
            ):
                if isinstance(fix_content, dict):
                    for fix_key_with_attrs, fix_value in fix_content.items():
                        if "|" not in fix_key_with_attrs:
                            fix_key = fix_key_with_attrs
                        else:
                            splited_key = fix_key_with_attrs.split("|")
                            fix_key = splited_key[0]
                            methods = splited_key[1:]
                            try:
                                content = value[fix_key].copy()
                            except AttributeError:
                                content = value[fix_key]
                            except TypeError:
                                continue

                            for method in methods:
                                fix_value = self.apply_method(
                                    content, fix_value, method
                                )
                        value[fix_key] = fix_value
                else:
                    # retrait de la valeur £ dans fix_id
                    fix_id = fix_id.partition(self.attr_split_string)[2]
                    value[fix_id] = fix_content

            del value[self.fix_string]
            value = self.__class__(value)
            value.key_disaggregation()
            # update_soft(self[key], value)
            self[key] = value

    def resolve_links(self) -> None:
        def resolve_links_in_str(instance, text: str) -> str:
            dialogs = re.split(instance.regex_links_in_str, text)
            for index, content_id in enumerate(dialogs[2::3]):
                content_id = content_id.strip()
                new_str = resolve_links_in_str(instance, instance[content_id]) or ""
                instance[content_id] = new_str
                dialogs[index * 3 + 1] = ""
                dialogs[index * 3 + 2] = new_str
            return "".join(dialogs)

        txt = resolve_links_in_str(self, json.dumps(self))
        self.clear()
        self.update(json.loads(txt))

    @staticmethod
    def apply_method(source: Any, value: Any, method: str) -> Any:
        try:
            value = value.copy()
        except AttributeError:
            pass

        if method in operator_to_method:
            try:
                return getattr(source, operator_to_method[method])(value)
            except AttributeError:
                print(
                    f"fix non appliqué: {type(source)} have no method for operator {method}"
                )
            except TypeError:
                print(f"fix non appliqué: type incorrect {type(source)}, {type(value)}")
        return value
