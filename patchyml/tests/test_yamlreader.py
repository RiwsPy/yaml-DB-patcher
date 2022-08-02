import pytest
import os


def test_abspath(reader):
    reader.load(__file__)
    assert reader.abspath == os.path.abspath(__file__)


def test_patchpath(reader):
    reader.load(__file__)
    assert reader.patchpath == os.path.basename(os.path.dirname(__file__))


def test_read_fail(reader, base_dir):
    with pytest.raises(FileNotFoundError):
        reader.load(os.path.join(base_dir, "lo.fail"))
