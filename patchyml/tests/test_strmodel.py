def test_output_type(strModel):
    txt = (strModel + "a").upper()

    excepted_value = "A"
    assert txt == excepted_value

    expected_type = type(strModel)
    assert type(txt) is expected_type


def test_output_type2(strModel):
    txt = strModel + "a"
    txt += "c"
    assert type(txt) is type(strModel)


def test_replace_inc_string(strModel):
    inc_string = strModel.inc_string
    txt = strModel + "test" + inc_string + "test" + inc_string + "a"
    expected_value = "test00000000test00000001a"
    assert txt.replace_inc_string() == expected_value


def test_replace_path_to_absolute(strModel):
    txt = strModel + f"{strModel.path_string}loulou"
    expected_value = "_base.loulou"

    assert txt.replace_path_string("_base") == expected_value


def test_replace_fix_string(strModel, dyct):
    txt = strModel + f"test{strModel.fix_string}test"
    expected_value = f"test{dyct.fix_string}.00000000test"
    assert txt.replace_fix_string() == expected_value
