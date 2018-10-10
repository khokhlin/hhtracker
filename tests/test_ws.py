import pytest
from hhtracker import config
config.test = True
from hhtracker.models import create_tables, drop_tables
from hhtracker.models import Vacancy
from hhtracker.ws import app


def setup_module(module):
    create_tables()


def teardown_module(module):
    drop_tables()


@pytest.fixture(scope="module")
def client():
    return app.test_client()


def test_can_get_vacancies(client):
    vacancy_params = {
        "vacancy_id": 1,
        "name": "Python Developer",
        "employer": {
            "employer_id": 1,
            "name": "Google",
        },
        "currency": "RUB",
        "salary": 100000,
    }
    Vacancy.create(**vacancy_params)
    vacancy = client.get("/api/vacancies").get_json()[0]
    assert vacancy_params["vacancy_id"] == vacancy["vacancy_id"]
    assert vacancy_params["salary"] == vacancy["salary"]
    assert vacancy_params["employer"] == vacancy["employer"]

    for i in range(2, 10):
        vacancy_params["vacancy_id"] = i
        Vacancy.create(**vacancy_params)

    page1 = client.get("/api/vacancies").get_json()
    assert len(page1) == 3
    page2 = client.get("/api/vacancies").get_json()

    # Change the first record visibility

    client.post("/api/vacancy/1", json={"visible": False})
    resp = client.get("/api/vacancies?per_page=10").get_json()
    assert len(resp) == 8
    assert len([item for item in resp if item["vacancy_id"] == 1]) == 0
