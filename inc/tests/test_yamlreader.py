from ..base import YamlReader
import pytest
from pathlib import Path
import os
from ..data_dict import Data_dict

BASE_DIR = Path(__file__).resolve().parent


def test_abspath():
    cls = YamlReader(__file__)
    assert cls.abspath == os.path.abspath(__file__)


def test_patchpath():
    cls = YamlReader(__file__)
    assert cls.patchpath == os.path.basename(os.path.dirname(__file__))


def test_read_ok():
    cls = YamlReader(os.path.join(BASE_DIR, "tiny.txt"))
    assert cls.read() == "ok"


def test_read_fail():
    with pytest.raises(FileNotFoundError):
        YamlReader(os.path.join(BASE_DIR, "lo.fail"))


def test_convert_inc_string():
    cls = YamlReader(__file__)
    ret = cls.convert_inc_string(
        "test" + cls.inc_string + "test" + cls.inc_string + "a", cls.inc_string
    )
    assert ret == "test00000000test00000001a"


def test_convert_path_to_absolute():
    cls = YamlReader(os.path.join(BASE_DIR, "db_test.yaml"), is_first=True)
    assert (
        cls.convert_path_to_absolute(cls.path_string, cls.path_string)
        == os.path.basename(os.path.dirname(__file__)) + "."
    )

    assert cls.data["tests"].get("0") == "hum!"


def test_key_disaggregation():
    data = Data_dict(**{"cre.PLAYER": {"name": "player_name", "con": 1}})
    data.key_disaggregation()
    assert data == {"cre": {"PLAYER": {"name": "player_name", "con": 1}}}


def test_extends():
    cls = YamlReader(os.path.join(BASE_DIR, "db_test.yaml"), is_first=True)
    data = cls.data
    assert data["tests.INANIMATE.color"] == data["tests.0"]

    assert data["tests.ITEM.new_attr"] == "test"
    assert data["tests.ITEM.color"] == "hum!"

    # mult-herit
    assert data["tests.ITEM.char"] == "1"
