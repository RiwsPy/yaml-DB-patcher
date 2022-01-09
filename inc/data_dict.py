from typing import Any


class Data_dict(dict):
    _first_instance = None

    def __new__(cls, *args, is_first=False, **kwargs):
        obj_id = super().__new__(cls, *args, **kwargs)
        if is_first:
            cls._first_instance = obj_id
        return obj_id

    def __getitem__(self, item: str) -> Any:
        if '.' not in item:
            return super().__getitem__(item)

        sub_dict = self
        for key in item.split('.'):
            try:
                sub_dict = sub_dict[key]
            except KeyError:
                return {}
        return sub_dict

    def expend_value(self) -> None:
        for k, v in self.items():
            if isinstance(v, dict):
                if '<' in v:
                    value_expended = self.__class__()
                    for key, value in v.items():
                        if key != '<':
                            value_expended[key] = value
                        else:
                            force_break = False
                            # héritages multiples
                            for splited_value in value.split():
                                value_expansion = self._first_instance[splited_value]
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
                    value_expended.expend_value()

                self[k] = value_expended

        for k, v in self.items():
            if isinstance(v, dict):
                dict_convert = self.__class__(v)
                dict_convert.expend_value()
                self[k] = dict_convert

    def key_disaggregation(self, split_string: str = '.') -> None:
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
            for index, splited_key in enumerate(splited_keys):
                if index >= len(splited_keys)-1:
                    sub_dict[splited_key] = v
                else:
                    if splited_key not in sub_dict:
                        sub_dict[splited_key] = {}
                    sub_dict = sub_dict[splited_key]
        self.clear()
        self.update(structured_dict)
