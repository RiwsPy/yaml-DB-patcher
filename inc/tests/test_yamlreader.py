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
    cls = YamlReader(os.path.join(BASE_DIR, 'tiny.txt'))
    assert cls.read() == 'ok'


def test_read_fail():
    with pytest.raises(FileNotFoundError):
        cls = YamlReader(os.path.join(BASE_DIR, 'lo.fail'))


def test_convert_inc_string():
    cls = YamlReader(__file__)
    ret = cls.convert_inc_string('test' + cls.inc_string + 'test' + cls.inc_string + 'a')
    assert ret == 'test00000000test00000001a'


def test_convert_path_to_absolute():
    cls = YamlReader(os.path.join(BASE_DIR, 'db_test.yaml'))
    assert cls.convert_path_to_absolute(cls.absolute_string) == os.path.basename(os.path.dirname(__file__)) + '.'

    cls.read_sub_save()
    assert cls.data['tests'].get('0') == 'hum!'


def test_key_disaggregation():
    cls = YamlReader(os.path.join(BASE_DIR, 'db_test.yaml'))
    cls.data = Data_dict(**{'cre.PLAYER': {'name': 'player_name', 'con': 1}})
    cls.data.key_disaggregation()
    assert cls.data == {'cre': {'PLAYER': {'name': 'player_name', 'con': 1}}}


def test_expend_value():
    cls = YamlReader(os.path.join(BASE_DIR, 'db_test.yaml'))
    cls.read_sub_save()
    cls.data.expend_value()
    assert cls.data['tests.INANIMATE.color'] == cls.data['tests.0']

    assert cls.data['tests.ITEM.new_attr'] == 'test'
    assert cls.data['tests.ITEM.color'] == 'hum!'

    # mult-herit
    assert cls.data['tests.ITEM.char'] == '1'
