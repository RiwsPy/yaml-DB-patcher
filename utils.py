def update_soft(source: dict, other: dict, *no_dict_key) -> None:
    """
    Similaire à dict.update(other_dict)
    Excepté : les clés ne sont écrasées qu'en dernier recours

    >>> a = {'key1': {"key2": "a_value1", "key3": "a_value2"}}
    >>> b = {'key1': {"key3": "b_value1"}}
    >>> update_soft(a, b)
    >>> a
    Output: {'key1': {"key2": "a_value1", "key3": "b_value1"}}
    """
    if not isinstance(source, dict) or not isinstance(other, dict):
        return

    for k, v in other.items():
        if k not in source or not isinstance(v, dict) or k in no_dict_key:
            try:
                source[k] = v.copy()
            except AttributeError:
                source[k] = v
        else:
            source_copy = source[k].copy()
            update_soft(source_copy, v, *no_dict_key)
            source[k] = source_copy
