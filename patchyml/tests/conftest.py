from pathlib import Path
import pytest
from patchyml import YamlManager, YamlReader
from ..db import StrModel, Dyct

BASE_DIR = Path(__file__).resolve().parent


@pytest.fixture
def reader() -> YamlReader:
    yield YamlReader()


@pytest.fixture
def manager() -> YamlManager:
    yield YamlManager(is_first=True)


@pytest.fixture
def base_dir() -> Path:
    return BASE_DIR


@pytest.fixture
def dyct() -> Dyct:
    yield Dyct(is_first=True)


@pytest.fixture
def strModel() -> StrModel:
    yield StrModel()
