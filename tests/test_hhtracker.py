import pytest
import requests_mock
from hhtracker import config
config.test = True
from hhtracker.hhtracker import get_vacancies
from hhtracker.models import create_tables, drop_tables


def setup_module(module):
    create_tables()


def teardown_module(module):
    drop_tables()


@pytest.fixture(scope="module")
def mocker():
    with requests_mock.Mocker() as mocker:
        yield mocker


def test_vacancies_created(mocker):
    resp = {"page": "0", "pages": 1, "items": []}
    mocker.get(requests_mock.ANY, json=resp)
    result = get_vacancies("python", 1)
    assert result == []

    resp = {
        "page": "0",
        "pages": 1,
        "items": [{
            "id": 1,
            "name": "Python developer",
            "salary": {
                "from": "100000",
                "currency": "RUR"
            },
            "employer": {
                "id": 1,
                "name": "Google"
            }
        }]
    }
    mocker.get(requests_mock.ANY, json=resp)

    result = get_vacancies("python", 1)
    result = get_vacancies("python", 1)

    result[0].pop("created_at")

    expected = [{
        'vacancy_id': 1,
        'currency': 'RUR',
        'employer': {'employer_id': 1, 'name': 'Google'},
        'name': 'Python developer',
        'salary': 100000
    }]
    assert result == expected

    resp["items"].append({
        "id": 2,
        "name": "Java Developer",
        "salary": "2000000",
        "currency": "RUR",
        "employer": {
            "id": 1,
            "name": "Google",
        }
    })

    items = get_vacancies("python", 1)
    assert len(items) == 2
    assert int(items[0]["vacancy_id"]) == 1
    assert int(items[1]["vacancy_id"]) == 2
    assert int(items[0]["employer"]["employer_id"]) == 1
    assert int(items[1]["employer"]["employer_id"]) == 1
