import pytest
import requests_mock
from hhtracker import config
config.test = True
from hhtracker.models import create_tables, drop_tables


@pytest.fixture(autouse=True)
def setup_database():
    create_tables()
    yield
    drop_tables()


@pytest.fixture(scope="module")
def mocker():
    with requests_mock.Mocker() as mocker:
        yield mocker
