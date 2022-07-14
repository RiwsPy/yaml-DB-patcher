from ..base import StrModel


def test_output_type():
    txt = StrModel("a").upper()

    excepted_value = "A"
    assert txt == excepted_value

    expected_type = StrModel
    assert type(txt) is expected_type


def test_convert_inc_string():
    inc_string = StrModel.inc_string
    txt = StrModel("test" + inc_string + "test" + inc_string + "a")
    expected_value = "test00000000test00000001a"
    assert txt.replace_inc_string() == expected_value


def test_convert_path_to_absolute():
    path_string = StrModel.path_string
    txt = StrModel(f"{path_string}loulou")
    expected_value = "_base.loulou"

    assert txt.replace_path_string("_base") == expected_value
