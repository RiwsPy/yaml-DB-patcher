from typing import Any


class Data_dict(dict):
    _first_instance = None

    def __new__(cls, *args, is_first=False, **kwargs):
        obj_id = super().__new__(cls, *args, **kwargs)
        if is_first or cls._first_instance is None:
            cls._first_instance = obj_id
        return obj_id

    # captation de l'attribut is_first
    def __init__(self, *args, is_first=False, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item: str) -> Any:
        # suit les chemins x.y comme s'il s'agissait de {"x": {"y": object}}
        if "." not in item:
            return super().__getitem__(item)

        sub_dict = self
        for key in item.split("."):
            try:
                sub_dict = sub_dict[key]
            except KeyError:
                return {}
        return sub_dict

    def extends(self) -> None:
        for k, v in self.items():
            if not isinstance(v, dict):
                continue

            if "<" in v:
                value_expended = self.__class__()
                for key, value in v.items():
                    if key != "<":
                        value_expended[key] = value
                        continue

                    # héritage multiple <: cls1 cls2 cls3
                    force_break = False
                    for entity in value.split(" "):
                        value_expansion = self._first_instance[entity]
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

    def key_disaggregation(self, split_string: str = ".") -> None:
        """
        >self.data = {'cre.PLAYER': {'name': 'player_name', 'con': 1}}
        >self.key_disaggregation()
        >self.data
        {'cre': {'PLAYER': {'name': 'player_name', 'con': 1}}}
        """
        structured_dict = self.__class__()
        for k, v in self.items():
            sub_dict = structured_dict
            splited_keys = k.split(split_string)
            for splited_key in splited_keys[:-1]:
                if splited_key not in sub_dict:
                    sub_dict[splited_key] = {}
                sub_dict = sub_dict[splited_key]

            if isinstance(v, dict):
                v = self.__class__(v)
                v.key_disaggregation()
            sub_dict[splited_keys[-1]] = v # dernier élément

        self.clear()
        self.update(structured_dict)
