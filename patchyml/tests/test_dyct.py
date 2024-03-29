from patchyml.db import apply_operator


def test_update_level1(dyct):
    dyct.update({"level1": 1})
    assert dyct == {"level1": 1}


def test_update_level2(dyct):
    dyct.update({"level1": {"level2": 1}})
    assert dyct == {"level1": {"level2": 1}}
    assert isinstance(dyct["level1"], type(dyct))


def test_key_disaggregation_level1(dyct):
    dyct.update({"cre.PLAYER": {"name": "player_name", "con": 1}})
    dyct.key_disaggregation()
    assert dyct == {"cre": {"PLAYER": {"name": "player_name", "con": 1}}}


def test_key_disaggregation_level2(dyct):
    dyct.update({"test": {"name.first": "firstname", "name.nickname": "nickname"}})
    dyct.key_disaggregation()
    assert dyct == {"test": {"name": {"first": "firstname", "nickname": "nickname"}}}


def test_key_disaggregation_autoupdate(dyct):
    dyct.update({"test": {"name": "Roger"}, "test.hp": 1})
    dyct.key_disaggregation()
    assert dyct == {"test": {"name": "Roger", "hp": 1}}


def test_key_disaggregation_autoupdate_level2(dyct):
    dyct.update({"test": {"name": "Roger"}, "test.hp.max": 1})
    dyct.key_disaggregation()
    assert dyct == {"test": {"name": "Roger", "hp": {"max": 1}}}


def test_extends_level1(dyct):
    dyct.update({"source": {"name": "test"}, "1": {"<": "source"}})
    dyct.extends()
    assert dyct["source"] == dyct["1"]


def test_extends_level2(dyct):
    dyct.update({"source": {"name": "test"}, "1": {"name": {"<": "source.name"}}})
    dyct.extends()
    assert dyct["source"] == dyct["1"]


def test_extends_empty(dyct):
    dyct.update({"": "test", "1": {"name": {"<": "   "}}})
    dyct.extends()
    assert dyct["1"] == {"name": {}}


def test_resolve_links_level1(dyct):
    dyct.update({"0": "value0", "1": "<<0>>1"})
    dyct.resolve_links()
    expected_value = {"0": "value0", "1": "value01"}
    assert dyct == expected_value


def test_resolve_links_level2(dyct):
    dyct.update({"person": {"name": "Loulou"}, "other": {"name": "<<person.name>>"}})
    dyct.resolve_links()
    expected_value = {"person": {"name": "Loulou"}, "other": {"name": "Loulou"}}
    assert dyct == expected_value


def test_resolve_links_double(dyct):
    dyct.update(
        {
            "person": {"name": "Loulou"},
            "other": {"name": "<<person.name>><<person.name>>"},
        }
    )
    dyct.resolve_links()
    expected_value = {"name": "LoulouLoulou"}
    assert dyct["other"] == expected_value


def test_resolve_links_imbr(dyct):
    dyct.update(
        {
            "person": {"name": "Loulou"},
            "other": {"hp": "<<<<person.name>>.hp>>"},
            "Loulou": {"hp": 2},
        }
    )
    dyct.resolve_links()
    expected_value = {"hp": 2}
    assert dyct["other"] == expected_value


def test_set_dict(dyct):
    dyct["test"] = {"ho": 1}
    assert type(dyct["test"]) == type(dyct)


def test_set_dict_level2(dyct):
    dyct["test.2"] = {"ho": 1}
    assert type(dyct["test"]["2"]) == type(dyct)


# 5
def test_dyct_update_is_dyct(dyct):
    dyct.update({"test": {"1": "2"}})
    assert type(dyct["test"]) is type(dyct)


"""
# Non implanté
def test_resolve_links_in_key(dyct):
    dyct.update({"0": 0, "01": 1, "0<<01>>2": 2})
    dyct.resolve_links()
    expected_value = {"0": 0, "01": 1, "012": 2}
    assert dyct == expected_value


def test_resolve_links_in_key_imbr(dyct):
    dyct.update({"0": 0, "01": {"test": 1}, "0<<01.test>>2": 2})
    dyct.resolve_links()
    expected_value = {"0": 0, "01": {"test": 1}, "012": 2}
    assert dyct == expected_value
"""


def test_apply_operator():
    assert apply_operator(1, 2, "+") == 3
    assert apply_operator(12, 3, "*") == 36
    assert apply_operator(None, -1, "+") == -1
    assert apply_operator(0, 2, "/") == 0
    assert apply_operator(["SCRL01"], ["POTN01"], "+") == ["SCRL01", "POTN01"]
    assert apply_operator(["SCRL01"], "POTN01", "+") == ["SCRL01"]

    # __sub__ n'existe pas pour le type list
    # assert dyct.apply_operator(["SCRL01", "POTN01"], ["POTN01"], "-") == ["SCRL01"]
