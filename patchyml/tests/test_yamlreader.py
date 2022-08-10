import pytest
import os


def test_read_fail(reader, base_dir):
    with pytest.raises(FileNotFoundError):
        reader.load(os.path.join(base_dir, "lo.fail"))
