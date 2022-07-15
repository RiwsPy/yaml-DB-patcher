from patchyml.utils import update_values


def test_update_values():
    a = {"key1": {"key2": "a_value1", "key3": "a_value2"}, "key4": 1}
    b = {"key1": {"key3": "b_value1"}}
    update_values(a, b)
    assert a == {"key1": {"key2": "a_value1", "key3": "b_value1"}, "key4": 1}

    a = {"key1": {"key2": "a_value1", "key3": "a_value2"}}
    b = {"key1": {"key3": {"key5": "b_value5"}}}
    update_values(a, b)
    assert a == {"key1": {"key2": "a_value1", "key3": {"key5": "b_value5"}}}

    a = {"key1": {"key2": "a_value1", "key3": "a_value2"}}
    b = {"key1": 1}
    update_values(a, b)
    assert a == {"key1": 1}
