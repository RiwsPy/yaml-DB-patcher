from ..patchyml import YamlReader, YamlManager
import pytest
from pathlib import Path
import os
from ..db import Dyct

BASE_DIR = Path(__file__).resolve().parent


def test_abspath():
    cls = YamlReader()
    cls.load(__file__)
    assert cls.abspath == os.path.abspath(__file__)


def test_patchpath():
    cls = YamlReader()
    cls.load(__file__)
    assert cls.patchpath == os.path.basename(os.path.dirname(__file__))


def test_read_fail():
    cls = YamlReader()
    with pytest.raises(FileNotFoundError):
        cls.load(os.path.join(BASE_DIR, "lo.fail"))


def test_key_disaggregation():
    data = Dyct(**{"cre.PLAYER": {"name": "player_name", "con": 1}})
    data.key_disaggregation()
    assert data == {"cre": {"PLAYER": {"name": "player_name", "con": 1}}}

    data = Dyct(**{"test": {"name.first": "firstname", "name.nickname": "nickname"}})
    data.key_disaggregation()
    assert data == {"test": {"name": {"first": "firstname", "nickname": "nickname"}}}

    data = Dyct(**{"test": {"name": "Roger"}, "test.hp": 1})
    data.key_disaggregation()
    assert data == {"test": {"name": "Roger", "hp": 1}}

    data = Dyct(**{"test": {"name": "Roger"}, "test.hp.max": 1})
    data.key_disaggregation()
    assert data == {"test": {"name": "Roger", "hp": {"max": 1}}}

    data = Dyct(**{"fix.test": 1})
    data.key_disaggregation()
    assert data == {"fix": {"test": 1}}


def test_extends():
    cls = YamlManager(is_first=True)
    cls.load(os.path.join(BASE_DIR, "db_test.yaml"))
    data = cls.data
    assert data["tests.INANIMATE.color"] == data["tests.0"]

    assert data["tests.ITEM.new_attr"] == "test"
    assert data["tests.ITEM.color"] == "hum!"

    # mult-herit
    assert data["tests.ITEM.char"] == "1"


def test_resolve_links():
    cls = Dyct()
    cls.update({"0": "value0", "1": "<<0>>1"})
    cls.resolve_links()
    expected_value = {"0": "value0", "1": "value01"}
    assert cls == expected_value

    cls.clear()
    cls.update({"person": {"name": "Loulou"}, "other": {"name": "<<person.name>>"}})
    cls.resolve_links()
    expected_value = {"person": {"name": "Loulou"}, "other": {"name": "Loulou"}}
    assert cls == expected_value
